from __future__ import annotations

import ast
import json
import re
from pathlib import Path
from typing import Iterable

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "raw_datasets" / "Dataset"
if not DATA_DIR.exists():
    DATA_DIR = PROJECT_ROOT / "Dataset"
if not DATA_DIR.exists():
    DATA_DIR = PROJECT_ROOT.parent / "Dataset"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "orang_b"

OFF_FILE = DATA_DIR / "en.openfoodfacts.org.products.csv"
OFF_USECOLS = [
    "code",
    "product_name",
    "brands",
    "countries_tags",
    "countries_en",
    "ingredients_text",
    "allergens",
    "allergens_en",
    "traces",
    "traces_en",
    "categories",
    "energy-kcal_100g",
    "proteins_100g",
    "fat_100g",
    "carbohydrates_100g",
]

ALLERGEN_COLUMNS = [
    "contains_gluten",
    "contains_dairy",
    "contains_nuts",
    "contains_peanut",
    "contains_seafood",
    "contains_egg",
    "contains_soy",
    "contains_celery",
    "contains_mustard",
    "contains_sesame",
    "contains_sulfite",
    "contains_other",
    "contains_unknown",
]

KEYWORDS = {
    "gluten": [
        "gluten",
        "wheat",
        "flour",
        "barley",
        "rye",
        "oat",
        "malt",
        "semolina",
        "spelt",
        "bread",
        "pasta",
        "noodle",
        "terigu",
        "gandum",
        "tepung terigu",
        "roti",
        "mie",
    ],
    "dairy": [
        "milk",
        "dairy",
        "cheese",
        "butter",
        "cream",
        "yogurt",
        "yoghurt",
        "whey",
        "casein",
        "lactose",
        "susu",
        "keju",
        "mentega",
        "krim",
    ],
    "nuts": [
        "tree nut",
        "almond",
        "cashew",
        "hazelnut",
        "walnut",
        "pecan",
        "pistachio",
        "macadamia",
        "brazil nut",
        "pine nut",
        "nut",
        "kacang mete",
        "kenari",
        "almond",
    ],
    "peanut": ["peanut", "groundnut", "kacang tanah"],
    "seafood": [
        "seafood",
        "fish",
        "shellfish",
        "shrimp",
        "prawn",
        "crab",
        "lobster",
        "mussel",
        "clam",
        "oyster",
        "squid",
        "cuttlefish",
        "anchovy",
        "tuna",
        "salmon",
        "ikan",
        "udang",
        "kepiting",
        "lobster",
        "kerang",
        "cumi",
        "teri",
        "tuna",
        "salmon",
    ],
    "egg": ["egg", "eggs", "albumen", "mayonnaise", "telur", "putih telur", "kuning telur"],
    "soy": ["soy", "soya", "soybean", "soybeans", "tofu", "tempeh", "tempe", "edamame", "kecap"],
    "celery": ["celery", "seledri"],
    "mustard": ["mustard", "moster"],
    "sesame": ["sesame", "sesame seed", "wijen"],
    "sulfite": ["sulfite", "sulphite", "sulfur dioxide", "sulphur dioxide"],
}

RAW_LABEL_MAP = {
    "gluten": "contains_gluten",
    "wheat": "contains_gluten",
    "barley": "contains_gluten",
    "rye": "contains_gluten",
    "dairy": "contains_dairy",
    "milk": "contains_dairy",
    "lactose": "contains_dairy",
    "casein": "contains_dairy",
    "nuts": "contains_nuts",
    "nut": "contains_nuts",
    "tree nuts": "contains_nuts",
    "almond": "contains_nuts",
    "cashew": "contains_nuts",
    "peanuts": "contains_peanut",
    "peanut": "contains_peanut",
    "fish": "contains_seafood",
    "shellfish": "contains_seafood",
    "seafood": "contains_seafood",
    "crustaceans": "contains_seafood",
    "molluscs": "contains_seafood",
    "eggs": "contains_egg",
    "egg": "contains_egg",
    "soybeans": "contains_soy",
    "soy": "contains_soy",
    "soya": "contains_soy",
    "celery": "contains_celery",
    "mustard": "contains_mustard",
    "sesame": "contains_sesame",
    "sesame seeds": "contains_sesame",
    "sulfites": "contains_sulfite",
    "sulphites": "contains_sulfite",
}


def normalize_text(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).lower()
    text = re.sub(r"[_:/|;]+", " ", text)
    text = re.sub(r"[^a-z0-9\u00c0-\u024f\u1e00-\u1eff\s,+.-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def split_terms(value: object) -> list[str]:
    if pd.isna(value) or value == "":
        return []
    if isinstance(value, list):
        return [normalize_text(v).replace("en ", "").strip() for v in value if normalize_text(v)]
    text = str(value).strip()
    if text.startswith("[") and text.endswith("]"):
        try:
            parsed = ast.literal_eval(text)
            if isinstance(parsed, list):
                return split_terms(parsed)
        except (SyntaxError, ValueError):
            pass
    text = text.replace("en:", "")
    terms = re.split(r"[,;|]", text)
    return [normalize_text(term) for term in terms if normalize_text(term)]


def empty_label_row() -> dict[str, bool]:
    return {col: False for col in ALLERGEN_COLUMNS}


def labels_from_terms(terms: Iterable[str]) -> tuple[dict[str, bool], bool]:
    labels = empty_label_row()
    matched_any = False
    unknown_terms = []
    for term in terms:
        norm = normalize_text(term)
        if not norm:
            continue
        matched = False
        for raw_key, column in RAW_LABEL_MAP.items():
            if raw_key in norm:
                labels[column] = True
                matched = True
                matched_any = True
        if not matched:
            unknown_terms.append(norm)
    if unknown_terms:
        labels["contains_other"] = True
        matched_any = True
    return labels, matched_any


def labels_from_keywords(text: object) -> tuple[dict[str, bool], list[str]]:
    labels = empty_label_row()
    norm = normalize_text(text)
    matched_keywords: list[str] = []
    if not norm:
        return labels, matched_keywords
    padded = f" {norm} "
    for category, keywords in KEYWORDS.items():
        for keyword in keywords:
            pattern = r"(?<![a-z0-9])" + re.escape(keyword.lower()) + r"(?![a-z0-9])"
            if re.search(pattern, padded):
                labels[f"contains_{category}"] = True
                matched_keywords.append(keyword)
                break
    if labels["contains_peanut"]:
        labels["contains_nuts"] = True
    return labels, matched_keywords


def merge_labels(*rows: dict[str, bool]) -> dict[str, bool]:
    merged = empty_label_row()
    for row in rows:
        for col in ALLERGEN_COLUMNS:
            merged[col] = bool(merged[col] or row.get(col, False))
    if merged["contains_peanut"]:
        merged["contains_nuts"] = True
    return merged


def bool_value(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if pd.isna(value):
        return False
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def make_record(
    source: str,
    source_record_id: object,
    product_name: object,
    ingredient_text: object = "",
    allergens_raw: object = "",
    labels: dict[str, bool] | None = None,
    label_source: str = "unknown",
    confidence: str = "low",
) -> dict[str, object]:
    labels = labels or empty_label_row()
    has_positive = any(labels[col] for col in ALLERGEN_COLUMNS if col != "contains_unknown")
    if not has_positive and label_source in {"unknown", "keyword_no_match"}:
        labels["contains_unknown"] = True
    record = {
        "source": source,
        "source_record_id": source_record_id,
        "product_name": product_name,
        "ingredient_text": ingredient_text,
        "allergens_raw": allergens_raw,
        "label_source": label_source,
        "confidence": confidence,
    }
    record.update(labels)
    return record


def build_allergen_reference() -> pd.DataFrame:
    rows = []
    for category, keywords in KEYWORDS.items():
        for keyword in sorted(set(keywords)):
            rows.append(
                {
                    "allergen_group": category,
                    "ingredient_keyword": keyword,
                    "canonical_name": keyword,
                    "risk_level": "high",
                    "source": "curated_keyword_dictionary",
                    "match_type": "keyword",
                }
            )
    for raw, column in sorted(RAW_LABEL_MAP.items()):
        rows.append(
            {
                "allergen_group": column.replace("contains_", ""),
                "ingredient_keyword": raw,
                "canonical_name": raw,
                "risk_level": "high",
                "source": "raw_label_mapping",
                "match_type": "label",
            }
        )
    return pd.DataFrame(rows).drop_duplicates()


def load_fooddata_records() -> list[dict[str, object]]:
    path = DATA_DIR / "FoodData.csv"
    if not path.exists():
        return []
    df = pd.read_csv(path)
    records = []
    for idx, row in df.iterrows():
        terms = split_terms(row.get("Allergy", ""))
        labels_terms, matched_terms = labels_from_terms(terms)
        labels_kw, matched_kw = labels_from_keywords(" ".join(map(str, [row.get("Food", ""), row.get("Group", ""), row.get("Type", "")])))
        labels = merge_labels(labels_terms, labels_kw)
        if pd.isna(row.get("Allergy")) or normalize_text(row.get("Allergy", "")) == "":
            label_source, confidence = "unknown", "low"
        elif matched_terms:
            label_source, confidence = "explicit_allergy_taxonomy", "high"
        elif matched_kw:
            label_source, confidence = "keyword_from_food_taxonomy", "medium"
        else:
            label_source, confidence = "unmapped_explicit_allergy", "low"
            labels["contains_other"] = True
        records.append(make_record("FoodData", idx, row.get("Food", ""), row.get("Group", ""), row.get("Allergy", ""), labels, label_source, confidence))
    return records


def load_food_ingredients_records() -> list[dict[str, object]]:
    path = DATA_DIR / "food_ingredients_and_allergens.csv"
    if not path.exists():
        return []
    df = pd.read_csv(path).drop_duplicates()
    ingredient_cols = ["Main Ingredient", "Sweetener", "Fat/Oil", "Seasoning"]
    records = []
    for idx, row in df.iterrows():
        ingredient_text = ", ".join([str(row.get(col, "")) for col in ingredient_cols if pd.notna(row.get(col, ""))])
        terms = split_terms(row.get("Allergens", ""))
        labels_terms, matched_terms = labels_from_terms(terms)
        labels_kw, matched_kw = labels_from_keywords(f"{row.get('Food Product', '')} {ingredient_text} {row.get('Allergens', '')}")
        labels = merge_labels(labels_terms, labels_kw)
        prediction = normalize_text(row.get("Prediction", ""))
        if "does not contain" in prediction and not terms and not matched_kw:
            label_source, confidence = "explicit_negative_prediction", "medium"
        elif terms or matched_terms:
            label_source, confidence = "explicit_allergen_list", "high"
        elif matched_kw:
            label_source, confidence = "keyword_from_ingredients", "medium"
        else:
            label_source, confidence = "unknown", "low"
        records.append(make_record("food_ingredients_and_allergens", idx, row.get("Food Product", ""), ingredient_text, row.get("Allergens", ""), labels, label_source, confidence))
    return records


def load_allergies_10k_records() -> list[dict[str, object]]:
    path = DATA_DIR / "allergies_10k.csv"
    if not path.exists():
        return []
    df = pd.read_csv(path)
    records = []
    for idx, row in df.iterrows():
        terms = split_terms(row.get("allergens", ""))
        labels_terms, matched_terms = labels_from_terms(terms)
        labels_kw, matched_kw = labels_from_keywords(row.get("ingredient", ""))
        labels = merge_labels(labels_terms, labels_kw)
        if terms:
            label_source, confidence = "explicit_ingredient_allergen_tags", "high"
        elif matched_kw:
            label_source, confidence = "keyword_from_ingredient_text", "medium"
        else:
            label_source, confidence = "explicit_empty_allergen_list", "high"
        records.append(make_record("allergies_10k", row.get("Unnamed: 0", idx), row.get("ingredient", ""), row.get("ingredient", ""), row.get("allergens", ""), labels, label_source, confidence))
    return records


def records_from_boolean_food_file(path: Path, source: str) -> list[dict[str, object]]:
    if not path.exists():
        return []
    df = pd.read_csv(path).drop_duplicates()
    records = []
    bool_map = {
        "contains_gluten": "contains_gluten",
        "contains_dairy": "contains_dairy",
        "contains_nuts": "contains_nuts",
        "contains_soy": "contains_soy",
        "contains_eggs": "contains_egg",
        "contains_fish": "contains_seafood",
    }
    for idx, row in df.iterrows():
        labels_bool = empty_label_row()
        for src_col, out_col in bool_map.items():
            if src_col in row:
                labels_bool[out_col] = bool_value(row.get(src_col))
        terms = split_terms(row.get("allergens", ""))
        labels_terms, _ = labels_from_terms(terms)
        text = " ".join(str(row.get(col, "")) for col in ["product_name", "categories", "ingredients"] if col in row)
        labels_kw, matched_kw = labels_from_keywords(text)
        labels = merge_labels(labels_bool, labels_terms, labels_kw)
        if any(labels_bool.values()) or terms:
            label_source, confidence = "explicit_boolean_or_allergen_tags", "high"
        elif matched_kw:
            label_source, confidence = "keyword_from_product_text", "medium"
        else:
            label_source, confidence = "explicit_boolean_negative", "medium"
        records.append(make_record(source, idx, row.get("product_name", ""), row.get("ingredients", ""), row.get("allergens", ""), labels, label_source, confidence))
    return records


def records_from_keyword_only_file(path: Path, source: str, name_col: str, ingredient_col: str | None = None, max_rows: int | None = None) -> list[dict[str, object]]:
    if not path.exists():
        return []
    df = pd.read_csv(path, nrows=max_rows)
    df = df.drop_duplicates()
    records = []
    for idx, row in df.iterrows():
        ingredient_text = row.get(ingredient_col, "") if ingredient_col else ""
        text = f"{row.get(name_col, '')} {ingredient_text}"
        labels_kw, matched_kw = labels_from_keywords(text)
        label_source = "keyword_from_food_name_or_ingredients" if matched_kw else "keyword_no_match"
        confidence = "medium" if matched_kw and ingredient_col else "low"
        records.append(make_record(source, idx, row.get(name_col, ""), ingredient_text, "", labels_kw, label_source, confidence))
    return records


def load_openfoodfacts_records(max_chunks: int = 20, chunk_size: int = 100_000, max_records: int = 50_000) -> list[dict[str, object]]:
    if not OFF_FILE.exists():
        return []
    records = []
    reader = pd.read_csv(
        OFF_FILE,
        sep="\t",
        usecols=lambda c: c in OFF_USECOLS,
        chunksize=chunk_size,
        low_memory=False,
        on_bad_lines="skip",
    )
    for chunk_idx, chunk in enumerate(reader):
        if max_chunks is not None and chunk_idx >= max_chunks:
            break
        has_name = chunk["product_name"].notna()
        has_signal = chunk[["ingredients_text", "allergens", "allergens_en", "traces", "traces_en"]].notna().any(axis=1)
        indonesia = chunk.get("countries_tags", pd.Series("", index=chunk.index)).fillna("").str.contains("indonesia", case=False)
        explicit_allergen = chunk[["allergens", "allergens_en"]].notna().any(axis=1)
        sampled = chunk[has_name & has_signal & (indonesia | explicit_allergen)].copy()
        for idx, row in sampled.iterrows():
            allergens_raw = ", ".join(str(row.get(col, "")) for col in ["allergens", "allergens_en", "traces", "traces_en"] if pd.notna(row.get(col, "")))
            terms = split_terms(allergens_raw)
            labels_terms, matched_terms = labels_from_terms(terms)
            labels_kw, matched_kw = labels_from_keywords(f"{row.get('product_name', '')} {row.get('ingredients_text', '')}")
            labels = merge_labels(labels_terms, labels_kw)
            if matched_terms:
                label_source, confidence = "openfoodfacts_explicit_allergen_tags", "high"
            elif matched_kw:
                label_source, confidence = "openfoodfacts_keyword_from_ingredients", "medium"
            else:
                label_source, confidence = "openfoodfacts_unknown", "low"
            records.append(make_record("openfoodfacts", row.get("code", idx), row.get("product_name", ""), row.get("ingredients_text", ""), allergens_raw, labels, label_source, confidence))
            if len(records) >= max_records:
                return records
    return records


def build_quality_report(labels: pd.DataFrame, source_files: dict[str, Path]) -> pd.DataFrame:
    rows = []
    for source, path in source_files.items():
        if not path.exists():
            rows.append({"source": source, "exists": False, "rows": 0, "duplicates": None, "missing_key_fields": None})
            continue
        if source == "openfoodfacts":
            rows.append({"source": source, "exists": True, "rows": "large_chunked", "duplicates": None, "missing_key_fields": None})
            continue
        df = pd.read_csv(path)
        key_cols = [col for col in ["product_name", "Food Product", "Food", "ingredient", "allergens", "Allergens", "Allergy"] if col in df.columns]
        missing_key_fields = int(df[key_cols].isna().sum().sum()) if key_cols else 0
        rows.append({"source": source, "exists": True, "rows": len(df), "duplicates": int(df.duplicated().sum()), "missing_key_fields": missing_key_fields})
    by_source = labels.groupby("source").size().rename("label_rows").reset_index()
    report = pd.DataFrame(rows).merge(by_source, on="source", how="left")
    report["label_rows"] = report["label_rows"].fillna(0).astype(int)
    return report


def build_eda_summary(labels: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in ALLERGEN_COLUMNS:
        rows.append({"metric": col, "value": int(labels[col].sum())})
    rows.extend(
        [
            {"metric": "total_rows", "value": int(len(labels))},
            {"metric": "duplicate_product_names", "value": int(labels.duplicated(["source", "product_name"]).sum())},
            {"metric": "high_confidence_rows", "value": int((labels["confidence"] == "high").sum())},
            {"metric": "medium_confidence_rows", "value": int((labels["confidence"] == "medium").sum())},
            {"metric": "low_confidence_rows", "value": int((labels["confidence"] == "low").sum())},
        ]
    )
    return pd.DataFrame(rows)


def write_handover_notes(labels: pd.DataFrame, quality: pd.DataFrame, output_dir: Path) -> None:
    top_counts = labels[ALLERGEN_COLUMNS].sum().sort_values(ascending=False)
    content = [
        "# Handover Notes - Orang B Alergen",
        "",
        "## Output",
        "",
        "- `allergen_reference_clean.csv`: kamus keyword dan mapping label alergen.",
        "- `food_allergen_labels.csv`: label multi-label per produk/makanan.",
        "- `ingredient_allergen_training.csv`: subset berbasis ingredient text untuk eksperimen klasifikasi teks.",
        "- `allergen_data_quality_report.csv`: audit jumlah baris, duplikasi, dan missing key fields.",
        "- `allergen_eda_summary.csv`: ringkasan distribusi label.",
        "",
        "## Prinsip labeling",
        "",
        "- Label eksplisit dari kolom allergen/boolean diberi confidence `high`.",
        "- Keyword match dari ingredient/name diberi confidence `medium` atau `low`.",
        "- Baris tanpa bukti alergen tidak otomatis aman, kecuali sumbernya memberi label negatif eksplisit.",
        "- Untuk mode conservative, `contains_unknown = True` sebaiknya difilter jika user punya alergi kritis.",
        "",
        "## Distribusi label",
        "",
    ]
    for col, value in top_counts.items():
        content.append(f"- `{col}`: {int(value)}")
    content.extend(["", "## Quality report", "", quality.to_markdown(index=False)])
    (output_dir / "handover_notes_orang_b.md").write_text("\n".join(content), encoding="utf-8")


def run_pipeline(off_max_chunks: int = 20, off_chunk_size: int = 100_000, off_max_records: int = 50_000) -> dict[str, Path]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    records: list[dict[str, object]] = []
    records += load_fooddata_records()
    records += load_food_ingredients_records()
    records += load_allergies_10k_records()
    records += records_from_boolean_food_file(DATA_DIR / "foods_allergens.csv", "foods_allergens")
    records += records_from_boolean_food_file(DATA_DIR / "foods_dietary_restrictions.csv", "foods_dietary_restrictions")
    records += records_from_boolean_food_file(DATA_DIR / "foods_health_scores_allergens.csv", "foods_health_scores_allergens")
    records += records_from_keyword_only_file(DATA_DIR / "comprehensive_foods_usda.csv", "comprehensive_foods_usda", "food_name", "ingredients")
    records += records_from_keyword_only_file(DATA_DIR / "healthy_foods_database.csv", "healthy_foods_database", "food_name", None)
    records += records_from_keyword_only_file(DATA_DIR / "nutrition.csv", "indonesian_nutrition", "name", None)
    records += load_openfoodfacts_records(max_chunks=off_max_chunks, chunk_size=off_chunk_size, max_records=off_max_records)

    labels = pd.DataFrame(records)
    labels["product_name_clean"] = labels["product_name"].map(normalize_text)
    labels["ingredient_text_clean"] = labels["ingredient_text"].map(normalize_text)
    labels = labels.drop_duplicates(subset=["source", "source_record_id", "product_name_clean", "ingredient_text_clean"])

    allergen_reference = build_allergen_reference()
    training_subset = labels[
        labels["ingredient_text_clean"].ne("")
        & labels["confidence"].isin(["high", "medium"])
    ].copy()

    source_files = {
        "FoodData": DATA_DIR / "FoodData.csv",
        "food_ingredients_and_allergens": DATA_DIR / "food_ingredients_and_allergens.csv",
        "allergies_10k": DATA_DIR / "allergies_10k.csv",
        "foods_allergens": DATA_DIR / "foods_allergens.csv",
        "foods_dietary_restrictions": DATA_DIR / "foods_dietary_restrictions.csv",
        "foods_health_scores_allergens": DATA_DIR / "foods_health_scores_allergens.csv",
        "comprehensive_foods_usda": DATA_DIR / "comprehensive_foods_usda.csv",
        "healthy_foods_database": DATA_DIR / "healthy_foods_database.csv",
        "indonesian_nutrition": DATA_DIR / "nutrition.csv",
        "openfoodfacts": OFF_FILE,
    }
    quality = build_quality_report(labels, source_files)
    eda = build_eda_summary(labels)

    paths = {
        "allergen_reference": OUTPUT_DIR / "allergen_reference_clean.csv",
        "food_allergen_labels": OUTPUT_DIR / "food_allergen_labels.csv",
        "ingredient_training": OUTPUT_DIR / "ingredient_allergen_training.csv",
        "quality_report": OUTPUT_DIR / "allergen_data_quality_report.csv",
        "eda_summary": OUTPUT_DIR / "allergen_eda_summary.csv",
        "metadata": OUTPUT_DIR / "pipeline_metadata.json",
    }

    allergen_reference.to_csv(paths["allergen_reference"], index=False)
    labels.to_csv(paths["food_allergen_labels"], index=False)
    training_subset.to_csv(paths["ingredient_training"], index=False)
    quality.to_csv(paths["quality_report"], index=False)
    eda.to_csv(paths["eda_summary"], index=False)
    write_handover_notes(labels, quality, OUTPUT_DIR)

    metadata = {
        "total_label_rows": int(len(labels)),
        "training_subset_rows": int(len(training_subset)),
        "output_dir": str(OUTPUT_DIR),
        "openfoodfacts_settings": {
            "max_chunks": off_max_chunks,
            "chunk_size": off_chunk_size,
            "max_records": off_max_records,
        },
        "allergen_columns": ALLERGEN_COLUMNS,
    }
    paths["metadata"].write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return paths


if __name__ == "__main__":
    written = run_pipeline()
    for name, path in written.items():
        print(f"{name}: {path}")
