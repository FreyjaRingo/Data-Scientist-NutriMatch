from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = PROJECT_ROOT / "final_datasets" / "train_ready_dataset.csv"
SUMMARY_PATH = PROJECT_ROOT / "final_datasets" / "feature_enrichment_summary.csv"
METADATA_PATH = PROJECT_ROOT / "final_datasets" / "feature_enrichment_metadata.json"
DATA_DIR = PROJECT_ROOT / "raw_datasets" / "Dataset"
if not DATA_DIR.exists():
    DATA_DIR = PROJECT_ROOT / "Dataset"
if not DATA_DIR.exists():
    DATA_DIR = PROJECT_ROOT.parent / "Dataset"
RECIPE_ARCHIVE_DIR = DATA_DIR / "archive"
INDONESIAN_BY_BASE_DIR = DATA_DIR / "archive (1)"
MEAL_TYPE_REFERENCE_PATH = DATA_DIR / "archive (2)" / "nutrition.csv"
GLOBAL_RECIPE_REFERENCE_PATH = DATA_DIR / "archive (3)" / "1_Recipe_csv.csv"

ADDED_COLUMNS = [
    "food_category",
    "food_category_source",
    "base_ingredient",
    "base_ingredient_tags",
    "suitable_breakfast",
    "suitable_lunch",
    "suitable_dinner",
    "meal_time_tags",
    "primary_meal_time",
    "feature_rule_version",
    "recipe_reference_match",
    "recipe_reference_source",
    "recipe_reference_title",
    "recipe_ingredients_reference",
]


def normalize_text(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).lower()
    text = re.sub(r"[^a-z0-9\s-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_base_category(value: object) -> str:
    category = normalize_text(value)
    mapping = {
        "ayam": "ayam",
        "chicken": "ayam",
        "sapi": "sapi",
        "beef": "sapi",
        "kambing": "kambing",
        "lamb": "kambing",
        "ikan": "ikan",
        "fish": "ikan",
        "udang": "seafood",
        "shrimp": "seafood",
        "seafood": "seafood",
        "tahu": "kedelai",
        "tofu": "kedelai",
        "tempe": "kedelai",
        "telur": "telur",
        "egg": "telur",
    }
    return mapping.get(category, category or "unknown")


def has_any(text: str, keywords: list[str]) -> bool:
    padded = f" {text} "
    return any(re.search(r"(?<![a-z0-9])" + re.escape(keyword) + r"(?![a-z0-9])", padded) for keyword in keywords)


def phrase_in_text(phrase: str, text: str) -> bool:
    return bool(re.search(r"(?<![a-z0-9])" + re.escape(phrase) + r"(?![a-z0-9])", text))


CATEGORY_RULES: list[tuple[str, list[str]]] = [
    ("minuman", ["air", "teh", "kopi", "susu", "jus", "sirup", "es ", "cendol", "dawet", "minuman", "wedang"]),
    ("berkuah", ["kuah", "sop", "sup", "soto", "rawon", "gulai", "lodeh", "opor", "laksa", "bakso", "kaldu", "kari", "semur"]),
    ("gorengan", ["goreng", "bakwan", "perkedel", "rempeyek", "peyek", "kerupuk", "keripik", "emping"]),
    ("sayuran", ["sayur", "bayam", "kangkung", "sawi", "kol", "kubis", "wortel", "buncis", "brokoli", "tauge", "taoge", "daun", "labu", "terong", "terung", "tomat", "timun", "mentimun", "selada", "andewi", "kacang panjang"]),
    ("buah", ["apel", "pisang", "alpukat", "anggur", "jeruk", "mangga", "pepaya", "nanas", "semangka", "melon", "jambu", "durian", "rambutan", "salak", "sirsak", "belimbing", "nangka", "kelapa", "markisa", "stroberi"]),
    ("karbohidrat_pokok", ["nasi", "beras", "ketan", "lontong", "ketupat", "bubur", "mie", "mi ", "bihun", "kwetiau", "roti", "jagung", "singkong", "ubi", "kentang", "talas", "sagu", "tepung"]),
    ("lauk_hewani", ["ayam", "sapi", "daging", "kambing", "kerbau", "ikan", "udang", "cumi", "kepiting", "kerang", "telur", "bebek", "itik", "angsa", "hati", "paru", "limpa", "usus", "abon", "bakso"]),
    ("lauk_nabati", ["tahu", "tempe", "oncom", "kedelai", "kacang hijau", "kacang merah", "kacang tanah", "kacang kedelai"]),
    ("bumbu_sambal", ["sambal", "cabai", "cabe", "kecap", "saus", "terasi", "bumbu", "andaliman", "lada", "merica", "garam"]),
    ("snack_dessert", ["kue", "bolu", "biskuit", "cookies", "wafer", "dodol", "puding", "agar-agar", "permen", "coklat", "cokelat", "manisan", "selai"]),
]


BASE_INGREDIENT_RULES: list[tuple[str, list[str]]] = [
    ("telur", ["telur"]),
    ("ayam", ["ayam"]),
    ("sapi", ["sapi", "daging sapi", "abon"]),
    ("daging_lain", ["babi", "kerbau"]),
    ("ikan", ["ikan", "haruan", "haruwan", "bandeng", "lele", "tongkol", "tuna", "salmon", "teri", "kembung", "gabus", "patin", "nila", "gurame", "gurami", "mujair", "kakap"]),
    ("seafood", ["udang", "cumi", "kepiting", "kerang", "lobster", "rajungan"]),
    ("kedelai", ["kedelai", "tahu", "tempe", "oncom", "ampas tahu"]),
    ("kacang", ["kacang", "almond", "mete", "kenari"]),
    ("beras", ["beras", "nasi", "ketan", "lontong", "ketupat", "bubur"]),
    ("jagung", ["jagung"]),
    ("umbi", ["singkong", "ubi", "kentang", "talas", "sagu", "ganyong", "sukun"]),
    ("gandum", ["gandum", "terigu", "roti", "mie", "mi ", "bihun", "kwetiau", "tepung"]),
    ("susu", ["susu", "keju", "yogurt", "yoghurt", "mentega"]),
    ("sayuran", ["sayur", "bayam", "kangkung", "sawi", "kol", "wortel", "buncis", "brokoli", "daun", "labu", "terong", "terung", "tomat", "timun", "selada"]),
    ("buah", ["apel", "pisang", "alpukat", "anggur", "jeruk", "mangga", "pepaya", "nanas", "semangka", "melon", "jambu", "durian", "rambutan", "salak", "sirsak", "belimbing", "nangka", "kelapa"]),
    ("kambing", ["kambing"]),
    ("unggas_lain", ["bebek", "itik", "angsa"]),
    ("bumbu_rempah", ["sambal", "cabai", "cabe", "kecap", "saus", "terasi", "bumbu", "andaliman", "lada", "merica"]),
]


def infer_food_category(name: str) -> tuple[str, str]:
    for category, keywords in CATEGORY_RULES:
        if has_any(name, keywords):
            return category, "keyword"
    return "lainnya", "fallback"


def infer_base_ingredient(name: str) -> tuple[str, str]:
    matches = [ingredient for ingredient, keywords in BASE_INGREDIENT_RULES if has_any(name, keywords)]
    if matches:
        return matches[0], "|".join(matches)
    return "unknown", ""


def category_from_recipe_text(text: str) -> str | None:
    if has_any(text, ["kuah", "sop", "sup", "soto", "rawon", "gulai", "lodeh", "opor", "laksa", "kaldu", "kari", "semur"]):
        return "berkuah"
    if has_any(text, ["goreng", "fried", "air fryer", "deep fried", "crispy"]):
        return "gorengan"
    if has_any(text, ["salad", "sayur", "vegetable", "vegetables", "veggie", "spinach", "broccoli"]):
        return "sayuran"
    if has_any(text, ["juice", "smoothie", "tea", "coffee", "drink", "beverage", "susu", "teh", "kopi"]):
        return "minuman"
    if has_any(text, ["cake", "cookie", "dessert", "pudding", "sweet", "kue", "puding"]):
        return "snack_dessert"
    if has_any(text, ["rice", "noodle", "pasta", "bread", "potato", "nasi", "mie", "roti", "kentang"]):
        return "karbohidrat_pokok"
    return None


def meal_type_to_primary(value: object) -> str | None:
    meal_type = normalize_text(value)
    if "breakfast" in meal_type:
        return "breakfast"
    if "dinner" in meal_type:
        return "dinner"
    if "lunch" in meal_type:
        return "lunch"
    return None


def normalize_main_ingredient(value: object) -> str:
    ingredient = normalize_base_category(value)
    mapping = {
        "other": "unknown",
        "terigu": "gandum",
        "babi": "daging_lain",
    }
    return mapping.get(ingredient, ingredient)


def parse_meal_time_tags(value: object) -> list[str]:
    text = normalize_text(value).replace("-", " ")
    tags = []
    for tag in ["breakfast", "lunch", "dinner"]:
        if tag in text:
            tags.append(tag)
    return tags


def primary_from_tags(tags: list[str]) -> str | None:
    if not tags:
        return None
    if tags == ["breakfast"]:
        return "breakfast"
    if tags == ["dinner"]:
        return "dinner"
    if "lunch" in tags:
        return "lunch"
    if "breakfast" in tags:
        return "breakfast"
    return tags[0]


def make_recipe_record(title: object, source: str, category: object = "", ingredients: object = "", meal_type: object = "") -> dict[str, object] | None:
    clean_title = normalize_text(title)
    if not clean_title:
        return None

    base = normalize_base_category(category)
    text = normalize_text(f"{title} {category} {ingredients}")
    food_category = category_from_recipe_text(text)
    inferred_base, base_tags = infer_base_ingredient(text)

    if base in {"ayam", "sapi", "kambing", "ikan", "seafood", "kedelai", "telur"}:
        inferred_base = base
        base_tags = base

    return {
        "recipe_title_clean": clean_title,
        "recipe_source": source,
        "recipe_category": normalize_text(category),
        "recipe_food_category": food_category,
        "recipe_base_ingredient": inferred_base,
        "recipe_base_ingredient_tags": base_tags,
        "recipe_primary_meal_time": meal_type_to_primary(meal_type),
        "recipe_ingredients_clean": normalize_text(ingredients)[:500],
    }


def load_recipe_references() -> dict[str, dict[str, object]]:
    records: list[dict[str, object]] = []

    indonesian_recipe_path = RECIPE_ARCHIVE_DIR / "Indonesian_Food_Recipes.csv"
    if indonesian_recipe_path.exists():
        df = pd.read_csv(indonesian_recipe_path, usecols=lambda c: c in {"Title", "Category", "Ingredients Cleaned", "Ingredients"})
        for _, row in df.iterrows():
            record = make_recipe_record(
                title=row.get("Title", ""),
                source="indonesian_food_recipes",
                category=row.get("Category", ""),
                ingredients=row.get("Ingredients Cleaned", row.get("Ingredients", "")),
            )
            if record:
                records.append(record)

    if INDONESIAN_BY_BASE_DIR.exists():
        for recipe_path in sorted(INDONESIAN_BY_BASE_DIR.glob("dataset-*.csv")):
            base_category = recipe_path.stem.replace("dataset-", "")
            df = pd.read_csv(recipe_path, usecols=lambda c: c in {"Title", "Ingredients"}, encoding_errors="ignore")
            for _, row in df.iterrows():
                record = make_recipe_record(
                    title=row.get("Title", ""),
                    source=f"indonesian_recipe_by_base:{base_category}",
                    category=base_category,
                    ingredients=row.get("Ingredients", ""),
                )
                if record:
                    records.append(record)

    if MEAL_TYPE_REFERENCE_PATH.exists():
        df = pd.read_csv(MEAL_TYPE_REFERENCE_PATH, usecols=lambda c: c in {"Dish Name", "Cuisine", "Meal Type", "Tags"})
        for _, row in df.iterrows():
            record = make_recipe_record(
                title=row.get("Dish Name", ""),
                source="global_cuisine_meal_type",
                category=row.get("Cuisine", ""),
                ingredients=row.get("Tags", ""),
                meal_type=row.get("Meal Type", ""),
            )
            if record:
                records.append(record)

    if GLOBAL_RECIPE_REFERENCE_PATH.exists():
        df = pd.read_csv(GLOBAL_RECIPE_REFERENCE_PATH, usecols=lambda c: c in {"recipe_title", "category", "subcategory", "ingredients"})
        for _, row in df.iterrows():
            record = make_recipe_record(
                title=row.get("recipe_title", ""),
                source="recipes_64k",
                category=row.get("category", ""),
                ingredients=f"{row.get('subcategory', '')} {row.get('ingredients', '')}",
            )
            if record:
                records.append(record)

    reference: dict[str, dict[str, object]] = {}
    for record in records:
        title = str(record["recipe_title_clean"])
        existing = reference.get(title)
        if existing is None:
            reference[title] = record
        elif existing.get("recipe_source") == "recipes_64k" and record.get("recipe_source") != "recipes_64k":
            reference[title] = record
    return reference


def find_recipe_match(food_name_clean: str, recipe_reference: dict[str, dict[str, object]]) -> dict[str, object] | None:
    if food_name_clean in recipe_reference:
        return recipe_reference[food_name_clean]

    tokens = food_name_clean.split()
    if len(tokens) < 2 or len(food_name_clean) < 7:
        return None

    generic_ingredient_tokens = {
        "bawang",
        "daun",
        "cabe",
        "cabai",
        "garam",
        "gula",
        "lada",
        "merica",
        "jahe",
        "kunyit",
        "lengkuas",
        "sereh",
        "serai",
        "kemiri",
    }
    if any(token in generic_ingredient_tokens for token in tokens):
        return None

    max_ngram = min(5, len(tokens))
    for ngram_size in range(max_ngram, 1, -1):
        for start in range(0, len(tokens) - ngram_size + 1):
            candidate = " ".join(tokens[start : start + ngram_size])
            if candidate in recipe_reference:
                return recipe_reference[candidate]
    return None


def infer_meal_time(row: pd.Series) -> tuple[bool, bool, bool, str, str]:
    name = row["food_name_clean"]
    category = row["food_category"]
    calories = float(row.get("calories_100g", 0) or 0)
    fat = float(row.get("fat_100g", 0) or 0)

    breakfast = False
    lunch = False
    dinner = False

    if category in {"buah", "minuman", "snack_dessert"} and calories <= 450:
        breakfast = True
    if has_any(name, ["bubur", "roti", "telur", "susu", "pisang", "apel", "oat"]):
        breakfast = True
    if category == "karbohidrat_pokok" and calories <= 450:
        breakfast = True

    if category in {"karbohidrat_pokok", "lauk_hewani", "lauk_nabati", "sayuran", "berkuah", "gorengan"}:
        lunch = True
    if 120 <= calories <= 750:
        lunch = True

    if category in {"berkuah", "sayuran", "lauk_hewani", "lauk_nabati"} and calories <= 650:
        dinner = True
    if category == "karbohidrat_pokok" and calories <= 400 and fat <= 20:
        dinner = True

    if not (breakfast or lunch or dinner):
        lunch = True

    tags = []
    if breakfast:
        tags.append("breakfast")
    if lunch:
        tags.append("lunch")
    if dinner:
        tags.append("dinner")

    if breakfast and category in {"buah", "minuman", "snack_dessert"}:
        primary = "breakfast"
    elif breakfast and has_any(name, ["bubur", "roti", "telur", "susu", "oat"]):
        primary = "breakfast"
    elif dinner and category in {"berkuah", "sayuran"}:
        primary = "dinner"
    elif lunch:
        primary = "lunch"
    elif dinner:
        primary = "dinner"
    else:
        primary = "breakfast"

    return breakfast, lunch, dinner, "|".join(tags), primary


def enrich_dataset(path: Path = DATASET_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)
    stale_columns = [
        col
        for col in df.columns
        if col in ADDED_COLUMNS or any(col.startswith(f"{added_col}.") for added_col in ADDED_COLUMNS)
    ]
    df = df.drop(columns=stale_columns)
    df["food_name_clean"] = df["food_name_clean"].fillna(df["food_name"].map(normalize_text))
    recipe_reference = load_recipe_references()
    recipe_matches = df["food_name_clean"].map(lambda name: find_recipe_match(str(name), recipe_reference))

    category_results = df["food_name_clean"].map(infer_food_category)
    df["food_category"] = category_results.map(lambda item: item[0])
    df["food_category_source"] = category_results.map(lambda item: item[1])

    base_results = df["food_name_clean"].map(infer_base_ingredient)
    df["base_ingredient"] = base_results.map(lambda item: item[0])
    df["base_ingredient_tags"] = base_results.map(lambda item: item[1])

    if "main_ingredient" in df.columns:
        normalized_main = df["main_ingredient"].map(normalize_main_ingredient)
        has_main = normalized_main.ne("unknown") & normalized_main.ne("")
        df.loc[has_main, "base_ingredient"] = normalized_main[has_main]
        df.loc[has_main, "base_ingredient_tags"] = normalized_main[has_main]

    if "cooking_category" in df.columns:
        normalized_cooking = df["cooking_category"].map(normalize_text)
        strong_cooking = normalized_cooking.isin(["gorengan", "berkuah", "tumis", "bakar", "rebus_kukus"])
        replace_category = strong_cooking & (
            df["food_category"].eq("lainnya") | normalized_cooking.isin(["gorengan", "berkuah"])
        )
        df.loc[replace_category, "food_category"] = normalized_cooking[replace_category]
        df.loc[replace_category, "food_category_source"] = "orang_a_cooking_category"

    df["recipe_reference_match"] = recipe_matches.map(lambda item: bool(item))
    df["recipe_reference_source"] = recipe_matches.map(lambda item: item.get("recipe_source", "") if item else "")
    df["recipe_reference_title"] = recipe_matches.map(lambda item: item.get("recipe_title_clean", "") if item else "")
    df["recipe_ingredients_reference"] = recipe_matches.map(lambda item: item.get("recipe_ingredients_clean", "") if item else "")

    for idx, match in recipe_matches.items():
        if not match:
            continue
        recipe_category = match.get("recipe_food_category")
        recipe_base = match.get("recipe_base_ingredient")
        recipe_base_tags = match.get("recipe_base_ingredient_tags", "")
        if recipe_category and df.at[idx, "food_category"] == "lainnya":
            df.at[idx, "food_category"] = recipe_category
            df.at[idx, "food_category_source"] = "recipe_reference"
        if recipe_base and recipe_base != "unknown":
            df.at[idx, "base_ingredient"] = recipe_base
            df.at[idx, "base_ingredient_tags"] = recipe_base_tags

    meal_results = df.apply(infer_meal_time, axis=1, result_type="expand")
    meal_results.columns = [
        "suitable_breakfast",
        "suitable_lunch",
        "suitable_dinner",
        "meal_time_tags",
        "primary_meal_time",
    ]
    df = pd.concat([df, meal_results], axis=1)

    for idx, match in recipe_matches.items():
        if not match:
            continue
        recipe_meal = match.get("recipe_primary_meal_time")
        if recipe_meal in {"breakfast", "lunch", "dinner"}:
            df.at[idx, f"suitable_{recipe_meal}"] = True
            tags = set(str(df.at[idx, "meal_time_tags"]).split("|"))
            tags.add(recipe_meal)
            df.at[idx, "meal_time_tags"] = "|".join(tag for tag in ["breakfast", "lunch", "dinner"] if tag in tags)
            df.at[idx, "primary_meal_time"] = recipe_meal

    if "meal_time" in df.columns:
        for idx, raw_meal_time in df["meal_time"].items():
            tags = parse_meal_time_tags(raw_meal_time)
            if not tags:
                continue
            for tag in tags:
                df.at[idx, f"suitable_{tag}"] = True
            existing_tags = set(str(df.at[idx, "meal_time_tags"]).split("|"))
            existing_tags.update(tags)
            df.at[idx, "meal_time_tags"] = "|".join(tag for tag in ["breakfast", "lunch", "dinner"] if tag in existing_tags)
            primary = primary_from_tags(tags)
            if primary and len(tags) == 1:
                df.at[idx, "primary_meal_time"] = primary

    df["feature_rule_version"] = "food_context_rules_v1"

    df.to_csv(path, index=False)
    return df


def write_summary(df: pd.DataFrame) -> None:
    rows = []
    for column in ["food_category", "base_ingredient", "primary_meal_time"]:
        counts = df[column].value_counts(dropna=False)
        for value, count in counts.items():
            rows.append({"feature": column, "value": value, "count": int(count)})
    for column in ["suitable_breakfast", "suitable_lunch", "suitable_dinner"]:
        rows.append({"feature": column, "value": "true", "count": int(df[column].sum())})
    rows.append({"feature": "recipe_reference_match", "value": "true", "count": int(df["recipe_reference_match"].sum())})
    pd.DataFrame(rows).to_csv(SUMMARY_PATH, index=False)

    metadata = {
        "rule_version": "food_context_rules_v1",
        "dataset_path": str(DATASET_PATH),
        "rows": int(len(df)),
        "added_columns": ADDED_COLUMNS,
        "notes": [
            "Features are rule-based and intended to improve recommendation diversity.",
            "When available, Orang A columns cooking_category, main_ingredient, and meal_time are used as stronger context signals.",
            "Recipe references from Dataset/archive through Dataset/archive (3) are used when title matching is available.",
            "Meal time is represented as both multilabel booleans and a primary class.",
            "contains_unknown should still be used as an allergy safety guardrail.",
        ],
    }
    METADATA_PATH.write_text(json.dumps(metadata, indent=2), encoding="utf-8")


if __name__ == "__main__":
    enriched = enrich_dataset()
    write_summary(enriched)
    print(f"Updated: {DATASET_PATH}")
    print(f"Rows: {len(enriched)}")
    print(f"Summary: {SUMMARY_PATH}")
    print(f"Metadata: {METADATA_PATH}")
