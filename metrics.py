"""
Metrics and RIS parsing engine for ASReview reviewer analytics.
Uses Pandas for aggregating reviewer counts and today's activity.
"""

from datetime import datetime, date
import re
import pandas as pd


def parse_asreview_ris(ris_text: str) -> list[dict]:
    """
    Parses RIS formatted text exported by ASReview LAB into a list of record dicts.
    Extracts bibliographic tags and custom ASReview N1 tags.
    """
    records = []
    current = {}
    current_authors = []
    current_tag = None

    for line in ris_text.splitlines():
        line = line.rstrip("\r\n")
        if not line:
            continue

        # Match standard RIS tag: e.g. "TI  - ..."
        match = re.match(r"^([A-Z0-9]{2})\s+-(?:\s+(.*))?$", line)
        if match:
            tag, val = match.group(1), match.group(2) or ""
            current_tag = tag

            if tag == "TY":
                current = {"type": val}
                current_authors = []
            elif tag == "ER":
                current["authors"] = current_authors
                records.append(current)
                current = {}
                current_authors = []
            elif tag == "AU":
                current_authors.append(val)
            elif tag == "N1":
                # Handle ASReview specific annotations
                if val == "ASReview_relevant":
                    current["label"] = 1
                elif val == "ASReview_irrelevant":
                    current["label"] = 0
                elif ":" in val:
                    key, v = val.split(":", 1)
                    clean_key = key.strip()
                    clean_val = v.strip().strip("'\"")
                    current[clean_key] = clean_val
                else:
                    current.setdefault("notes", []).append(val)
            elif tag == "TI":
                current["title"] = val
            elif tag == "AB":
                current["abstract"] = val
            elif tag == "PY":
                current["year"] = val
            elif tag == "DO":
                current["doi"] = val
            elif tag == "ID":
                current["id"] = val
        else:
            # Continuation of previous multi-line tag
            if current_tag == "AB" and "abstract" in current:
                current["abstract"] += " " + line.strip()
            elif current_tag == "TI" and "title" in current:
                current["title"] += " " + line.strip()

    return records


def compute_reviewer_metrics(records: list[dict], target_date: date = None) -> dict:
    """
    Calculates total and today's reviewer metrics using Pandas.

    Args:
        records: List of parsed record dictionaries from RIS.
        target_date: Date to filter for "Today" metrics (defaults to today's local date).

    Returns:
        Dictionary containing:
        - summary: High-level dashboard counters
        - total_breakdown: List of per-reviewer total stats (Total, Relevant, Irrelevant)
        - today_breakdown: List of per-reviewer today's stats
        - target_date_str: Formatted string of target date
    """
    if target_date is None:
        target_date = date.today()
    target_date_str = target_date.strftime("%Y-%m-%d")

    if not records:
        return {
            "summary": {
                "total_screened": 0,
                "total_today": 0,
                "total_relevant": 0,
                "total_irrelevant": 0,
                "overall_inclusion_rate": 0.0,
                "reviewers_count": 0,
                "today_reviewers_count": 0
            },
            "total_breakdown": [],
            "today_breakdown": [],
            "target_date_str": target_date_str
        }

    df = pd.DataFrame(records)

    # Clean and standardize columns
    if "asreview_user_name" not in df.columns:
        df["asreview_user_name"] = "Unknown"
    else:
        df["asreview_user_name"] = df["asreview_user_name"].fillna("Unknown").replace("", "Unknown")

    if "asreview_user_email" not in df.columns:
        df["asreview_user_email"] = ""
    else:
        df["asreview_user_email"] = df["asreview_user_email"].fillna("")

    if "label" not in df.columns:
        df["label"] = 0
    else:
        df["label"] = pd.to_numeric(df["label"], errors="coerce").fillna(0).astype(int)

    # Parse screening timestamp
    if "asreview_time" in df.columns:
        df["parsed_time"] = pd.to_datetime(df["asreview_time"], errors="coerce")
        df["screen_date"] = df["parsed_time"].dt.date
    else:
        df["parsed_time"] = pd.NaT
        df["screen_date"] = None

    # 1. Total records breakdown per reviewer
    total_breakdown = []
    grouped_total = df.groupby(["asreview_user_name", "asreview_user_email"])

    for (reviewer_name, reviewer_email), group in grouped_total:
        total_count = len(group)
        rel_count = int((group["label"] == 1).sum())
        irrel_count = int((group["label"] == 0).sum())
        rate = round((rel_count / total_count * 100), 1) if total_count > 0 else 0.0

        total_breakdown.append({
            "name": reviewer_name,
            "email": reviewer_email,
            "total_labeled": total_count,
            "relevant": rel_count,
            "irrelevant": irrel_count,
            "inclusion_rate": rate
        })

    # Sort descending by total labeled
    total_breakdown.sort(key=lambda x: x["total_labeled"], reverse=True)

    # 2. Today's breakdown per reviewer
    today_breakdown = []
    today_df = df[df["screen_date"] == target_date]

    if not today_df.empty:
        grouped_today = today_df.groupby(["asreview_user_name", "asreview_user_email"])
        for (reviewer_name, reviewer_email), group in grouped_today:
            t_count = len(group)
            t_rel = int((group["label"] == 1).sum())
            t_irrel = int((group["label"] == 0).sum())
            t_rate = round((t_rel / t_count * 100), 1) if t_count > 0 else 0.0

            today_breakdown.append({
                "name": reviewer_name,
                "email": reviewer_email,
                "today_labeled": t_count,
                "relevant": t_rel,
                "irrelevant": t_irrel,
                "inclusion_rate": t_rate
            })
        today_breakdown.sort(key=lambda x: x["today_labeled"], reverse=True)
    else:
        # If no records screened today, list reviewers with 0
        for r in total_breakdown:
            today_breakdown.append({
                "name": r["name"],
                "email": r["email"],
                "today_labeled": 0,
                "relevant": 0,
                "irrelevant": 0,
                "inclusion_rate": 0.0
            })

    # 3. Overall Summary Cards
    total_screened = len(df)
    total_rel = int((df["label"] == 1).sum())
    total_irrel = int((df["label"] == 0).sum())
    total_today = len(today_df)
    overall_rate = round((total_rel / total_screened * 100), 1) if total_screened > 0 else 0.0

    summary = {
        "total_screened": total_screened,
        "total_today": total_today,
        "total_relevant": total_rel,
        "total_irrelevant": total_irrel,
        "overall_inclusion_rate": overall_rate,
        "reviewers_count": len(total_breakdown),
        "today_reviewers_count": sum(1 for r in today_breakdown if r["today_labeled"] > 0)
    }

    return {
        "summary": summary,
        "total_breakdown": total_breakdown,
        "today_breakdown": today_breakdown,
        "target_date_str": target_date_str
    }
