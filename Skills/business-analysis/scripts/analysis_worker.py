#!/usr/bin/env python3
"""
analysis_worker.py — Local pandas execution engine for PRISM Investigate stage.

Executes Claude-generated pandas analysis code against a data file locally,
returning only aggregated JSON results. This keeps raw data out of Claude's
context window: Claude generates the analysis code, this script runs it,
and Claude only ever sees the summary.

Usage:
    # Run inline code string
    python3 analysis_worker.py sales.csv --code "result = {'rows': len(df)}" --output out.json

    # Run code from a file
    python3 analysis_worker.py sales.csv --code-file analysis_code.py --output findings.json

    # Quick info check (shape + columns)
    python3 analysis_worker.py sales.csv --info

Dependencies: pandas, numpy, openpyxl, chardet
"""

import argparse
import json
import math
import os
import re
import signal
import sys
import traceback
from collections import OrderedDict
from datetime import datetime, timedelta
from pathlib import Path

# ---------------------------------------------------------------------------
# Dependency checks
# ---------------------------------------------------------------------------

_MISSING_DEPS: list[str] = []

try:
    import pandas as pd
except ImportError:
    _MISSING_DEPS.append("pandas")

try:
    import numpy as np
except ImportError:
    _MISSING_DEPS.append("numpy")

try:
    import chardet
except ImportError:
    _MISSING_DEPS.append("chardet")

# openpyxl is only needed for xlsx; we check lazily when loading xlsx files.

if _MISSING_DEPS:
    print(
        f"[analysis_worker] ERROR: Missing dependencies: {', '.join(_MISSING_DEPS)}\n"
        f"Install with: pip install {' '.join(_MISSING_DEPS)}",
        file=sys.stderr,
    )
    sys.exit(1)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TIMEOUT_SECONDS = 120
LARGE_FILE_THRESHOLD_MB = 100

# Modules allowed inside the analysis sandbox
ALLOWED_MODULES = {
    "pandas": pd,
    "pd": pd,
    "numpy": np,
    "np": np,
    "math": math,
    "re": re,
    "datetime": __import__("datetime"),
    "timedelta": timedelta,
    "collections": __import__("collections"),
    "OrderedDict": OrderedDict,
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _detect_encoding(file_path: str) -> str:
    """Detect file encoding: try utf-8 first, then chardet, fallback latin-1."""
    # Fast path — try utf-8
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            f.read(8192)
        return "utf-8"
    except (UnicodeDecodeError, UnicodeError):
        pass

    # chardet detection
    try:
        with open(file_path, "rb") as f:
            raw = f.read(65536)
        detection = chardet.detect(raw)
        encoding = detection.get("encoding")
        if encoding:
            # Validate by attempting a read
            with open(file_path, "r", encoding=encoding) as f:
                f.read(8192)
            return encoding
    except Exception:
        pass

    # Fallback
    return "latin-1"


def _load_dataframe(file_path: str, sheet: str | None = None) -> pd.DataFrame:
    """Load a data file into a pandas DataFrame."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Data file not found: {file_path}")

    suffix = path.suffix.lower()
    file_size_mb = path.stat().st_size / (1024 * 1024)

    if file_size_mb > LARGE_FILE_THRESHOLD_MB:
        print(
            f"[analysis_worker] WARNING: File is {file_size_mb:.1f} MB "
            f"(>{LARGE_FILE_THRESHOLD_MB} MB). Proceeding — analysis code should "
            f"handle sampling if needed.",
            file=sys.stderr,
        )

    if suffix in (".xlsx", ".xls"):
        try:
            import openpyxl  # noqa: F401
        except ImportError:
            print(
                "[analysis_worker] ERROR: openpyxl is required for Excel files.\n"
                "Install with: pip install openpyxl",
                file=sys.stderr,
            )
            sys.exit(1)

        kwargs: dict = {}
        if sheet is not None:
            kwargs["sheet_name"] = sheet
        return pd.read_excel(file_path, **kwargs)

    elif suffix == ".tsv":
        encoding = _detect_encoding(file_path)
        return pd.read_csv(file_path, sep="\t", encoding=encoding)

    elif suffix == ".csv":
        encoding = _detect_encoding(file_path)
        return pd.read_csv(file_path, encoding=encoding)

    else:
        # Best-effort: try CSV with auto-detection
        encoding = _detect_encoding(file_path)
        return pd.read_csv(file_path, encoding=encoding, sep=None, engine="python")


def _build_sandbox_namespace(df: pd.DataFrame) -> dict:
    """Build the restricted namespace for code execution."""
    namespace = {
        "__builtins__": _safe_builtins(),
        "df": df,
        "pd": pd,
        "pandas": pd,
        "np": np,
        "numpy": np,
        "math": math,
        "re": re,
        "datetime": __import__("datetime"),
        "timedelta": timedelta,
        "collections": __import__("collections"),
        "OrderedDict": OrderedDict,
    }
    return namespace


def _safe_builtins() -> dict:
    """Return a restricted __builtins__ dict — no file I/O, no imports of
    dangerous modules, no exec/eval escape hatches beyond what we control."""
    import builtins as _b

    # Allowlist of safe built-in functions
    ALLOWED_BUILTINS = [
        "abs", "all", "any", "bool", "bytes", "callable", "chr", "complex",
        "dict", "dir", "divmod", "enumerate", "filter", "float", "format",
        "frozenset", "getattr", "hasattr", "hash", "hex", "id", "int",
        "isinstance", "issubclass", "iter", "len", "list", "map", "max",
        "min", "next", "object", "oct", "ord", "pow", "print", "property",
        "range", "repr", "reversed", "round", "set", "slice", "sorted",
        "str", "sum", "tuple", "type", "vars", "zip",
        # Needed for pandas operations
        "ValueError", "KeyError", "TypeError", "IndexError", "AttributeError",
        "RuntimeError", "StopIteration", "Exception", "ZeroDivisionError",
        "NotImplementedError", "OverflowError",
        "True", "False", "None",
    ]

    safe = {}
    for name in ALLOWED_BUILTINS:
        obj = getattr(_b, name, None)
        if obj is not None:
            safe[name] = obj

    # Restricted __import__ — only allow safe modules
    IMPORTABLE = {
        "pandas", "numpy", "math", "re", "datetime", "collections",
        "statistics", "itertools", "functools", "operator", "decimal",
        "fractions", "string",
    }

    def _restricted_import(name, *args, **kwargs):
        top_level = name.split(".")[0]
        if top_level not in IMPORTABLE:
            raise ImportError(
                f"Import of '{name}' is not allowed. "
                f"Available modules: {', '.join(sorted(IMPORTABLE))}"
            )
        return __import__(name, *args, **kwargs)

    safe["__import__"] = _restricted_import

    return safe


class _JsonEncoder(json.JSONEncoder):
    """Handle pandas/numpy types that standard json cannot serialize."""

    def default(self, obj):
        # numpy scalar types
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            if np.isnan(obj) or np.isinf(obj):
                return None
            return float(obj)
        if isinstance(obj, (np.bool_,)):
            return bool(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()

        # pandas types
        if isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        if isinstance(obj, pd.Period):
            return str(obj)
        if isinstance(obj, pd.Timedelta):
            return str(obj)
        if isinstance(obj, (pd.Categorical,)):
            return obj.tolist()
        if isinstance(obj, pd.Series):
            return obj.tolist()
        if isinstance(obj, pd.DataFrame):
            return obj.to_dict("records")
        if hasattr(obj, "item"):
            return obj.item()

        # datetime types
        if isinstance(obj, (datetime,)):
            return obj.isoformat()
        if isinstance(obj, (timedelta,)):
            return str(obj)

        # NaN / NaT / None
        if obj is pd.NaT:
            return None

        # Fallback: try string conversion
        try:
            return str(obj)
        except Exception:
            return repr(obj)


def _sanitize_for_json(obj):
    """Recursively replace NaN/Inf float values with None for valid JSON output.

    Python's json encoder handles float('nan') and float('inf') as special
    cases that bypass JSONEncoder.default(), producing invalid JSON tokens
    like NaN and Infinity. This function walks the data structure and
    converts them to None before serialization.
    """
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    if isinstance(obj, dict):
        return {k: _sanitize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_sanitize_for_json(item) for item in obj]
    return obj


def _serialize_result(result: object) -> str:
    """Serialize the result object to a JSON string."""
    sanitized = _sanitize_for_json(result)
    return json.dumps(sanitized, cls=_JsonEncoder, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Timeout handler
# ---------------------------------------------------------------------------

class TimeoutError(Exception):
    pass


def _timeout_handler(signum, frame):
    raise TimeoutError(
        f"Analysis code execution exceeded {TIMEOUT_SECONDS} second timeout."
    )


# ---------------------------------------------------------------------------
# Core execution
# ---------------------------------------------------------------------------

def run_info(file_path: str, sheet: str | None = None) -> None:
    """Print DataFrame shape and column info, then exit."""
    df = _load_dataframe(file_path, sheet=sheet)
    info = {
        "file": os.path.basename(file_path),
        "shape": {"rows": df.shape[0], "columns": df.shape[1]},
        "columns": [],
    }
    for col in df.columns:
        info["columns"].append({
            "name": str(col),
            "dtype": str(df[col].dtype),
            "non_null": int(df[col].count()),
            "null_pct": round(df[col].isna().mean() * 100, 1),
        })

    print(json.dumps(info, ensure_ascii=False, indent=2))


def run_analysis(
    file_path: str,
    code: str,
    output_path: str,
    sheet: str | None = None,
) -> None:
    """Execute analysis code against the data file and write results to JSON."""

    # --- Load data ---
    print(f"[analysis_worker] Loading data from: {os.path.basename(file_path)}")
    try:
        df = _load_dataframe(file_path, sheet=sheet)
    except Exception as exc:
        _write_error_json(output_path, "data_load_error", str(exc))
        return

    print(
        f"[analysis_worker] DataFrame loaded: {df.shape[0]} rows x {df.shape[1]} columns"
    )

    # --- Build sandbox ---
    namespace = _build_sandbox_namespace(df)

    # --- Execute with timeout ---
    print(f"[analysis_worker] Executing analysis code ({len(code)} chars) ...")

    # Set timeout (SIGALRM is Unix-only; on Windows we skip the alarm)
    has_alarm = hasattr(signal, "SIGALRM")
    if has_alarm:
        old_handler = signal.signal(signal.SIGALRM, _timeout_handler)
        signal.alarm(TIMEOUT_SECONDS)

    try:
        exec(compile(code, "<analysis_code>", "exec"), namespace)
    except TimeoutError as exc:
        if has_alarm:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)
        _write_error_json(output_path, "timeout_error", str(exc))
        return
    except SyntaxError as exc:
        if has_alarm:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)
        _write_error_json(
            output_path,
            "syntax_error",
            traceback.format_exc(),
        )
        return
    except Exception as exc:
        if has_alarm:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)
        # Include first 5 rows for debugging context
        sample_rows = df.head(5).to_dict("records")
        _write_error_json(
            output_path,
            "runtime_error",
            traceback.format_exc(),
            debug_context={
                "df_shape": list(df.shape),
                "df_columns": list(df.columns),
                "df_dtypes": {str(k): str(v) for k, v in df.dtypes.items()},
                "first_5_rows": sample_rows,
            },
        )
        return
    finally:
        if has_alarm:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)

    # --- Extract result ---
    if "result" not in namespace:
        _write_error_json(
            output_path,
            "missing_result",
            "Analysis code did not define a 'result' variable. "
            "The code must assign its output to a variable named 'result'.",
        )
        return

    result = namespace["result"]

    # --- Serialize and write ---
    try:
        json_str = _serialize_result(result)
    except Exception as exc:
        _write_error_json(
            output_path,
            "serialization_error",
            f"Could not serialize result to JSON: {exc}\n"
            f"Result type: {type(result).__name__}",
        )
        return

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(json_str)

    # Brief summary
    result_size = len(json_str)
    if isinstance(result, dict):
        keys = list(result.keys())
        print(f"[analysis_worker] Result keys: {keys}")
    print(
        f"[analysis_worker] Output written to: {output_path} "
        f"({result_size:,} bytes)"
    )


def _write_error_json(
    output_path: str,
    error_type: str,
    message: str,
    debug_context: dict | None = None,
) -> None:
    """Write a structured error JSON to the output path."""
    error_obj: dict = {
        "error": True,
        "error_type": error_type,
        "message": message,
    }
    if debug_context is not None:
        error_obj["debug_context"] = debug_context

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(error_obj, f, cls=_JsonEncoder, ensure_ascii=False, indent=2)

    print(
        f"[analysis_worker] ERROR ({error_type}): see {output_path}",
        file=sys.stderr,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description=(
            "PRISM analysis worker — executes pandas analysis code locally "
            "against a data file and outputs aggregated results as JSON."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python3 analysis_worker.py sales.csv --info\n"
            '  python3 analysis_worker.py sales.csv --code "result = {\'rows\': len(df)}" --output out.json\n'
            "  python3 analysis_worker.py sales.csv --code-file analysis.py --output findings.json\n"
            "  python3 analysis_worker.py data.xlsx --sheet Sheet2 --code-file code.py --output out.json"
        ),
    )

    parser.add_argument(
        "data_file",
        help="Path to the data file (csv, xlsx, tsv)",
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Print DataFrame shape and column names, then exit",
    )
    parser.add_argument(
        "--code",
        type=str,
        default=None,
        help="Python code string to execute (must define 'result' variable)",
    )
    parser.add_argument(
        "--code-file",
        type=str,
        default=None,
        help="Path to a .py file containing analysis code",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output JSON file path",
    )
    parser.add_argument(
        "--sheet",
        type=str,
        default=None,
        help="Sheet name for xlsx files (default: first sheet)",
    )

    args = parser.parse_args()

    # --- Info mode ---
    if args.info:
        try:
            run_info(args.data_file, sheet=args.sheet)
        except Exception as exc:
            print(f"[analysis_worker] ERROR: {exc}", file=sys.stderr)
            sys.exit(1)
        return

    # --- Analysis mode: validate arguments ---
    if args.code is None and args.code_file is None:
        parser.error("Either --code or --code-file is required (unless using --info)")

    if args.code is not None and args.code_file is not None:
        parser.error("Specify either --code or --code-file, not both")

    if args.output is None:
        parser.error("--output is required for analysis mode")

    # Resolve code
    if args.code_file is not None:
        code_path = Path(args.code_file)
        if not code_path.exists():
            print(
                f"[analysis_worker] ERROR: Code file not found: {args.code_file}",
                file=sys.stderr,
            )
            sys.exit(1)
        code = code_path.read_text(encoding="utf-8")
    else:
        code = args.code

    # Run
    run_analysis(
        file_path=args.data_file,
        code=code,
        output_path=args.output,
        sheet=args.sheet,
    )


if __name__ == "__main__":
    main()
