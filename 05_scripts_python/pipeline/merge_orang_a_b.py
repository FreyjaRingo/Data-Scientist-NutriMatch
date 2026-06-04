from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from orang_b_allergen_pipeline import ALLERGEN_COLUMNS, labels_from_keywords, normalize_text


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "outputs"
ORANG_B_DIR = OUTPUT_DIR / "orang_b"
MERGED_DIR = OUTPUT_DIR / "merged"


FOOD_NAME_CANDIDATES = ["food_name", "name", "nama_makanan", "product_name", "Food", "food"]
CALORIE_CANDIDATES = ["calories_100g", "calories", "kalori", "energy_kcal", "energy-kcal_100g"]
PROTEIN_CANDIDATES = ["protein_100g", "proteins_100g", "protein_g", "proteins", "protein"]
FAT_CANDIDATES = ["fat_100g", "fat_g", "fat", "lemak"]
CARB_CANDIDATES = ["carbohydrate_100g", "carbohydrates_100g", "carbs_g", "carbohydrate", "karbohidrat"]
IMAGE_CANDIDATES = ["image_url", "image", "img_url", "photo_url"]
SOURCE_CANDIDATES = ["source", "data_source", "dataset_source"]
ID_CANDIDATES = ["food_id", "id", "fdc_id", "source_record_id"]


def first_existing(columns: list[str], candidates: list[str]) -> str | None:
    lower_map = {col.lower(): col for col in columns}
    for candidate in candidates:
        if candidate.lower() in lower_map:
            return lower_map[candidate.lower()]
    return None


def score_food_master_columns(columns: list[str]) -> int:
    score = 0
    for candidates, weight in [
        (FOOD_NAME_CANDIDATES, 5),
        (CALORIE_CANDIDATES, 3),
        (PROTEIN_CANDIDATES, 2),
        (FAT_CANDIDATES, 2),
        (CARB_CANDIDATES, 2),
        (ID_CANDIDATES, 1),
    ]:
        if first_existing(columns, candidates):
            score += weight
    return score


def score_food_master_path(path: Path) -> int:
    path_text = str(path).lower()
    score = 0
    if "food_master_clean" in path.name.lower():
        score += 20
    if "processed" in path_text or "output" in path_text or "outputs" in path_text:
        score += 5
    if "raw" in path_text:
        score -= 5
    if path.name.lower() == "nutrition.csv":
        score -= 3
    return score


def find_food_master(root: Path) -> tuple[Path, int, list[str]]:
    candidates: list[tuple[int, Path, list[str]]] = []
    skip_parts = {"orang_b", ".git", "__pycache__"}
    for csv_path in root.rglob("*.csv"):
        if any(part in skip_parts for part in csv_path.parts):
            continue
        if csv_path.name == "en.openfoodfacts.org.products.csv":
            continue
        try:
            sample = pd.read_csv(csv_path, nrows=5)
        except Exception:
            continue
        score = score_food_master_columns(list(sample.columns)) + score_food_master_path(csv_path)
        if score >= 10:
            candidates.append((score, csv_path, list(sample.columns)))
    if not candidates:
        raise FileNotFoundError(
            f"Tidak menemukan kandidat food master di {root}. "
            "Berikan path eksplisit ke food_master_clean.csv milik Orang A."
        )
    candidates.sort(key=lambda item: (item[0], -len(str(item[1]))), reverse=True)
    score, path, columns = candidates[0]
    return path, score, columns


def standardize_food_master(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    columns = list(df.columns)
    name_col = first_existing(columns, FOOD_NAME_CANDIDATES)
    if not name_col:
        raise ValueError(f"Tidak ada kolom nama makanan pada {path}")

    out = pd.DataFrame()
    id_col = first_existing(columns, ID_CANDIDATES)
    used_input_cols = {col for col in [id_col, name_col] if col}
    out["food_id"] = df[id_col] if id_col else range(1, len(df) + 1)
    out["food_name"] = df[name_col]
    out["food_name_clean"] = df["food_name_clean"] if "food_name_clean" in df.columns else df[name_col].map(normalize_text)

    rename_map = {
        "calories_100g": first_existing(columns, CALORIE_CANDIDATES),
        "protein_100g": first_existing(columns, PROTEIN_CANDIDATES),
        "fat_100g": first_existing(columns, FAT_CANDIDATES),
        "carbohydrate_100g": first_existing(columns, CARB_CANDIDATES),
        "image_url": first_existing(columns, IMAGE_CANDIDATES),
        "source": first_existing(columns, SOURCE_CANDIDATES),
    }
    for out_col, in_col in rename_map.items():
        if in_col:
            out[out_col] = df[in_col]
            used_input_cols.add(in_col)
        else:
            out[out_col] = pd.NA
    out["source"] = out["source"].fillna(path.stem)

    for col in df.columns:
        if col in used_input_cols or col == "food_name_clean" or col in out.columns:
            continue
        out[col] = df[col]

    out = out.drop_duplicates(subset=["food_name_clean"]).reset_index(drop=True)
    return out


def aggregate_orang_b_labels(path: Path) -> pd.DataFrame:
    labels = pd.read_csv(path, low_memory=False)
    if "product_name_clean" not in labels.columns:
        labels["product_name_clean"] = labels["product_name"].map(normalize_text)
    labels = labels[labels["product_name_clean"].notna() & labels["product_name_clean"].ne("")].copy()

    for col in ALLERGEN_COLUMNS:
        labels[col] = labels[col].fillna(False).astype(bool)

    known_cols = [col for col in ALLERGEN_COLUMNS if col != "contains_unknown"]
    weak_unknown_only = (
        labels["label_source"].fillna("").eq("keyword_no_match")
        & ~labels[known_cols].any(axis=1)
    )
    labels = labels.loc[~weak_unknown_only].copy()

    confidence_rank = {"unknown": 0, "low": 1, "medium": 2, "high": 3}
    rank_confidence = {value: key for key, value in confidence_rank.items()}
    labels["confidence_rank"] = labels["confidence"].fillna("unknown").map(confidence_rank).fillna(0).astype(int)

    grouped_bool = labels.groupby("product_name_clean", as_index=False)[ALLERGEN_COLUMNS].max()
    meta = labels.groupby("product_name_clean").agg(
        allergen_match_count=("product_name_clean", "size"),
        confidence_rank=("confidence_rank", "max"),
        allergen_sources=("source", lambda s: "|".join(sorted(set(map(str, s)))[:8])),
        label_sources=("label_source", lambda s: "|".join(sorted(set(map(str, s)))[:8])),
    ).reset_index()
    meta["confidence"] = meta["confidence_rank"].map(rank_confidence).fillna("unknown")
    meta = meta.drop(columns=["confidence_rank"])
    return grouped_bool.merge(meta, on="product_name_clean", how="left")


def apply_keyword_fallback(df: pd.DataFrame) -> pd.DataFrame:
    unmatched = df["merge_status"].eq("not_matched")
    for idx in df[unmatched].index:
        labels, matched_keywords = labels_from_keywords(df.at[idx, "food_name"])
        if matched_keywords:
            for col in ALLERGEN_COLUMNS:
                df.at[idx, col] = bool(labels[col])
            df.at[idx, "merge_status"] = "keyword_fallback"
            df.at[idx, "confidence"] = "low"
            df.at[idx, "allergen_sources"] = "curated_keyword_dictionary"
            df.at[idx, "label_sources"] = "keyword_from_food_name"
            df.at[idx, "allergen_match_count"] = 1
    return df


def merge_food_and_allergens(
    food_master_path: Path | None = None,
    search_root: Path | None = None,
    conservative_unknown: bool = True,
) -> dict[str, Path]:
    MERGED_DIR.mkdir(parents=True, exist_ok=True)
    search_root = search_root or PROJECT_ROOT

    if food_master_path is None:
        food_master_path, score, columns = find_food_master(search_root)
    else:
        food_master_path = Path(food_master_path)
        score = score_food_master_columns(list(pd.read_csv(food_master_path, nrows=5).columns))
        columns = list(pd.read_csv(food_master_path, nrows=1).columns)

    food = standardize_food_master(food_master_path)
    allergen = aggregate_orang_b_labels(ORANG_B_DIR / "food_allergen_labels.csv")

    merged = food.merge(
        allergen,
        left_on="food_name_clean",
        right_on="product_name_clean",
        how="left",
    )
    merged["merge_status"] = merged["product_name_clean"].notna().map({True: "exact_name", False: "not_matched"})
    merged = merged.drop(columns=["product_name_clean"])

    for col in ALLERGEN_COLUMNS:
        if col not in merged.columns:
            merged[col] = False
        merged[col] = merged[col].astype("boolean").fillna(False).astype(bool)

    merged["confidence"] = merged["confidence"].fillna("unknown")
    merged["allergen_sources"] = merged["allergen_sources"].fillna("not_matched")
    merged["label_sources"] = merged["label_sources"].fillna("not_matched")
    merged["allergen_match_count"] = merged["allergen_match_count"].fillna(0).astype(int)

    merged = apply_keyword_fallback(merged)

    still_unmatched = merged["merge_status"].eq("not_matched")
    if conservative_unknown:
        merged.loc[still_unmatched, "contains_unknown"] = True

    core_food_cols = [
        "food_id",
        "food_name",
        "food_name_clean",
        "calories_100g",
        "protein_100g",
        "fat_100g",
        "carbohydrate_100g",
        "image_url",
        "source",
    ]
    extra_food_cols = [col for col in food.columns if col not in core_food_cols]
    train_ready_cols = [
        *core_food_cols,
        *extra_food_cols,
        *ALLERGEN_COLUMNS,
        "confidence",
        "allergen_sources",
        "label_sources",
        "allergen_match_count",
        "merge_status",
    ]
    merged = merged[train_ready_cols]

    summary = pd.DataFrame(
        [
            {"metric": "food_master_path", "value": str(food_master_path)},
            {"metric": "food_master_score", "value": score},
            {"metric": "food_master_rows", "value": len(food)},
            {"metric": "train_ready_rows", "value": len(merged)},
            {"metric": "exact_name_rows", "value": int((merged["merge_status"] == "exact_name").sum())},
            {"metric": "keyword_fallback_rows", "value": int((merged["merge_status"] == "keyword_fallback").sum())},
            {"metric": "not_matched_rows", "value": int((merged["merge_status"] == "not_matched").sum())},
            {"metric": "conservative_unknown", "value": conservative_unknown},
        ]
    )

    paths = {
        "train_ready": MERGED_DIR / "train_ready_dataset.csv",
        "merge_summary": MERGED_DIR / "merge_summary.csv",
        "food_master_standardized": MERGED_DIR / "food_master_standardized.csv",
        "allergen_labels_aggregated": MERGED_DIR / "allergen_labels_aggregated.csv",
        "metadata": MERGED_DIR / "merge_metadata.json",
    }
    merged.to_csv(paths["train_ready"], index=False)
    summary.to_csv(paths["merge_summary"], index=False)
    food.to_csv(paths["food_master_standardized"], index=False)
    allergen.to_csv(paths["allergen_labels_aggregated"], index=False)
    paths["metadata"].write_text(
        json.dumps(
            {
                "food_master_path": str(food_master_path),
                "food_master_score": score,
                "food_master_columns": columns,
                "conservative_unknown": conservative_unknown,
                "outputs": {name: str(path) for name, path in paths.items()},
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return paths


if __name__ == "__main__":
    written = merge_food_and_allergens()
    for name, path in written.items():
        print(f"{name}: {path}")
