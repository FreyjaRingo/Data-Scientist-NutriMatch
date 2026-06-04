from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = PROJECT_ROOT.parent
FINAL_DIR = PROJECT_ROOT / "final_datasets"
TRAIN_READY_PATH = FINAL_DIR / "train_ready_dataset.csv"
FULL_AUDIT_PATH = FINAL_DIR / "train_ready_dataset_full_audit.csv"
SUMMARY_PATH = FINAL_DIR / "menu_ready_filter_summary.csv"
METADATA_PATH = FINAL_DIR / "menu_ready_filter_metadata.json"
NEW_DATASET_DIR = WORKSPACE_ROOT / "new datasets"

RULE_VERSION = "menu_ready_filter_v1"

MENU_COLUMNS = [
    "context_correction_notes",
    "menu_reference_match",
    "menu_reference_source",
    "menu_reference_title",
    "menu_reference_category",
    "menu_reference_meal_time",
    "ingredient_only_flag",
    "raw_ingredient_flag",
    "is_recommendable_food",
    "recommendation_item_type",
    "recommendation_confidence",
    "recommendation_exclusion_reason",
    "halal_status",
    "is_halal_candidate",
    "contains_non_halal_ingredient",
    "non_halal_ingredient_tags",
    "halal_review_reason",
    "halal_confidence",
    "halal_rule_version",
    "menu_ready_rule_version",
]

PREPARED_COOKING_CATEGORIES = {"olahan", "gorengan", "berkuah", "tumis", "bakar", "rebus_kukus"}
DIRECT_ALLOW_CATEGORIES = {"buah", "sayuran", "snack_dessert", "minuman", "gorengan", "berkuah"}
PROTEIN_CATEGORIES = {"lauk_hewani", "lauk_nabati"}
STAPLE_BASES = {"beras", "gandum", "umbi", "jagung", "singkong"}
ANIMAL_BASES = {"ayam", "sapi", "kambing", "ikan", "seafood", "telur", "daging_lain", "unggas_lain"}

HALAL_RULE_VERSION = "halal_context_rules_v1"

NON_HALAL_RULES: list[tuple[str, list[str]]] = [
    ("pork", ["babi", "pork", "bacon", "lard", "prosciutto"]),
    ("processed_pork", ["ham"]),
    ("dog", ["anjing", "dog"]),
    ("alcohol", ["alkohol", "bir", "beer", "wine", "arak", "mirin", "sake", "rum", "vodka", "whisky", "brandy", "tuak"]),
]

HALAL_REVIEW_RULES: list[tuple[str, list[str]]] = [
    ("exotic_or_sensitive_animal", ["paniki", "penyu", "buaya", "katak", "kura-kura", "kura kura", "biawak", "ular", "kelelawar", "bekicot", "keong"]),
]

NON_HALAL_FALSE_POSITIVE_PHRASES = [
    "kacang babi",
]

INGREDIENT_ONLY_PHRASES = [
    "asam gelugur",
    "asam jawa",
    "daun salam",
    "daun jeruk",
    "daun pandan",
    "encung asam",
    "kaldu bubuk",
    "santan dengan air",
    "santan kelapa",
    "santan murni",
    "asam kandis",
    "asam payak",
    "tepung beras",
    "tepung jagung",
    "tepung sagu",
    "tepung tapioka",
    "tepung terigu",
    "minyak goreng",
    "bawang goreng",
]

INGREDIENT_ONLY_KEYWORDS = [
    "andaliman",
    "bawang",
    "bumbu",
    "cabai",
    "cabe",
    "cengkeh",
    "cuka",
    "garam",
    "gula",
    "jahe",
    "kapulaga",
    "kayu manis",
    "kecap",
    "kemiri",
    "kencur",
    "ketumbar",
    "kunyit",
    "lada",
    "lengkuas",
    "lemak",
    "margarin",
    "merica",
    "minyak",
    "msg",
    "pala",
    "pati",
    "penyedap",
    "ragi",
    "rempah",
    "sambal",
    "saus",
    "serai",
    "sereh",
    "terasi",
    "tepung",
    "vanili",
]

BYPRODUCT_KEYWORDS = ["ampas", "bungkil"]
RAW_MARKERS = ["mentah", "segar", "kering", "bubuk"]

INGREDIENT_ONLY_PREFIXES = [
    "asam ",
    "bawang ",
    "bumbu ",
    "cabai ",
    "cabe ",
    "garam ",
    "gula ",
    "kecap ",
    "minyak ",
    "santan ",
    "saus ",
    "tepung ",
]

PREPARED_KEYWORDS = [
    "acar",
    "abon",
    "asinan",
    "bakso",
    "bakar",
    "balado",
    "barongko",
    "bebek betutu",
    "bekasam",
    "bekasang",
    "bika",
    "botok",
    "brongkos",
    "burger",
    "buntil",
    "cake",
    "chicken teriyaki",
    "coto",
    "dadar",
    "dendeng",
    "dodol",
    "es krim",
    "gado-gado",
    "goreng",
    "gulai",
    "kari",
    "keripik",
    "kerupuk",
    "kornet",
    "kue",
    "kukus",
    "lodeh",
    "masak",
    "masakan",
    "matang",
    "mie",
    "mi ",
    "nasi",
    "opor",
    "panggang",
    "pecel",
    "pepes",
    "perkedel",
    "pindang",
    "rawon",
    "rebus",
    "rendang",
    "rica",
    "roti",
    "sate",
    "semur",
    "sop",
    "sosis",
    "soto",
    "sup",
    "tumis",
]

SNACK_KEYWORDS = [
    "agar-agar",
    "bagea",
    "baje",
    "bakpia",
    "barongko",
    "biskuit",
    "bolu",
    "cake",
    "cemilan",
    "cokelat",
    "coklat",
    "dodol",
    "enting-enting",
    "es krim",
    "gemblong",
    "keripik",
    "kerupuk",
    "kue",
    "permen",
    "snack",
    "wafer",
]

ANIMAL_RAW_KEYWORDS = [
    "ayam",
    "babi",
    "bebek",
    "daging",
    "ginjal",
    "hati",
    "ikan",
    "kambing",
    "kerang",
    "limpa",
    "paru",
    "sapi",
    "telur",
    "udang",
    "usus",
]

STAPLE_RAW_KEYWORDS = ["beras", "bihun", "mie", "mi", "jagung", "ketan", "pati", "tepung"]

FRUIT_KEYWORDS = [
    "alpukat",
    "anggur",
    "apel",
    "arbei",
    "belimbing",
    "bengkuang",
    "biwah",
    "buah",
    "carica",
    "cempedak",
    "duku",
    "durian",
    "duwet",
    "erbis",
    "gandaria",
    "jambu",
    "jeruk",
    "kelapa",
    "mangga",
    "markisa",
    "melon",
    "nanas",
    "nangka",
    "papaya",
    "pepaya",
    "pisang",
    "rambutan",
    "salak",
    "semangka",
    "sirsak",
    "stroberi",
]

VEGETABLE_KEYWORDS = [
    "andewi",
    "bayam",
    "brokoli",
    "buncis",
    "bunga pepaya",
    "bunga turi",
    "caisin",
    "daun katuk",
    "daun kelor",
    "daun pepaya",
    "daun singkong",
    "genjer",
    "gambas",
    "kangkung",
    "kacang panjang",
    "kol",
    "kubis",
    "labu",
    "oyong",
    "pakis",
    "pare",
    "rebung",
    "sawi",
    "sayur",
    "selada",
    "taoge",
    "tauge",
    "terong",
    "terung",
    "timun",
    "tomat",
    "wortel",
]

GENERIC_MATCH_TOKENS = {
    "bawang",
    "cabai",
    "cabe",
    "daun",
    "garam",
    "gula",
    "jahe",
    "kemiri",
    "kunyit",
    "lada",
    "lengkuas",
    "merica",
    "sereh",
    "serai",
}


def normalize_text(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).lower()
    text = re.sub(r"[^a-z0-9\s_-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def has_any(text: str, keywords: list[str] | set[str]) -> bool:
    padded = f" {text} "
    return any(re.search(r"(?<![a-z0-9])" + re.escape(keyword) + r"(?![a-z0-9])", padded) for keyword in keywords)


def phrase_has_any(text: str, phrases: list[str]) -> bool:
    return any(phrase in text for phrase in phrases)


def first_non_empty(*values: object) -> str:
    for value in values:
        text = normalize_text(value)
        if text:
            return text
    return ""


def infer_meal_time(value: object) -> str:
    text = normalize_text(value)
    if "breakfast" in text or "sarapan" in text:
        return "breakfast"
    if "dinner" in text or "malam" in text:
        return "dinner"
    if "lunch" in text or "main course" in text or "siang" in text:
        return "lunch"
    return ""


def infer_reference_category(text: str) -> str:
    if has_any(text, ["breakfast", "dessert", "snack", "cake", "cookie", "kue", "sweet"]):
        return "snack_dessert"
    if has_any(text, ["soup", "stew", "curry", "soto", "sop", "sup", "gulai", "kuah"]):
        return "berkuah"
    if has_any(text, ["fried", "goreng", "crispy", "fritter"]):
        return "gorengan"
    if has_any(text, ["salad", "vegetable", "vegetables", "veggie", "sayur"]):
        return "sayuran"
    if has_any(text, ["rice", "biryani", "noodle", "pasta", "bread", "nasi", "mie", "roti"]):
        return "karbohidrat_pokok"
    if has_any(text, ["drink", "beverage", "juice", "smoothie", "tea", "coffee"]):
        return "minuman"
    return "menu"


def make_reference_record(
    title: object,
    source: str,
    category: object = "",
    ingredients: object = "",
    meal_time: object = "",
) -> dict[str, str] | None:
    title_clean = normalize_text(title)
    if not title_clean:
        return None

    context = normalize_text(f"{title} {category} {ingredients} {meal_time}")
    return {
        "title_clean": title_clean,
        "source": source,
        "category": normalize_text(category),
        "reference_category": infer_reference_category(context),
        "meal_time": infer_meal_time(first_non_empty(meal_time, category)),
    }


def add_reference(records: list[dict[str, str]], record: dict[str, str] | None) -> None:
    if record:
        records.append(record)


def load_menu_references() -> dict[str, dict[str, str]]:
    records: list[dict[str, str]] = []

    multi_cuisine_path = NEW_DATASET_DIR / "extracted" / "archive (1)" / "Multi_Cuisine_Recipe_Dataset.csv"
    if multi_cuisine_path.exists():
        df = pd.read_csv(
            multi_cuisine_path,
            usecols=lambda col: col in {"name", "area", "category", "ingredients"},
            encoding_errors="ignore",
        )
        for _, row in df.iterrows():
            add_reference(
                records,
                make_reference_record(
                    title=row.get("name", ""),
                    source="new_multi_cuisine_recipe",
                    category=f"{row.get('area', '')} {row.get('category', '')}",
                    ingredients=row.get("ingredients", ""),
                ),
            )

    recipe_master_path = NEW_DATASET_DIR / "extracted" / "archive (2)" / "recipes_master.csv"
    recipe_ingredients_path = NEW_DATASET_DIR / "extracted" / "archive (2)" / "recipe_ingredients.csv"
    if recipe_master_path.exists():
        master = pd.read_csv(
            recipe_master_path,
            usecols=lambda col: col
            in {"recipe_id", "recipe_name", "cuisine", "category", "cooking_method", "meal_type"},
            encoding_errors="ignore",
        )
        if recipe_ingredients_path.exists():
            ingredients = pd.read_csv(
                recipe_ingredients_path,
                usecols=lambda col: col in {"recipe_id", "ingredient_name", "category"},
                encoding_errors="ignore",
            )
            ingredients["ingredient_text"] = ingredients[["ingredient_name", "category"]].fillna("").agg(" ".join, axis=1)
            ingredient_lookup = ingredients.groupby("recipe_id")["ingredient_text"].apply(lambda values: " ".join(values)).to_dict()
        else:
            ingredient_lookup = {}

        for _, row in master.iterrows():
            add_reference(
                records,
                make_reference_record(
                    title=row.get("recipe_name", ""),
                    source="new_recipe_master",
                    category=f"{row.get('cuisine', '')} {row.get('category', '')} {row.get('cooking_method', '')}",
                    ingredients=ingredient_lookup.get(row.get("recipe_id", ""), ""),
                    meal_time=row.get("meal_type", ""),
                ),
            )

    for nutrition_path in [
        NEW_DATASET_DIR / "extracted" / "archive (4)" / "NutritionalFacts_Fruit_Vegetables_Seafood.csv",
        NEW_DATASET_DIR / "extracted" / "archive (5)" / "NutritionalFacts_Fruit_Vegetables_Seafood.csv",
    ]:
        if not nutrition_path.exists():
            continue
        df = pd.read_csv(
            nutrition_path,
            usecols=lambda col: col in {"Food and Serving", "Food Type"},
            encoding_errors="ignore",
        )
        for _, row in df.dropna(subset=["Food and Serving"]).iterrows():
            food_name = str(row.get("Food and Serving", "")).split(",")[0]
            add_reference(
                records,
                make_reference_record(
                    title=food_name,
                    source="new_fruit_vegetable_seafood_nutrition",
                    category=row.get("Food Type", ""),
                ),
            )

    reference: dict[str, dict[str, str]] = {}
    for record in records:
        title = record["title_clean"]
        if title and title not in reference:
            reference[title] = record
    return reference


def find_menu_reference(food_name_clean: str, reference: dict[str, dict[str, str]]) -> dict[str, str] | None:
    if food_name_clean in reference:
        return reference[food_name_clean]

    tokens = food_name_clean.split()
    if len(tokens) < 2 or len(food_name_clean) < 7:
        return None
    if any(token in GENERIC_MATCH_TOKENS for token in tokens):
        return None

    max_ngram = min(5, len(tokens))
    for ngram_size in range(max_ngram, 1, -1):
        for start in range(0, len(tokens) - ngram_size + 1):
            candidate = " ".join(tokens[start : start + ngram_size])
            if candidate in reference:
                return reference[candidate]
    return None


def is_fruit(name: str, category: str, base: str) -> bool:
    if category == "sayuran":
        return False
    if has_any(name, ["bunga", "daun", "jantung"]) and is_vegetable(name, category, base):
        return False
    return category == "buah" or base == "buah" or has_any(name, FRUIT_KEYWORDS)


def is_vegetable(name: str, category: str, base: str) -> bool:
    return category == "sayuran" or base == "sayuran" or has_any(name, VEGETABLE_KEYWORDS)


def has_prepared_context(name: str, cooking: str = "") -> bool:
    return cooking in PREPARED_COOKING_CATEGORIES or has_any(name, PREPARED_KEYWORDS)


def is_hard_ingredient_name(name: str) -> bool:
    return (
        phrase_has_any(name, INGREDIENT_ONLY_PHRASES)
        or has_any(name, INGREDIENT_ONLY_KEYWORDS)
        or any(name.startswith(prefix) for prefix in INGREDIENT_ONLY_PREFIXES)
        or has_any(name, BYPRODUCT_KEYWORDS)
    )


def halal_text_for_matching(row: pd.Series) -> str:
    return normalize_text(
        " ".join(
            str(row.get(column, ""))
            for column in [
                "food_name",
                "food_name_clean",
                "food_category",
                "base_ingredient",
                "recipe_ingredients_reference",
            ]
        )
    )


def collect_halal_rule_tags(text: str, rules: list[tuple[str, list[str]]]) -> list[str]:
    clean_text = text
    for phrase in NON_HALAL_FALSE_POSITIVE_PHRASES:
        clean_text = clean_text.replace(phrase, " ")
    tags = [tag for tag, keywords in rules if has_any(clean_text, keywords)]
    return tags


def classify_halal_status(row: pd.Series) -> tuple[str, bool, bool, str, str, str, str]:
    text = halal_text_for_matching(row)
    non_halal_tags = collect_halal_rule_tags(text, NON_HALAL_RULES)
    if non_halal_tags:
        return (
            "non_halal",
            False,
            True,
            "|".join(non_halal_tags),
            "explicit_non_halal_keyword",
            "high",
            HALAL_RULE_VERSION,
        )

    review_tags = collect_halal_rule_tags(text, HALAL_REVIEW_RULES)
    if review_tags:
        return (
            "needs_review",
            False,
            False,
            "",
            "|".join(review_tags),
            "medium",
            HALAL_RULE_VERSION,
        )

    return (
        "halal_candidate",
        True,
        False,
        "",
        "",
        "medium",
        HALAL_RULE_VERSION,
    )


def is_ingredient_only(name: str, category: str, base: str) -> bool:
    hard_ingredient = is_hard_ingredient_name(name)
    if category == "bumbu_sambal" and not (has_prepared_context(name) and not hard_ingredient):
        return True
    return hard_ingredient


def is_raw_ingredient(name: str, category: str, base: str, cooking: str) -> bool:
    if has_any(name, ANIMAL_RAW_KEYWORDS) and has_any(name, ["mentah", "segar", "bubuk"]):
        return True
    if has_any(name, STAPLE_RAW_KEYWORDS) and (has_any(name, ["mentah", "bubuk"]) or "kering mentah" in name):
        return True
    if is_fruit(name, category, base) or is_vegetable(name, category, base):
        return False
    if cooking == "mentah_segar":
        return True
    if has_any(name, ["mentah", "bubuk"]):
        return True
    if has_any(name, ["segar", "kering"]) and (base in ANIMAL_BASES or base in STAPLE_BASES or category == "lainnya"):
        return True
    return False


def classify_row(row: pd.Series) -> tuple[bool, str, str, str]:
    name = normalize_text(row.get("food_name_clean", row.get("food_name", "")))
    category = normalize_text(row.get("food_category", ""))
    base = normalize_text(row.get("base_ingredient", ""))
    cooking = normalize_text(row.get("cooking_category", ""))
    recipe_match = bool(row.get("recipe_reference_match", False))
    menu_match = bool(row.get("menu_reference_match", False))
    ingredient_flag = bool(row.get("ingredient_only_flag", False))
    raw_flag = bool(row.get("raw_ingredient_flag", False))

    if ingredient_flag:
        return False, "ingredient_only", "high", "bumbu_condiment_or_raw_component"
    if raw_flag:
        return False, "raw_ingredient", "high", "raw_or_unprepared_component"

    if category == "minuman" or has_any(name, ["air", "jus", "teh", "kopi", "susu", "es "]):
        return True, "drink", "high", ""
    if category == "snack_dessert" or has_any(name, SNACK_KEYWORDS):
        return True, "snack", "high", ""
    if category in {"gorengan", "berkuah"} or cooking in PREPARED_COOKING_CATEGORIES:
        return True, "menu", "high", ""
    if recipe_match or menu_match:
        return True, "menu", "high", ""
    if is_vegetable(name, category, base):
        return True, "vegetable", "high", ""
    if is_fruit(name, category, base):
        return True, "fruit", "high", ""
    if category in PROTEIN_CATEGORIES and base in {"kedelai", "kacang"}:
        return True, "plant_protein", "medium", ""
    if category in PROTEIN_CATEGORIES and base in ANIMAL_BASES:
        return True, "protein_dish", "medium", ""
    if category == "karbohidrat_pokok" or base in STAPLE_BASES:
        if has_any(name, ["beras", "tepung", "pati"]) and not has_any(name, PREPARED_KEYWORDS):
            return False, "raw_staple", "high", "uncooked_staple_or_flour"
        return True, "staple", "medium", ""
    if category in DIRECT_ALLOW_CATEGORIES:
        return True, category, "medium", ""
    if has_any(name, PREPARED_KEYWORDS):
        return True, "menu", "medium", ""

    return True, "local_food_or_menu", "low", ""


def load_candidate_dataset() -> pd.DataFrame:
    if FULL_AUDIT_PATH.exists():
        audit_df = pd.read_csv(FULL_AUDIT_PATH)
        train_df = pd.read_csv(TRAIN_READY_PATH)
        if len(audit_df) >= len(train_df) and "menu_ready_rule_version" in audit_df.columns:
            return audit_df
    return pd.read_csv(TRAIN_READY_PATH)


def apply_context_corrections(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    notes = pd.Series("", index=df.index, dtype="object")

    if "food_name_clean" not in df.columns:
        df["food_name_clean"] = df["food_name"].map(normalize_text)
    else:
        df["food_name_clean"] = df["food_name_clean"].fillna(df["food_name"].map(normalize_text))

    names = df["food_name_clean"].map(normalize_text)
    category = df.get("food_category", pd.Series("", index=df.index)).map(normalize_text)
    base = df.get("base_ingredient", pd.Series("", index=df.index)).map(normalize_text)
    cooking = df.get("cooking_category", pd.Series("", index=df.index)).map(normalize_text)

    animal_base_rules = [
        ("ayam", ["ayam"]),
        ("sapi", ["sapi", "daging sapi"]),
        ("kambing", ["kambing", "domba"]),
        ("daging_lain", ["babi"]),
        ("ikan", ["ikan", "belut", "bandeng", "lele", "tongkol", "tuna", "teri", "kembung", "gabus", "patin", "nila", "gurame", "mujair", "kakap"]),
        ("seafood", ["udang", "cumi", "kepiting", "kerang", "teripang"]),
        ("telur", ["telur"]),
    ]
    for base_value, keywords in animal_base_rules:
        mask = names.map(lambda value, keys=keywords: has_any(value, keys))
        df.loc[mask, "base_ingredient"] = base_value
        df.loc[mask, "food_category"] = "lauk_hewani"
        notes.loc[mask] = notes.loc[mask].map(lambda value, item=base_value: f"{value}|animal_base_{item}".strip("|"))

    kacang_babi_mask = names.map(lambda value: phrase_has_any(value, NON_HALAL_FALSE_POSITIVE_PHRASES))
    df.loc[kacang_babi_mask, "base_ingredient"] = "kacang"
    df.loc[kacang_babi_mask, "food_category"] = "lauk_nabati"
    notes.loc[kacang_babi_mask] = notes.loc[kacang_babi_mask].map(
        lambda value: f"{value}|kacang_babi_legume_exception".strip("|")
    )

    rice_mask = names.map(lambda value: has_any(value, ["beras", "bihun", "ketan", "lontong", "ketupat", "bubur", "nasi"]))
    df.loc[rice_mask, "base_ingredient"] = "beras"
    df.loc[rice_mask, "food_category"] = "karbohidrat_pokok"
    notes.loc[rice_mask] = notes.loc[rice_mask].map(lambda value: f"{value}|staple_keyword".strip("|"))

    category = df["food_category"].map(normalize_text)
    base = df["base_ingredient"].map(normalize_text)
    fruit_mask = [is_fruit(name, cat, ingredient) for name, cat, ingredient in zip(names, category, base)]
    vegetable_mask = [is_vegetable(name, cat, ingredient) for name, cat, ingredient in zip(names, category, base)]
    fruit_mask = pd.Series(fruit_mask, index=df.index)
    vegetable_mask = pd.Series(vegetable_mask, index=df.index)
    spice_leaf_mask = names.map(lambda value: phrase_has_any(value, ["daun salam", "daun jeruk", "daun pandan"]))

    df.loc[fruit_mask, "food_category"] = "buah"
    df.loc[fruit_mask, "base_ingredient"] = "buah"
    notes.loc[fruit_mask] = notes.loc[fruit_mask].map(lambda value: f"{value}|fruit_keyword".strip("|"))

    clean_vegetable_mask = vegetable_mask & ~spice_leaf_mask
    df.loc[clean_vegetable_mask, "food_category"] = "sayuran"
    df.loc[clean_vegetable_mask, "base_ingredient"] = "sayuran"
    notes.loc[clean_vegetable_mask] = notes.loc[clean_vegetable_mask].map(lambda value: f"{value}|vegetable_keyword".strip("|"))

    ingredient_mask = names.map(lambda value: is_ingredient_only(value, "", ""))
    prepared_mask = [
        has_prepared_context(name, cook) and not is_hard_ingredient_name(name)
        for name, cook in zip(names, cooking)
    ]
    prepared_mask = pd.Series(prepared_mask, index=df.index)
    df.loc[prepared_mask & df["food_category"].eq("bumbu_sambal"), "food_category"] = "lainnya"

    df.loc[ingredient_mask, "food_category"] = df.loc[ingredient_mask, "food_category"].where(
        df.loc[ingredient_mask, "food_category"].ne("lainnya"),
        "bumbu_sambal",
    )
    df.loc[ingredient_mask, "base_ingredient"] = df.loc[ingredient_mask, "base_ingredient"].where(
        df.loc[ingredient_mask, "base_ingredient"].ne("unknown"),
        "bumbu_rempah",
    )
    notes.loc[ingredient_mask] = notes.loc[ingredient_mask].map(lambda value: f"{value}|ingredient_keyword".strip("|"))

    df["context_correction_notes"] = notes
    return df


def add_menu_reference_columns(df: pd.DataFrame, reference: dict[str, dict[str, str]]) -> pd.DataFrame:
    matches = df["food_name_clean"].map(lambda value: find_menu_reference(str(value), reference))
    df["menu_reference_match"] = matches.map(lambda item: bool(item))
    df["menu_reference_source"] = matches.map(lambda item: item.get("source", "") if item else "")
    df["menu_reference_title"] = matches.map(lambda item: item.get("title_clean", "") if item else "")
    df["menu_reference_category"] = matches.map(lambda item: item.get("reference_category", "") if item else "")
    df["menu_reference_meal_time"] = matches.map(lambda item: item.get("meal_time", "") if item else "")

    for idx, match in matches.items():
        if not match:
            continue
        ref_category = match.get("reference_category", "")
        if ref_category and ref_category != "menu" and normalize_text(df.at[idx, "food_category"]) == "lainnya":
            df.at[idx, "food_category"] = ref_category
            note = str(df.at[idx, "context_correction_notes"])
            df.at[idx, "context_correction_notes"] = f"{note}|new_menu_reference_category".strip("|")

        meal = match.get("meal_time", "")
        if meal in {"breakfast", "lunch", "dinner"}:
            suitable_col = f"suitable_{meal}"
            if suitable_col in df.columns:
                df.at[idx, suitable_col] = True
            if "meal_time_tags" in df.columns:
                tags = set(str(df.at[idx, "meal_time_tags"]).split("|")) if str(df.at[idx, "meal_time_tags"]) else set()
                tags.add(meal)
                df.at[idx, "meal_time_tags"] = "|".join(tag for tag in ["breakfast", "lunch", "dinner"] if tag in tags)
            if "primary_meal_time" in df.columns and not str(df.at[idx, "primary_meal_time"]):
                df.at[idx, "primary_meal_time"] = meal
    return df


def build_menu_ready_dataset() -> pd.DataFrame:
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    df = load_candidate_dataset()
    stale_columns = [column for column in MENU_COLUMNS if column in df.columns]
    if stale_columns:
        df = df.drop(columns=stale_columns)

    df = apply_context_corrections(df)
    menu_reference = load_menu_references()
    df = add_menu_reference_columns(df, menu_reference)

    names = df["food_name_clean"].map(normalize_text)
    categories = df["food_category"].map(normalize_text)
    bases = df["base_ingredient"].map(normalize_text)
    cooking = df.get("cooking_category", pd.Series("", index=df.index)).map(normalize_text)

    df["ingredient_only_flag"] = [
        is_ingredient_only(name, category, base)
        for name, category, base in zip(names, categories, bases)
    ]
    df["raw_ingredient_flag"] = [
        is_raw_ingredient(name, category, base, cook)
        for name, category, base, cook in zip(names, categories, bases, cooking)
    ]

    classified = df.apply(classify_row, axis=1, result_type="expand")
    classified.columns = [
        "is_recommendable_food",
        "recommendation_item_type",
        "recommendation_confidence",
        "recommendation_exclusion_reason",
    ]
    df = pd.concat([df, classified], axis=1)

    halal_results = df.apply(classify_halal_status, axis=1, result_type="expand")
    halal_results.columns = [
        "halal_status",
        "is_halal_candidate",
        "contains_non_halal_ingredient",
        "non_halal_ingredient_tags",
        "halal_review_reason",
        "halal_confidence",
        "halal_rule_version",
    ]
    df = pd.concat([df, halal_results], axis=1)
    df["menu_ready_rule_version"] = RULE_VERSION

    df.to_csv(FULL_AUDIT_PATH, index=False)
    final_df = df[df["is_recommendable_food"]].copy()
    final_df.to_csv(TRAIN_READY_PATH, index=False)
    write_summary_and_metadata(df, final_df, menu_reference)
    return final_df


def source_file_status() -> list[dict[str, object]]:
    files = [
        NEW_DATASET_DIR / "extracted" / "archive (1)" / "Multi_Cuisine_Recipe_Dataset.csv",
        NEW_DATASET_DIR / "extracted" / "archive (2)" / "recipes_master.csv",
        NEW_DATASET_DIR / "extracted" / "archive (2)" / "recipe_ingredients.csv",
        NEW_DATASET_DIR / "extracted" / "archive (2)" / "recipe_nutrition.csv",
        NEW_DATASET_DIR / "extracted" / "archive (4)" / "NutritionalFacts_Fruit_Vegetables_Seafood.csv",
        NEW_DATASET_DIR / "dish_ingredients.csv",
        NEW_DATASET_DIR / "dish_nutrition_values.csv",
    ]
    return [
        {
            "path": str(path),
            "exists": path.exists(),
            "size_bytes": path.stat().st_size if path.exists() else 0,
        }
        for path in files
    ]


def write_summary_and_metadata(audit_df: pd.DataFrame, final_df: pd.DataFrame, menu_reference: dict[str, dict[str, str]]) -> None:
    rows = [
        {"metric": "rows_audit_all_items", "value": int(len(audit_df))},
        {"metric": "rows_train_ready_recommendable", "value": int(len(final_df))},
        {"metric": "rows_removed_not_recommendable", "value": int((~audit_df["is_recommendable_food"]).sum())},
        {"metric": "menu_reference_records_loaded", "value": int(len(menu_reference))},
        {"metric": "menu_reference_matches", "value": int(audit_df["menu_reference_match"].sum())},
    ]

    for value, count in audit_df["recommendation_item_type"].value_counts(dropna=False).items():
        rows.append({"metric": f"item_type:{value}", "value": int(count)})
    for value, count in audit_df["recommendation_exclusion_reason"].fillna("").replace("", "included").value_counts(dropna=False).items():
        rows.append({"metric": f"exclusion_reason:{value}", "value": int(count)})
    for value, count in final_df["halal_status"].value_counts(dropna=False).items():
        rows.append({"metric": f"halal_status_final:{value}", "value": int(count)})
    rows.append(
        {
            "metric": "contains_non_halal_ingredient_final",
            "value": int(final_df["contains_non_halal_ingredient"].sum()),
        }
    )
    pd.DataFrame(rows).to_csv(SUMMARY_PATH, index=False)

    metadata = {
        "rule_version": RULE_VERSION,
        "train_ready_dataset": str(TRAIN_READY_PATH),
        "full_audit_dataset": str(FULL_AUDIT_PATH),
        "summary": str(SUMMARY_PATH),
        "rows_audit_all_items": int(len(audit_df)),
        "rows_train_ready_recommendable": int(len(final_df)),
        "rows_removed_not_recommendable": int((~audit_df["is_recommendable_food"]).sum()),
        "new_dataset_sources_checked": source_file_status(),
        "notes": [
            "train_ready_dataset.csv is filtered to items suitable for recommendation: prepared menu items, fruits, vegetables, snacks, drinks, and edible staples.",
            "train_ready_dataset_full_audit.csv keeps all source rows with flags and exclusion reasons for reporting and review.",
            "New recipe datasets are used as menu-reference signals. They are not appended as new food rows because several sources do not share the same per-100g nutrition basis and some dish datasets do not include dish names.",
            "Raw ingredients, condiments, seasoning components, uncooked staples, and raw animal proteins are excluded from the main train-ready file.",
            "Halal status is rule-based from food names and ingredient text. halal_candidate is not a formal halal certification.",
            "non_halal marks explicit pork/dog/alcohol keywords. needs_review marks sensitive or uncommon animal items that should not be recommended in halal-only mode without manual review.",
        ],
        "added_columns": MENU_COLUMNS,
    }
    METADATA_PATH.write_text(json.dumps(metadata, indent=2), encoding="utf-8")


if __name__ == "__main__":
    result = build_menu_ready_dataset()
    print(f"Updated train ready dataset: {TRAIN_READY_PATH}")
    print(f"Rows: {len(result)}")
    print(f"Full audit dataset: {FULL_AUDIT_PATH}")
    print(f"Summary: {SUMMARY_PATH}")
    print(f"Metadata: {METADATA_PATH}")
