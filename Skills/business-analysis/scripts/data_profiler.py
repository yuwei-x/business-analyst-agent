#!/usr/bin/env python3
"""
PRISM Data Profiler — generates profile.json for large dataset analysis.

Profiles a dataset without loading it into Claude's context. Outputs a structured
profile.json that Claude reads to understand the data's shape, quality, types,
distributions, correlations, and complexity.

Usage:
    python3 data_profiler.py <file_path> [--sheet "Sheet Name"]

Supported formats: .csv, .xlsx, .xls, .tsv
"""

import argparse
import json
import os
import sys
import warnings
from datetime import datetime
from pathlib import Path

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# Dependency check
# ---------------------------------------------------------------------------

REQUIRED = {"pandas": "pandas", "numpy": "numpy", "chardet": "chardet"}
OPTIONAL = {"openpyxl": "openpyxl"}  # needed only for .xlsx

_missing = []
for mod, pkg in {**REQUIRED, **OPTIONAL}.items():
    try:
        __import__(mod)
    except ImportError:
        _missing.append(pkg)

if _missing:
    print(f"[profiler] Missing packages: {', '.join(_missing)}")
    print(f"[profiler] Install with:  pip install {' '.join(_missing)}")
    sys.exit(1)

import numpy as np
import pandas as pd
import chardet

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

LARGE_FILE_MB = 100
SAMPLE_ROWS_LIMIT = 50_000
SAMPLE_VALUES_COUNT = 5
HEAD_ROWS = 5
RANDOM_ROWS = 5

# Column-name keyword signals (Chinese + English) for semantic type detection
_TIME_KEYWORDS = {"date", "time", "month", "year", "day", "week", "quarter",
                  "日期", "时间", "月份", "年份", "日", "周", "季度",
                  "created", "updated", "timestamp", "period"}
_SUBJECT_KEYWORDS = {"customer", "user", "employee", "client", "member",
                     "person", "buyer", "seller", "vendor", "supplier",
                     "客户", "用户", "员工", "会员", "人员", "买家", "卖家"}
_OBJECT_KEYWORDS = {"product", "item", "sku", "category", "brand", "model",
                    "service", "channel", "region", "store", "shop",
                    "产品", "商品", "品类", "品牌", "型号", "门店", "渠道", "区域"}
_VALUE_KEYWORDS = {"revenue", "price", "cost", "amount", "sales", "total",
                   "profit", "income", "expense", "fee", "payment", "spend",
                   "收入", "价格", "成本", "金额", "销售额", "利润", "费用", "支出"}
_QUANTITY_KEYWORDS = {"qty", "quantity", "count", "units", "volume", "num",
                      "数量", "件数", "台数", "个数"}
_ID_KEYWORDS = {"id", "code", "number", "no", "编号", "代码", "编码", "序号"}
_STATUS_KEYWORDS = {"status", "state", "flag", "level", "type", "grade",
                    "tier", "rank", "tag", "label",
                    "状态", "等级", "级别", "类型", "标签"}
_METRIC_KEYWORDS = {"rate", "ratio", "margin", "score", "pct", "percent",
                    "proportion", "conversion", "retention", "churn",
                    "率", "比率", "比例", "得分", "评分", "转化率"}

# Hierarchical column-name patterns
_HIER_KEYWORDS = {"category", "subcategory", "sub_category", "parent",
                  "child", "group", "subgroup", "sub_group",
                  "department", "division", "section",
                  "大类", "小类", "子类", "父级", "一级", "二级", "三级"}


# ---------------------------------------------------------------------------
# File reading
# ---------------------------------------------------------------------------

def _detect_encoding(file_path: str) -> str:
    """Detect file encoding using chardet."""
    with open(file_path, "rb") as f:
        raw = f.read(min(1_000_000, os.path.getsize(file_path)))
    result = chardet.detect(raw)
    return result.get("encoding") or "utf-8"


def read_data(file_path: str, sheet_name=None) -> pd.DataFrame:
    """Read data from csv/tsv/xlsx/xls with encoding fallback."""
    ext = Path(file_path).suffix.lower()
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)

    if ext in (".xlsx", ".xls"):
        sheet = sheet_name if sheet_name else 0
        df = pd.read_excel(file_path, sheet_name=sheet, engine="openpyxl" if ext == ".xlsx" else None)
    elif ext in (".csv", ".tsv"):
        sep = "\t" if ext == ".tsv" else ","
        # Try utf-8 first, then chardet, then latin-1
        for enc in ["utf-8", None, "latin-1"]:
            try:
                if enc is None:
                    enc = _detect_encoding(file_path)
                df = pd.read_csv(file_path, sep=sep, encoding=enc, low_memory=False)
                break
            except (UnicodeDecodeError, LookupError):
                continue
        else:
            raise ValueError(f"Cannot decode file {file_path} with any encoding.")
    else:
        raise ValueError(f"Unsupported file format: {ext}. Supported: .csv, .xlsx, .xls, .tsv")

    sampled = False
    original_rows = len(df)
    if file_size_mb > LARGE_FILE_MB and len(df) > SAMPLE_ROWS_LIMIT:
        df = df.head(SAMPLE_ROWS_LIMIT)
        sampled = True

    return df, sampled, original_rows


# ---------------------------------------------------------------------------
# Semantic type detection
# ---------------------------------------------------------------------------

def _col_name_lower(name: str) -> str:
    return str(name).lower().replace(" ", "_")


def _name_matches(col_name: str, keywords: set) -> bool:
    """Check if column name contains any keyword."""
    lower = _col_name_lower(col_name)
    return any(kw in lower for kw in keywords)


def _try_parse_datetime(series: pd.Series) -> pd.Series:
    """Attempt to parse a series as datetime. Returns the parsed series or None."""
    try:
        return pd.to_datetime(series, format="mixed", errors="coerce", dayfirst=False)
    except (TypeError, ValueError):
        pass
    # Fallback for older pandas without format="mixed"
    try:
        return pd.to_datetime(series, infer_datetime_format=True, errors="coerce")
    except (TypeError, ValueError):
        pass
    try:
        return pd.to_datetime(series, errors="coerce")
    except Exception:
        return None


def _is_datetime_parseable(series: pd.Series) -> bool:
    """Try to parse a sample as datetime. Only checks string/object columns."""
    if pd.api.types.is_datetime64_any_dtype(series):
        return True
    # Do NOT attempt datetime parsing on numeric columns — pd.to_datetime
    # happily converts numbers to timestamps (epoch), causing false positives.
    if pd.api.types.is_numeric_dtype(series):
        return False
    if series.dtype == object or pd.api.types.is_string_dtype(series):
        sample = series.dropna().head(50)
        if sample.empty:
            return False
        parsed = _try_parse_datetime(sample)
        if parsed is None:
            return False
        return parsed.notna().mean() > 0.8
    return False


def detect_semantic_type(col_name: str, series: pd.Series) -> str:
    """Classify a column into one of 8 semantic types."""
    n = len(series)
    nunique = series.nunique()
    unique_pct = (nunique / n * 100) if n > 0 else 0
    is_numeric = pd.api.types.is_numeric_dtype(series)

    # 1. Time — name match OR successful datetime parse (strings only)
    if _name_matches(col_name, _TIME_KEYWORDS):
        return "Time"
    if _is_datetime_parseable(series):
        return "Time"

    # 2. Identifier — >80% unique
    if _name_matches(col_name, _ID_KEYWORDS) and unique_pct > 80:
        return "Identifier"

    # 3. Metric — check BEFORE Value so "利润率" (profit margin) is Metric, not Value
    if is_numeric and _name_matches(col_name, _METRIC_KEYWORDS):
        return "Metric"

    # 4. Value — numeric + value keywords
    if is_numeric and _name_matches(col_name, _VALUE_KEYWORDS):
        return "Value"

    # 5. Quantity — integer-dominant + quantity keywords
    if is_numeric and _name_matches(col_name, _QUANTITY_KEYWORDS):
        return "Quantity"

    # 6. Status — low cardinality (<10% unique)
    if _name_matches(col_name, _STATUS_KEYWORDS) and unique_pct < 10:
        return "Status"

    # 7. Object — medium cardinality (<50% unique)
    if _name_matches(col_name, _OBJECT_KEYWORDS) and unique_pct < 50:
        return "Object"

    # 8. Subject — high cardinality text (10-80% unique)
    if _name_matches(col_name, _SUBJECT_KEYWORDS) and 10 <= unique_pct <= 80:
        return "Subject"

    # Fallbacks
    if is_numeric:
        # Numeric 0-1 or 0-100 with no keyword match
        vmin, vmax = series.min(), series.max()
        if pd.notna(vmin) and pd.notna(vmax):
            if (0 <= vmin and vmax <= 1) or (0 <= vmin and vmax <= 100 and nunique < 100):
                return "Metric"
        return "Value"

    # Text fallbacks
    if unique_pct > 80:
        return "Identifier"
    if unique_pct < 10:
        return "Status"
    if 10 <= unique_pct <= 80:
        return "Subject"

    return "Status"


# ---------------------------------------------------------------------------
# Column profiling
# ---------------------------------------------------------------------------

def _safe_val(v):
    """Convert numpy/pandas types to JSON-safe Python types."""
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        if np.isnan(v) or np.isinf(v):
            return None
        return round(float(v), 4)
    if isinstance(v, (np.bool_,)):
        return bool(v)
    if isinstance(v, pd.Timestamp):
        return v.isoformat()
    if isinstance(v, (np.datetime64,)):
        ts = pd.Timestamp(v)
        return ts.isoformat() if not pd.isna(ts) else None
    if isinstance(v, (np.ndarray,)):
        return v.tolist()
    if pd.isna(v):
        return None
    return v


def profile_column(col_name: str, series: pd.Series) -> dict:
    """Generate a profile dict for one column."""
    n = len(series)
    null_count = int(series.isna().sum())
    null_pct = round(null_count / n * 100, 2) if n > 0 else 0
    nunique = int(series.nunique())
    unique_pct = round(nunique / n * 100, 2) if n > 0 else 0

    sem_type = detect_semantic_type(col_name, series)

    # Try to convert Time columns to datetime
    working_series = series
    if sem_type == "Time" and not pd.api.types.is_datetime64_any_dtype(series):
        parsed = _try_parse_datetime(series)
        if parsed is not None and parsed.notna().mean() > 0.5:
            working_series = parsed

    dtype_str = str(working_series.dtype)

    # Stats
    stats = {}
    non_null = working_series.dropna()

    if pd.api.types.is_datetime64_any_dtype(working_series) and not non_null.empty:
        stats["min"] = str(non_null.min().date()) if hasattr(non_null.min(), "date") else str(non_null.min())
        stats["max"] = str(non_null.max().date()) if hasattr(non_null.max(), "date") else str(non_null.max())
        try:
            stats["range"] = str(non_null.max() - non_null.min())
        except Exception:
            pass
    elif pd.api.types.is_numeric_dtype(working_series) and not non_null.empty:
        stats["mean"] = _safe_val(non_null.mean())
        stats["median"] = _safe_val(non_null.median())
        stats["std"] = _safe_val(non_null.std())
        stats["min"] = _safe_val(non_null.min())
        stats["max"] = _safe_val(non_null.max())
        stats["p25"] = _safe_val(non_null.quantile(0.25))
        stats["p75"] = _safe_val(non_null.quantile(0.75))
        try:
            stats["skewness"] = _safe_val(non_null.skew())
        except Exception:
            pass
        try:
            stats["kurtosis"] = _safe_val(non_null.kurtosis())
        except Exception:
            pass
    elif not non_null.empty:
        # Categorical / text
        vc = non_null.value_counts()
        stats["most_common"] = _safe_val(vc.index[0]) if len(vc) > 0 else None
        stats["most_common_count"] = _safe_val(vc.iloc[0]) if len(vc) > 0 else None
        stats["least_common"] = _safe_val(vc.index[-1]) if len(vc) > 0 else None
        stats["least_common_count"] = _safe_val(vc.iloc[-1]) if len(vc) > 0 else None
        if len(vc) <= 20:
            stats["value_counts"] = {str(k): int(v) for k, v in vc.items()}

    # Sample values
    sample = non_null.sample(min(SAMPLE_VALUES_COUNT, len(non_null)), random_state=42) if len(non_null) > 0 else pd.Series(dtype=object)
    sample_values = [_safe_val(v) for v in sample.tolist()]

    return {
        "name": str(col_name),
        "dtype": dtype_str,
        "semantic_type": sem_type,
        "null_count": null_count,
        "null_pct": null_pct,
        "unique_count": nunique,
        "unique_pct": unique_pct,
        "stats": stats,
        "sample_values": sample_values,
    }


# ---------------------------------------------------------------------------
# Quality scoring
# ---------------------------------------------------------------------------

def assess_quality(df: pd.DataFrame, column_profiles: list) -> dict:
    """Compute data quality score and list issues."""
    issues = []
    n = len(df)

    # Duplicate rows
    dup_count = int(df.duplicated().sum())
    if dup_count > 0:
        severity = "high" if dup_count / n > 0.05 else "medium"
        issues.append({
            "severity": severity,
            "description": f"{dup_count} duplicate rows detected ({round(dup_count / n * 100, 1)}%)"
        })

    # Null analysis per column
    total_nulls = 0
    total_cells = n * len(df.columns)
    for cp in column_profiles:
        total_nulls += cp["null_count"]
        if cp["null_pct"] > 0:
            if cp["null_pct"] >= 30:
                severity = "high"
            elif cp["null_pct"] >= 10:
                severity = "high"
            elif cp["null_pct"] >= 5:
                severity = "medium"
            else:
                severity = "low"
            issues.append({
                "severity": severity,
                "description": f"Column '{cp['name']}' has {cp['null_pct']}% null values ({cp['null_count']} rows)"
            })

    # Outlier detection for numeric columns (beyond 3 sigma)
    for cp in column_profiles:
        if cp["semantic_type"] in ("Value", "Quantity", "Metric") and "mean" in cp["stats"] and "std" in cp["stats"]:
            col = df[cp["name"]]
            mean = cp["stats"]["mean"]
            std = cp["stats"]["std"]
            if std and std > 0 and mean is not None:
                outlier_count = int(((col - mean).abs() > 3 * std).sum())
                if outlier_count > 0:
                    issues.append({
                        "severity": "low" if outlier_count < 10 else "medium",
                        "description": f"Column '{cp['name']}' has {outlier_count} outliers beyond 3 sigma"
                    })

    # Constant columns
    for cp in column_profiles:
        if cp["unique_count"] == 1:
            issues.append({
                "severity": "low",
                "description": f"Column '{cp['name']}' has only 1 unique value (constant)"
            })

    # High cardinality text that might be free text / noise
    for cp in column_profiles:
        if cp["semantic_type"] == "Identifier" and cp["unique_pct"] > 95:
            issues.append({
                "severity": "low",
                "description": f"Column '{cp['name']}' is near-unique ({cp['unique_pct']}% unique) — likely an identifier, not useful for aggregation"
            })

    total_null_pct = round(total_nulls / total_cells * 100, 2) if total_cells > 0 else 0

    # Score: start at 100, deduct
    score = 100
    score -= min(30, dup_count / max(n, 1) * 200)  # Up to -30 for duplicates
    score -= min(40, total_null_pct * 4)  # Up to -40 for nulls
    high_issues = sum(1 for i in issues if i["severity"] == "high")
    medium_issues = sum(1 for i in issues if i["severity"] == "medium")
    score -= high_issues * 5
    score -= medium_issues * 2
    score = max(0, min(100, round(score)))

    return {
        "score": score,
        "issues": sorted(issues, key=lambda x: {"high": 0, "medium": 1, "low": 2}[x["severity"]]),
        "duplicate_rows": dup_count,
        "total_null_pct": total_null_pct,
    }


# ---------------------------------------------------------------------------
# Correlations
# ---------------------------------------------------------------------------

def compute_correlations(df: pd.DataFrame, column_profiles: list) -> list:
    """Compute Pearson correlations between numeric columns."""
    numeric_cols = [cp["name"] for cp in column_profiles
                    if cp["semantic_type"] in ("Value", "Quantity", "Metric")
                    and cp["unique_count"] > 1]

    if len(numeric_cols) < 2:
        return []

    # Limit to avoid extremely large correlation matrices
    numeric_cols = numeric_cols[:30]

    sub = df[numeric_cols].apply(pd.to_numeric, errors="coerce")
    corr_matrix = sub.corr(method="pearson")

    results = []
    seen = set()
    for i, col_a in enumerate(numeric_cols):
        for j, col_b in enumerate(numeric_cols):
            if i >= j:
                continue
            pair = (col_a, col_b)
            if pair in seen:
                continue
            seen.add(pair)
            r = corr_matrix.loc[col_a, col_b]
            if pd.isna(r):
                continue
            abs_r = abs(r)
            if abs_r < 0.3:
                continue  # Skip weak correlations
            # Estimate significance (rough heuristic based on sample size)
            n = sub[[col_a, col_b]].dropna().shape[0]
            if n < 3:
                continue
            t_stat = r * np.sqrt((n - 2) / (1 - r**2 + 1e-10))
            if abs(t_stat) > 3.29:
                sig = "p<0.001"
            elif abs(t_stat) > 2.576:
                sig = "p<0.01"
            elif abs(t_stat) > 1.96:
                sig = "p<0.05"
            else:
                sig = f"p~{round(2 * (1 - 0.5 * (1 + abs(t_stat) / np.sqrt(n))), 3)}"

            results.append({
                "col_a": col_a,
                "col_b": col_b,
                "pearson": round(float(r), 4),
                "significance": sig,
            })

    # Sort by absolute correlation strength, return top 15
    results.sort(key=lambda x: abs(x["pearson"]), reverse=True)
    return results[:15]


# ---------------------------------------------------------------------------
# Sample rows
# ---------------------------------------------------------------------------

def _row_to_safe_dict(row: pd.Series) -> dict:
    """Convert a DataFrame row to a JSON-safe dict."""
    return {str(k): _safe_val(v) for k, v in row.items()}


def extract_sample_rows(df: pd.DataFrame, column_profiles: list) -> dict:
    """Extract head, random, and extreme rows."""
    head = [_row_to_safe_dict(df.iloc[i]) for i in range(min(HEAD_ROWS, len(df)))]

    random_indices = df.sample(min(RANDOM_ROWS, len(df)), random_state=42).index
    random_rows = [_row_to_safe_dict(df.loc[i]) for i in random_indices]

    # Extreme rows: find primary value column and get min/max rows
    extremes = []
    value_cols = [cp["name"] for cp in column_profiles if cp["semantic_type"] == "Value"]
    if value_cols:
        primary = value_cols[0]
        numeric_col = pd.to_numeric(df[primary], errors="coerce")
        if numeric_col.notna().any():
            min_idx = numeric_col.idxmin()
            max_idx = numeric_col.idxmax()
            if pd.notna(min_idx):
                extremes.append(_row_to_safe_dict(df.loc[min_idx]))
            if pd.notna(max_idx) and max_idx != min_idx:
                extremes.append(_row_to_safe_dict(df.loc[max_idx]))

    return {
        "head": head,
        "random": random_rows,
        "extremes": extremes,
    }


# ---------------------------------------------------------------------------
# Complexity scoring
# ---------------------------------------------------------------------------

def compute_complexity(df: pd.DataFrame, column_profiles: list) -> dict:
    """Score dataset complexity from 0-6."""
    n_rows = len(df)
    n_cols = len(df.columns)

    has_time = any(cp["semantic_type"] == "Time" for cp in column_profiles)
    subject_count = sum(1 for cp in column_profiles if cp["semantic_type"] == "Subject")
    value_count = sum(1 for cp in column_profiles if cp["semantic_type"] == "Value")

    # Hierarchical detection via column names
    has_hierarchical = False
    col_names_lower = [_col_name_lower(c) for c in df.columns]
    for kw in _HIER_KEYWORDS:
        if any(kw in cn for cn in col_names_lower):
            has_hierarchical = True
            break
    # Also check if any pair looks like parent/child (e.g., category + subcategory)
    if not has_hierarchical:
        for i, cn_a in enumerate(col_names_lower):
            for cn_b in col_names_lower[i + 1:]:
                if cn_b.startswith(cn_a) and cn_b != cn_a:
                    has_hierarchical = True
                    break

    factors = {
        "large_dataset": n_rows > 500,
        "many_columns": n_cols > 10,
        "has_time": has_time,
        "multiple_subjects": subject_count > 1,
        "multiple_values": value_count > 2,
        "hierarchical": has_hierarchical,
    }

    score = sum(1 for v in factors.values() if v)

    if score <= 2:
        depth = "standard"
    elif score <= 4:
        depth = "deep"
    else:
        depth = "comprehensive"

    return {
        "score": score,
        "factors": factors,
        "recommended_depth": depth,
    }


# ---------------------------------------------------------------------------
# Main profiling pipeline
# ---------------------------------------------------------------------------

def profile_dataset(file_path: str, sheet_name=None) -> dict:
    """Run the full profiling pipeline and return the profile dict."""
    file_path = os.path.abspath(file_path)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    file_size_mb = round(os.path.getsize(file_path) / (1024 * 1024), 2)

    print(f"[profiler] Reading {Path(file_path).name} ({file_size_mb} MB)...")
    df, sampled, original_rows = read_data(file_path, sheet_name)

    if sampled:
        print(f"[profiler] Large file detected. Sampled first {SAMPLE_ROWS_LIMIT:,} of {original_rows:,} rows.")

    print(f"[profiler] Shape: {len(df):,} rows x {len(df.columns)} columns")
    print(f"[profiler] Profiling columns...")

    # Column profiles
    column_profiles = []
    for col in df.columns:
        cp = profile_column(col, df[col])
        column_profiles.append(cp)

    # Type summary for stdout
    type_counts = {}
    for cp in column_profiles:
        t = cp["semantic_type"]
        type_counts[t] = type_counts.get(t, 0) + 1

    print(f"[profiler] Semantic types: {type_counts}")

    # Quality
    print(f"[profiler] Assessing data quality...")
    quality = assess_quality(df, column_profiles)
    print(f"[profiler] Quality score: {quality['score']}/100 ({len(quality['issues'])} issues)")

    # Correlations
    print(f"[profiler] Computing correlations...")
    correlations = compute_correlations(df, column_profiles)
    print(f"[profiler] Found {len(correlations)} significant correlations (|r| >= 0.3)")

    # Sample rows
    sample_rows = extract_sample_rows(df, column_profiles)

    # Complexity
    complexity = compute_complexity(df, column_profiles)
    print(f"[profiler] Complexity: {complexity['score']}/6 -> {complexity['recommended_depth']} analysis")

    # Memory usage
    memory_mb = round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2)

    # Build meta
    meta = {
        "file_name": Path(file_path).name,
        "file_path": file_path,
        "file_size_mb": file_size_mb,
        "row_count": original_rows,
        "column_count": len(df.columns),
        "memory_mb": memory_mb,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
    }
    if sampled:
        meta["sampled"] = True
        meta["sampled_rows"] = len(df)
        meta["note"] = f"File > {LARGE_FILE_MB}MB. Profiled first {SAMPLE_ROWS_LIMIT:,} of {original_rows:,} rows."

    profile = {
        "meta": meta,
        "columns": column_profiles,
        "quality": quality,
        "correlations": correlations,
        "sample_rows": sample_rows,
        "complexity": complexity,
    }

    return profile


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="PRISM Data Profiler — profile a dataset and output profile.json"
    )
    parser.add_argument("file_path", help="Path to the data file (.csv, .xlsx, .xls, .tsv)")
    parser.add_argument("--sheet", default=None, help="Sheet name for .xlsx files (default: first sheet)")
    parser.add_argument("--output", "-o", default=None,
                        help="Output path for profile.json (default: same directory as input file)")

    args = parser.parse_args()

    try:
        profile = profile_dataset(args.file_path, sheet_name=args.sheet)
    except Exception as e:
        print(f"[profiler] ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    # Determine output path
    if args.output:
        output_path = os.path.abspath(args.output)
    else:
        output_path = os.path.join(os.path.dirname(os.path.abspath(args.file_path)), "profile.json")

    # Write profile.json
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2, default=str)

    print()
    print(f"{'=' * 60}")
    print(f"  PRISM Data Profile — {profile['meta']['file_name']}")
    print(f"{'=' * 60}")
    print(f"  Rows:        {profile['meta']['row_count']:,}")
    print(f"  Columns:     {profile['meta']['column_count']}")
    print(f"  File size:   {profile['meta']['file_size_mb']} MB")
    print(f"  Memory:      {profile['meta']['memory_mb']} MB")
    print(f"  Quality:     {profile['quality']['score']}/100")
    print(f"  Complexity:  {profile['complexity']['score']}/6 ({profile['complexity']['recommended_depth']})")
    print(f"  Duplicates:  {profile['quality']['duplicate_rows']}")
    print(f"  Null %:      {profile['quality']['total_null_pct']}%")
    print()

    # Column summary table
    print(f"  {'Column':<30} {'Type':<12} {'Semantic':<12} {'Nulls':<10} {'Unique':<10}")
    print(f"  {'-' * 30} {'-' * 12} {'-' * 12} {'-' * 10} {'-' * 10}")
    for cp in profile["columns"]:
        name = cp["name"][:29]
        dtype = cp["dtype"][:11]
        sem = cp["semantic_type"][:11]
        nulls = f"{cp['null_pct']}%"
        uniq = f"{cp['unique_count']}"
        print(f"  {name:<30} {dtype:<12} {sem:<12} {nulls:<10} {uniq:<10}")

    if profile["quality"]["issues"]:
        print()
        print(f"  Quality Issues:")
        for issue in profile["quality"]["issues"][:10]:
            icon = {"high": "!!!", "medium": " !!", "low": "  !"}[issue["severity"]]
            print(f"    {icon} [{issue['severity'].upper()}] {issue['description']}")

    if profile["correlations"]:
        print()
        print(f"  Top Correlations:")
        for corr in profile["correlations"][:5]:
            direction = "+" if corr["pearson"] > 0 else "-"
            print(f"    {corr['col_a']} <-> {corr['col_b']}: r={corr['pearson']:+.3f} ({corr['significance']})")

    print()
    print(f"  Output: {output_path}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
