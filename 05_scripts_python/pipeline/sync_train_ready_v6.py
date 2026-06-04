from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FINAL_DIR = PROJECT_ROOT / "final_datasets"
TRAIN_READY_PATH = FINAL_DIR / "train_ready_dataset.csv"
FULL_AUDIT_PATH = FINAL_DIR / "train_ready_dataset_full_audit.csv"
SYNC_SUMMARY_PATH = FINAL_DIR / "train_ready_v6_sync_summary.csv"
SYNC_METADATA_PATH = FINAL_DIR / "train_ready_v6_sync_metadata.json"

PAIRING_COLUMNS = [
    "pairing_group",
    "pairing_role",
    "pairing_notes",
    "pairing_suitability_notes",
    "cleaning_action",
    "cleaning_reason",
    "meal_template_role",
    "meal_combo_valid",
]


def normalize_text(value: object) -> str:
    if pd.isna(value):
        return ""
    return " ".join(str(value).lower().strip().split())


def sync_from_v6(source_path: Path) -> pd.DataFrame:
    if not source_path.exists():
        raise FileNotFoundError(f"V6 source file not found: {source_path}")

    source_df = pd.read_csv(source_path)
    source_df["food_name_clean"] = source_df["food_name_clean"].map(normalize_text)
    source_df = source_df.drop_duplicates(subset=["food_name_clean"], keep="first").copy()

    old_train_df = pd.read_csv(TRAIN_READY_PATH) if TRAIN_READY_PATH.exists() else pd.DataFrame()
    if not old_train_df.empty:
        old_train_df["food_name_clean"] = old_train_df["food_name_clean"].map(normalize_text)

    old_audit_df = pd.read_csv(FULL_AUDIT_PATH) if FULL_AUDIT_PATH.exists() else old_train_df.copy()
    if not old_audit_df.empty:
        old_audit_df["food_name_clean"] = old_audit_df["food_name_clean"].map(normalize_text)

    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    source_df.to_csv(TRAIN_READY_PATH, index=False)

    if not old_audit_df.empty:
        audit_df = old_audit_df.copy()
        v6_lookup = source_df.set_index("food_name_clean")
        for column in PAIRING_COLUMNS:
            audit_df[column] = audit_df["food_name_clean"].map(v6_lookup[column]) if column in v6_lookup.columns else ""

        keep_mask = audit_df["food_name_clean"].isin(set(source_df["food_name_clean"]))
        audit_df.loc[keep_mask, "cleaning_action"] = audit_df.loc[keep_mask, "cleaning_action"].replace("", "keep")
        audit_df.loc[~keep_mask, "cleaning_action"] = "drop"

        if "recommendation_exclusion_reason" in audit_df.columns:
            fallback_reason = audit_df["recommendation_exclusion_reason"].fillna("")
            fallback_reason = fallback_reason.mask(fallback_reason.eq(""), "removed_by_v6_pairing_cleaning_filter")
        else:
            fallback_reason = "removed_by_v6_pairing_cleaning_filter"
        cleaning_reason = audit_df["cleaning_reason"].fillna("")
        audit_df.loc[~keep_mask, "cleaning_reason"] = cleaning_reason.loc[~keep_mask].mask(
            cleaning_reason.loc[~keep_mask].eq(""),
            fallback_reason.loc[~keep_mask] if isinstance(fallback_reason, pd.Series) else fallback_reason,
        )
        audit_df.to_csv(FULL_AUDIT_PATH, index=False)

    summary_rows = [
        {"metric": "source_v6_rows", "value": int(len(source_df))},
        {"metric": "source_v6_columns", "value": int(len(source_df.columns))},
        {"metric": "old_train_rows", "value": int(len(old_train_df)) if not old_train_df.empty else 0},
        {"metric": "old_audit_rows", "value": int(len(old_audit_df)) if not old_audit_df.empty else 0},
    ]
    for column in ["pairing_group", "pairing_role", "meal_template_role", "meal_combo_valid", "halal_status"]:
        if column in source_df.columns:
            for value, count in source_df[column].value_counts(dropna=False).items():
                summary_rows.append({"metric": f"{column}:{value}", "value": int(count)})

    pd.DataFrame(summary_rows).to_csv(SYNC_SUMMARY_PATH, index=False)
    metadata = {
        "sync_version": "train_ready_v6_sync_v1",
        "source_path": str(source_path),
        "train_ready_dataset": str(TRAIN_READY_PATH),
        "full_audit_dataset": str(FULL_AUDIT_PATH),
        "rows": int(len(source_df)),
        "columns": int(len(source_df.columns)),
        "new_pairing_columns": PAIRING_COLUMNS,
        "notes": [
            "train_ready_dataset.csv is synchronized from the teammate-updated train_ready_dataset_v6.csv.",
            "Matching is based on food_name_clean because v6 food_id values were re-indexed after cleaning.",
            "train_ready_dataset_full_audit.csv keeps previously audited rows and marks rows absent from v6 as cleaning_action=drop.",
        ],
    }
    SYNC_METADATA_PATH.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return source_df


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Synchronize local train-ready dataset with teammate V6 CSV.")
    parser.add_argument("source_path", type=Path, help="Path to train_ready_dataset_v6.csv")
    args = parser.parse_args()

    result = sync_from_v6(args.source_path)
    print(f"Updated: {TRAIN_READY_PATH}")
    print(f"Rows: {len(result)}")
    print(f"Summary: {SYNC_SUMMARY_PATH}")
    print(f"Metadata: {SYNC_METADATA_PATH}")
