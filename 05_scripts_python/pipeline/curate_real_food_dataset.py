from __future__ import annotations

import re
import shutil
import json
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FINAL_DATASET_PATH = PROJECT_ROOT / "orang_b" / "final_datasets" / "train_ready_dataset.csv"
DASHBOARD_DATASET_PATH = PROJECT_ROOT / "streamlit_dashboard" / "data" / "train_ready_dataset.csv"
IMAGE_ACCESS_CHECK_PATH = PROJECT_ROOT / "streamlit_dashboard" / "data" / "image_access_check.csv"
IMAGE_ACCESS_SUMMARY_PATH = PROJECT_ROOT / "streamlit_dashboard" / "data" / "image_access_check_summary.json"

CURATION_SOURCE = "manual_real_food_curation_2026_06_04"
IMAGE_RULE_VERSION = "real_food_image_fix_v2"


IMAGE_REPLACEMENTS = {
    "beef burger": "https://commons.wikimedia.org/wiki/Special:FilePath/NCI%20Visuals%20Food%20Hamburger.jpg",
    "beef teriyaki masakan": "https://commons.wikimedia.org/wiki/Special:FilePath/Beef%20Teriyaki%20from%20Sarku%20Japan%20at%20the%20Natick%20Mall%2C%20Natick%20MA.jpg",
    "coto mangkasara kuda masakan": "https://commons.wikimedia.org/wiki/Special:FilePath/Coto%20makassar.jpg",
    "dendeng belut goreng": "https://commons.wikimedia.org/wiki/Special:FilePath/Dendeng%20balado.JPG",
    "empal daging goreng masakan": "https://commons.wikimedia.org/wiki/Special:FilePath/Empal%20Daging.jpg",
    "gulai kambing": "https://commons.wikimedia.org/wiki/Special:FilePath/Gulai%20tongseng%20kambing.JPG",
    "gulai pliek": "https://commons.wikimedia.org/wiki/Special:FilePath/Kuwah%20Pliek%20U.jpg",
    "ikan asar merah masakan": "https://commons.wikimedia.org/wiki/Special:FilePath/Cakalang%20fufu.JPG",
    "ikan baung bakar": "https://commons.wikimedia.org/wiki/Special:FilePath/Ikan%20Bakar.jpg",
    "ikan lais bakar": "https://commons.wikimedia.org/wiki/Special:FilePath/Ikan%20bakar.jpg",
    "ikan lele goreng": "https://commons.wikimedia.org/wiki/Special:FilePath/Lele%20Goreng.jpg",
    "ikan mujair goreng": "https://commons.wikimedia.org/wiki/Special:FilePath/Ikan%20Goreng.jpg",
    "soto dengan daging": "https://commons.wikimedia.org/wiki/Special:FilePath/SOTO%20BETAWI.jpg",
    "rawon masakan": "https://commons.wikimedia.org/wiki/Special:FilePath/Rawon%20Setan%20Surabaya.jpg",
    "soto bandung masakan": "https://commons.wikimedia.org/wiki/Special:FilePath/Soto%20Bandung.jpg",
    "soto betawi masakan": "https://commons.wikimedia.org/wiki/Special:FilePath/SOTO%20BETAWI.jpg",
    "sop buntut masakan": "https://commons.wikimedia.org/wiki/Special:FilePath/Sop%20Buntut%20Oxtail%20soup.jpg",
    "coto mangkasara sapi masakan": "https://commons.wikimedia.org/wiki/Special:FilePath/Coto%20makassar.jpg",
    "nasi campur bali": "https://commons.wikimedia.org/wiki/Special:FilePath/Nasi%20campur%20bali.jpg",
}


NAME_CORRECTIONS = {
    "abon haruwan": {
        "food_name": "abon ikan haruan",
        "main_ingredient": "ikan",
        "base_ingredient": "ikan",
        "base_ingredient_tags": "ikan",
        "context_correction_notes": "renamed_haruwan_to_haruan_and_corrected_fish_base",
    },
    "ayam goreng kentuckysayap": {"food_name": "ayam goreng tepung sayap"},
    "ayam goreng church texa sayap": {"food_name": "ayam goreng tepung sayap ala texas"},
    "ayam goreng church texas dada": {"food_name": "ayam goreng tepung dada ala texas"},
    "ayam goreng kentucky dada": {"food_name": "ayam goreng tepung dada"},
    "ayam goreng kentucky paha": {"food_name": "ayam goreng tepung paha"},
    "beef burger": {"food_name": "burger sapi"},
    "beef teriyaki masakan": {"food_name": "daging sapi teriyaki"},
    "beef yakiniku masakan": {"food_name": "daging sapi yakiniku"},
    "bulgogi masakan": {
        "food_name": "bulgogi sapi",
        "food_category": "lauk_hewani",
        "main_ingredient": "sapi",
        "base_ingredient": "sapi",
        "base_ingredient_tags": "sapi",
        "pairing_group": "traditional_protein",
        "pairing_role": "protein",
        "pairing_notes": "traditional_protein_for_rice_noodle",
        "pairing_suitability_notes": "main_meal_component",
        "meal_template_role": "protein",
        "context_correction_notes": "renamed_and_corrected_beef_bulgogi_base",
    },
    "chikiniku masakan": {
        "food_name": "chicken yakiniku",
        "food_category": "lauk_hewani",
        "main_ingredient": "ayam",
        "base_ingredient": "ayam",
        "base_ingredient_tags": "ayam",
        "pairing_group": "traditional_protein",
        "pairing_role": "protein",
        "pairing_notes": "traditional_protein_for_rice_noodle",
        "pairing_suitability_notes": "main_meal_component",
        "meal_template_role": "protein",
        "context_correction_notes": "renamed_and_corrected_chicken_yakiniku_base",
    },
    "coto mangkasara kuda masakan": {"food_name": "coto makassar kuda"},
    "coto mangkasara sapi masakan": {"food_name": "coto makassar sapi"},
    "dendeng mujahir goreng": {"food_name": "dendeng mujair goreng"},
    "mujahir acar kuning masakan": {"food_name": "mujair acar kuning"},
    "ikan mujair dendeng goreng": {"food_name": "dendeng ikan mujair goreng"},
    "empal daging goreng masakan": {"food_name": "empal daging sapi goreng"},
    "rawon masakan": {"food_name": "rawon daging sapi"},
    "rendang sapi masakan": {"food_name": "rendang sapi"},
    "sop buntut masakan": {"food_name": "sop buntut sapi"},
    "sop daging sapi masakan": {"food_name": "sop daging sapi"},
    "sop kaki sapi masakan": {"food_name": "sop kaki sapi"},
    "sop konro masakan": {"food_name": "sop konro"},
    "soto bandung masakan": {"food_name": "soto bandung"},
    "soto betawi masakan": {"food_name": "soto betawi"},
    "soto jeroan masakan": {"food_name": "soto jeroan sapi"},
    "soto padang masakan": {"food_name": "soto padang"},
    "soto sulung masakan": {"food_name": "soto sulung"},
    "sop kool": {"food_name": "sop kol"},
    "sop kool dan wortel": {"food_name": "sop kol dan wortel"},
    "keju": {
        "food_name": "keju cheddar",
        "ingredient_only_flag": "True",
        "is_recommendable_food": "False",
        "recommendation_exclusion_reason": "ingredient_or_topping_not_menu",
        "recommendation_confidence": "low",
        "recommendation_item_type": "ingredient",
        "context_correction_notes": "renamed_cheese_and_excluded_as_standalone_ingredient",
    },
    "keju kacang tanah": {
        "food_name": "selai kacang",
        "food_category": "lainnya",
        "main_ingredient": "kacang",
        "base_ingredient": "kacang",
        "base_ingredient_tags": "kacang",
        "contains_dairy": "False",
        "contains_nuts": "True",
        "contains_peanut": "True",
        "ingredient_only_flag": "True",
        "is_recommendable_food": "False",
        "recommendation_exclusion_reason": "spread_not_standalone_menu",
        "recommendation_confidence": "low",
        "recommendation_item_type": "ingredient",
        "context_correction_notes": "renamed_peanut_cheese_to_selai_kacang_and_excluded_as_spread",
    },
    "leverwost sosis hati": {
        "food_name": "sosis hati liverwurst",
        "main_ingredient": "sapi",
        "base_ingredient": "sapi",
        "base_ingredient_tags": "sapi",
        "is_recommendable_food": "False",
        "recommendation_exclusion_reason": "processed_meat_not_menu",
        "recommendation_confidence": "low",
    },
    "sapi daging sosis worst": {"food_name": "sosis daging sapi wurst"},
    "sapi hati sosis liverworst": {"food_name": "sosis hati sapi liverwurst"},
    "worst sosis daging": {"food_name": "sosis daging wurst"},
    "serbuk coklat": {
        "food_name": "bubuk cokelat",
        "ingredient_only_flag": "True",
        "is_recommendable_food": "False",
        "recommendation_exclusion_reason": "ingredient_powder_not_menu",
        "recommendation_confidence": "low",
        "recommendation_item_type": "ingredient",
    },
    "beras giling masak nasi": {"food_name": "nasi putih"},
    "beras ketan hitam kukus": {"food_name": "ketan hitam kukus"},
    "beras ketan putih kukus": {"food_name": "ketan putih kukus"},
    "biji jambu mete": {
        "food_name": "kacang mete",
        "food_category": "snack_dessert",
        "main_ingredient": "kacang",
        "base_ingredient": "kacang",
        "base_ingredient_tags": "kacang",
        "contains_nuts": "True",
        "cooking_category": "olahan",
        "meal_template_role": "snack",
        "pairing_role": "snack",
    },
    "biji jambu mete goreng": {
        "food_name": "kacang mete goreng",
        "food_category": "snack_dessert",
        "main_ingredient": "kacang",
        "base_ingredient": "kacang",
        "base_ingredient_tags": "kacang",
        "contains_nuts": "True",
        "meal_template_role": "snack",
        "pairing_role": "snack",
    },
    "jagung kuning giling": {"food_name": "jagung giling kuning"},
    "jagung kuning pipil baru": {"food_name": "jagung pipil kuning segar"},
    "jagung kuning pipil lama": {"food_name": "jagung pipil kuning kering"},
    "jagung pipil var harapan kering": {"food_name": "jagung pipil kering"},
    "jagung pipil var metro kering": {"food_name": "jagung pipil kering metro"},
    "jagung putih giling": {"food_name": "jagung giling putih"},
    "jagung putih pipil baru": {"food_name": "jagung pipil putih segar"},
    "jagung putih pipil lama": {"food_name": "jagung pipil putih kering"},
    "katul jagung": {"food_name": "bekatul jagung"},
    "jamur kuping kering": {"food_name": "jamur kuping kering"},
    "teh hijau daun kering": {"food_name": "daun teh hijau kering"},
    "teh melati daun kering": {"food_name": "daun teh melati kering"},
    "bagea kw 1": {
        "food_name": "kue bagea sagu",
        "food_category": "snack_dessert",
        "main_ingredient": "sagu",
        "base_ingredient": "sagu",
        "base_ingredient_tags": "sagu",
    },
    "bagea kw 2": {
        "food_name": "kue bagea sagu kelapa",
        "food_category": "snack_dessert",
        "main_ingredient": "sagu",
        "base_ingredient": "sagu",
        "base_ingredient_tags": "sagu|kelapa",
    },
    "baje": {
        "food_name": "baje ketan",
        "food_category": "snack_dessert",
        "main_ingredient": "beras",
        "base_ingredient": "beras",
        "base_ingredient_tags": "beras|kelapa",
    },
    "bakwan": {
        "food_name": "bakwan sayur",
        "food_category": "gorengan",
        "main_ingredient": "sayuran",
        "base_ingredient": "sayuran",
        "base_ingredient_tags": "sayuran|gandum",
        "contains_gluten": "True",
        "meal_template_role": "side",
    },
    "barongko": {
        "food_name": "barongko pisang",
        "main_ingredient": "buah",
        "base_ingredient": "buah",
        "base_ingredient_tags": "pisang|santan|telur",
        "contains_egg": "True",
    },
    "bika ambon": {
        "food_name": "bika ambon",
        "main_ingredient": "gandum",
        "base_ingredient": "gandum",
        "base_ingredient_tags": "gandum|telur|santan",
        "contains_gluten": "True",
        "contains_egg": "True",
    },
    "biskuit": {
        "food_name": "biskuit",
        "main_ingredient": "gandum",
        "base_ingredient": "gandum",
        "base_ingredient_tags": "gandum",
        "contains_gluten": "True",
    },
    "coklat manis batang": {
        "food_name": "cokelat batang manis",
        "base_ingredient": "cokelat",
        "base_ingredient_tags": "cokelat",
    },
    "coklat pahit batang": {
        "food_name": "cokelat batang pahit",
        "base_ingredient": "cokelat",
        "base_ingredient_tags": "cokelat",
    },
    "combro": {
        "food_name": "combro",
        "food_category": "gorengan",
        "main_ingredient": "singkong",
        "base_ingredient": "singkong",
        "base_ingredient_tags": "singkong|kedelai",
        "contains_soy": "True",
        "meal_template_role": "side",
    },
    "dodol": {"food_name": "dodol", "base_ingredient": "beras", "base_ingredient_tags": "beras|santan"},
    "dodol bali": {"food_name": "dodol bali", "base_ingredient": "beras", "base_ingredient_tags": "beras|santan"},
    "dodol banjarmasin": {"food_name": "dodol banjarmasin", "base_ingredient": "beras", "base_ingredient_tags": "beras|santan"},
    "dodol galamai": {"food_name": "dodol galamai", "base_ingredient": "beras", "base_ingredient_tags": "beras|santan"},
    "dodol manado": {"food_name": "dodol manado", "base_ingredient": "beras", "base_ingredient_tags": "beras|santan"},
    "empal goreng": {
        "food_name": "empal goreng sapi",
        "food_category": "lauk_hewani",
        "main_ingredient": "sapi",
        "base_ingredient": "sapi",
        "base_ingredient_tags": "sapi",
        "meal_template_role": "protein",
    },
    "emping kerupuk melinjo": {"food_name": "emping melinjo", "base_ingredient": "melinjo", "base_ingredient_tags": "melinjo"},
    "emping komak": {"food_name": "emping komak", "base_ingredient": "kacang", "base_ingredient_tags": "kacang"},
    "enting-enting gepuk hello kity": {"food_name": "enting-enting gepuk", "base_ingredient": "kacang", "base_ingredient_tags": "kacang"},
    "enting-enting wijen": {"food_name": "enting-enting wijen", "base_ingredient": "wijen", "base_ingredient_tags": "wijen"},
    "gemblong": {"food_name": "gemblong ketan", "base_ingredient": "beras", "base_ingredient_tags": "beras|kelapa"},
    "gendar goreng": {"food_name": "gendar goreng", "base_ingredient": "beras", "base_ingredient_tags": "beras"},
    "intip goreng": {"food_name": "intip goreng", "base_ingredient": "beras", "base_ingredient_tags": "beras"},
    "jambal goreng": {"food_name": "ikan jambal goreng", "main_ingredient": "ikan", "base_ingredient": "ikan", "base_ingredient_tags": "ikan"},
    "kalio kikil tunjang masakan": {"food_name": "kalio kikil sapi", "main_ingredient": "sapi", "base_ingredient": "sapi", "base_ingredient_tags": "sapi"},
    "kalio otak masakan": {"food_name": "kalio otak sapi", "main_ingredient": "sapi", "base_ingredient": "sapi", "base_ingredient_tags": "sapi"},
    "kerupuk aci": {"food_name": "kerupuk aci", "base_ingredient": "singkong", "base_ingredient_tags": "singkong"},
    "kerupuk kemplang goreng": {"food_name": "kemplang goreng", "main_ingredient": "ikan", "base_ingredient": "ikan", "base_ingredient_tags": "ikan"},
    "kerupuk kemplang panggang": {"food_name": "kemplang panggang", "main_ingredient": "ikan", "base_ingredient": "ikan", "base_ingredient_tags": "ikan"},
    "kerupuk melinjo tebal goreng asin": {"food_name": "emping melinjo goreng asin", "base_ingredient": "melinjo", "base_ingredient_tags": "melinjo"},
    "kerupuk melinjo tebal goreng manis": {"food_name": "emping melinjo goreng manis", "base_ingredient": "melinjo", "base_ingredient_tags": "melinjo"},
    "kerupuk melinjo tipis goreng": {"food_name": "emping melinjo tipis goreng", "base_ingredient": "melinjo", "base_ingredient_tags": "melinjo"},
    "laksa": {"food_name": "laksa ayam", "main_ingredient": "ayam", "base_ingredient": "ayam", "base_ingredient_tags": "ayam|santan"},
    "makaroni": {"food_name": "makaroni rebus", "main_ingredient": "gandum", "base_ingredient": "gandum", "base_ingredient_tags": "gandum", "contains_gluten": "True"},
    "nopia spesial": {"food_name": "nopia", "main_ingredient": "gandum", "base_ingredient": "gandum", "base_ingredient_tags": "gandum", "contains_gluten": "True"},
    "putu mayang": {"food_name": "putu mayang", "base_ingredient": "beras", "base_ingredient_tags": "beras|santan"},
    "renggi goreng": {"food_name": "rengginang goreng", "base_ingredient": "beras", "base_ingredient_tags": "beras"},
    "sate pusut masakan": {"food_name": "sate pusut ikan", "main_ingredient": "ikan", "base_ingredient": "ikan", "base_ingredient_tags": "ikan"},
    "sie reuboh masakan": {"food_name": "sie reuboh sapi", "food_category": "lauk_hewani", "main_ingredient": "sapi", "base_ingredient": "sapi", "base_ingredient_tags": "sapi"},
    "sukiyaki masakan": {"food_name": "sukiyaki sapi", "main_ingredient": "sapi", "base_ingredient": "sapi", "base_ingredient_tags": "sapi"},
    "betok wadi masakan": {"food_name": "betok wadi ikan", "main_ingredient": "ikan", "base_ingredient": "ikan", "base_ingredient_tags": "ikan"},
    "jangang bintatoeng masakan": {"food_name": "ayam bintatoeng", "food_category": "lauk_hewani", "main_ingredient": "ayam", "base_ingredient": "ayam", "base_ingredient_tags": "ayam"},
    "jukku pallu kaloa masakan": {"food_name": "ikan pallu kaloa", "food_category": "berkuah", "main_ingredient": "ikan", "base_ingredient": "ikan", "base_ingredient_tags": "ikan"},
    "lawara jangang masakan": {"food_name": "lawar ayam", "food_category": "lauk_hewani", "main_ingredient": "ayam", "base_ingredient": "ayam", "base_ingredient_tags": "ayam"},
    "lawara penjah masakan": {"food_name": "lawar ikan", "food_category": "lauk_hewani", "main_ingredient": "ikan", "base_ingredient": "ikan", "base_ingredient_tags": "ikan"},
    "nasu likku masakan": {"food_name": "ayam nasu likku", "food_category": "lauk_hewani", "main_ingredient": "ayam", "base_ingredient": "ayam", "base_ingredient_tags": "ayam"},
    "pelepah manuk masakan": {"food_name": "ayam pelepah manuk", "food_category": "lauk_hewani", "main_ingredient": "ayam", "base_ingredient": "ayam", "base_ingredient_tags": "ayam"},
    "tedong pallu basa masakan": {"food_name": "pallu basa kerbau", "food_category": "berkuah", "main_ingredient": "daging_lain", "base_ingredient": "daging_lain", "base_ingredient_tags": "kerbau"},
    "gulai keumamah masakan": {"food_name": "gulai keumamah"},
    "sop saudara masakan": {"food_name": "sop saudara"},
    "soto banjar masakan": {"food_name": "soto banjar"},
    "soto kudus masakan": {"food_name": "soto kudus"},
    "soto madura masakan": {"food_name": "soto madura"},
    "soto pekalongan masakan": {"food_name": "soto pekalongan"},
    "soto pemalang masakan": {"food_name": "soto pemalang"},
    "soto sukaraja masakan": {"food_name": "soto sukaraja"},
    "ayam taliwang masakan": {"food_name": "ayam taliwang"},
    "chicken teriyaki masakan": {
        "food_name": "ayam teriyaki",
        "food_category": "lauk_hewani",
        "main_ingredient": "ayam",
        "base_ingredient": "ayam",
        "base_ingredient_tags": "ayam",
        "meal_template_role": "protein",
    },
    "gulai ikan masakan": {"food_name": "gulai ikan", "food_category": "berkuah", "main_ingredient": "ikan", "base_ingredient": "ikan", "base_ingredient_tags": "ikan"},
    "gulai ikan paya masakan": {"food_name": "gulai ikan paya", "food_category": "berkuah", "main_ingredient": "ikan", "base_ingredient": "ikan", "base_ingredient_tags": "ikan"},
    "gulai tiram masakan": {"food_name": "gulai tiram", "food_category": "berkuah", "main_ingredient": "seafood", "base_ingredient": "seafood", "base_ingredient_tags": "seafood"},
    "gurame asem manis masakan": {"food_name": "gurame asam manis"},
    "ikan asar merah masakan": {"food_name": "ikan asar merah"},
    "ikan bandeng presto masakan": {"food_name": "bandeng presto"},
    "ikan sanggang masakan": {"food_name": "ikan sanggang"},
    "kalio jeroan masakan": {"food_name": "kalio jeroan sapi", "food_category": "lauk_hewani", "main_ingredient": "sapi", "base_ingredient": "sapi", "base_ingredient_tags": "sapi"},
    "kalio telur masakan": {"food_name": "kalio telur", "base_ingredient": "telur", "base_ingredient_tags": "telur"},
    "naan maran sapi masakan": {"food_name": "naan maran sapi"},
    "parede baleh masakan": {"food_name": "parede baleh ikan", "food_category": "berkuah", "main_ingredient": "ikan", "base_ingredient": "ikan", "base_ingredient_tags": "ikan"},
    "pencok lele masakan": {"food_name": "pencok lele"},
    "sop kambing masakan": {"food_name": "sop kambing", "food_category": "berkuah", "main_ingredient": "kambing", "base_ingredient": "kambing", "base_ingredient_tags": "kambing"},
    "teri balado masakan": {"food_name": "teri balado"},
    "keripik gadung": {"food_name": "keripik gadung", "base_ingredient": "umbi", "base_ingredient_tags": "gadung|umbi"},
    "keripik lampung": {"food_name": "keripik pisang lampung", "base_ingredient": "buah", "base_ingredient_tags": "pisang"},
    "koro kerupuk biji": {"food_name": "kerupuk koro", "base_ingredient": "kacang", "base_ingredient_tags": "kacang|koro"},
}


FIELD_CORRECTIONS = {
    "beef yakiniku masakan": {
        "food_category": "lauk_hewani",
        "food_category_source": "manual_real_food_curation",
        "base_ingredient": "sapi",
        "base_ingredient_tags": "sapi",
        "pairing_group": "traditional_protein",
        "pairing_role": "protein",
        "pairing_notes": "traditional_protein_for_rice_noodle",
        "pairing_suitability_notes": "main_meal_component",
        "meal_template_role": "protein",
        "context_correction_notes": "corrected_not_berkuah_yakiniku_is_beef_protein_dish",
    },
    "coto mangkasara sapi masakan": {
        "cooking_category": "berkuah",
        "food_category": "berkuah",
        "food_category_source": "manual_real_food_curation",
        "main_ingredient": "sapi",
        "base_ingredient": "sapi",
        "base_ingredient_tags": "sapi",
        "meal_template_role": "complete",
        "context_correction_notes": "corrected_as_sapi_berkuah",
    },
    "rawon masakan": {
        "food_category": "berkuah",
        "food_category_source": "manual_real_food_curation",
        "main_ingredient": "sapi",
        "base_ingredient": "sapi",
        "base_ingredient_tags": "sapi",
        "meal_template_role": "complete",
        "context_correction_notes": "corrected_as_sapi_berkuah",
    },
    "sop buntut masakan": {
        "food_category": "berkuah",
        "food_category_source": "manual_real_food_curation",
        "main_ingredient": "sapi",
        "base_ingredient": "sapi",
        "base_ingredient_tags": "sapi",
        "meal_template_role": "complete",
        "context_correction_notes": "corrected_as_sapi_berkuah",
    },
    "sop daging sapi masakan": {
        "food_category": "berkuah",
        "food_category_source": "manual_real_food_curation",
        "main_ingredient": "sapi",
        "base_ingredient": "sapi",
        "base_ingredient_tags": "sapi",
        "meal_template_role": "complete",
        "context_correction_notes": "corrected_as_sapi_berkuah",
    },
    "sop kaki sapi masakan": {
        "food_category": "berkuah",
        "food_category_source": "manual_real_food_curation",
        "main_ingredient": "sapi",
        "base_ingredient": "sapi",
        "base_ingredient_tags": "sapi",
        "meal_template_role": "complete",
        "context_correction_notes": "corrected_as_sapi_berkuah",
    },
    "sop konro masakan": {
        "food_category": "berkuah",
        "food_category_source": "manual_real_food_curation",
        "main_ingredient": "sapi",
        "base_ingredient": "sapi",
        "base_ingredient_tags": "sapi",
        "meal_template_role": "complete",
        "context_correction_notes": "corrected_as_sapi_berkuah",
    },
    "soto bandung masakan": {
        "food_category": "berkuah",
        "food_category_source": "manual_real_food_curation",
        "main_ingredient": "sapi",
        "base_ingredient": "sapi",
        "base_ingredient_tags": "sapi|lobak",
        "meal_template_role": "complete",
        "context_correction_notes": "corrected_as_sapi_berkuah",
    },
    "soto betawi masakan": {
        "food_category": "berkuah",
        "food_category_source": "manual_real_food_curation",
        "main_ingredient": "sapi",
        "base_ingredient": "sapi",
        "base_ingredient_tags": "sapi|susu|santan",
        "contains_dairy": "True",
        "meal_template_role": "complete",
        "context_correction_notes": "corrected_as_sapi_berkuah",
    },
    "soto dengan daging": {
        "food_category": "berkuah",
        "food_category_source": "manual_real_food_curation",
        "main_ingredient": "sapi",
        "base_ingredient": "sapi",
        "base_ingredient_tags": "sapi",
        "meal_template_role": "complete",
        "context_correction_notes": "corrected_as_sapi_berkuah",
    },
    "soto jeroan masakan": {
        "food_category": "berkuah",
        "food_category_source": "manual_real_food_curation",
        "main_ingredient": "sapi",
        "base_ingredient": "sapi",
        "base_ingredient_tags": "sapi",
        "meal_template_role": "complete",
        "context_correction_notes": "corrected_as_sapi_berkuah",
    },
    "soto padang masakan": {
        "food_category": "berkuah",
        "food_category_source": "manual_real_food_curation",
        "main_ingredient": "sapi",
        "base_ingredient": "sapi",
        "base_ingredient_tags": "sapi",
        "meal_template_role": "complete",
        "context_correction_notes": "corrected_as_sapi_berkuah",
    },
    "soto sulung masakan": {
        "food_category": "berkuah",
        "food_category_source": "manual_real_food_curation",
        "main_ingredient": "sapi",
        "base_ingredient": "sapi",
        "base_ingredient_tags": "sapi",
        "meal_template_role": "complete",
        "context_correction_notes": "corrected_as_sapi_berkuah",
    },
    "bakso": {
        "food_category": "berkuah",
        "food_category_source": "manual_real_food_curation",
        "main_ingredient": "sapi",
        "base_ingredient": "sapi",
        "base_ingredient_tags": "sapi",
        "meal_template_role": "complete",
        "context_correction_notes": "corrected_default_bakso_sapi_berkuah",
    },
    "gado-gado": {
        "food_category": "sayuran",
        "food_category_source": "manual_real_food_curation",
        "main_ingredient": "sayuran",
        "base_ingredient": "sayuran",
        "base_ingredient_tags": "sayuran|kacang|telur",
        "contains_peanut": "True",
        "contains_nuts": "True",
        "contains_egg": "True",
        "meal_template_role": "complete",
        "context_correction_notes": "corrected_gado_gado_as_vegetable_complete_menu",
    },
    "gulai keumamah masakan": {
        "food_category": "berkuah",
        "food_category_source": "manual_real_food_curation",
        "main_ingredient": "ikan",
        "base_ingredient": "ikan",
        "base_ingredient_tags": "ikan",
        "contains_seafood": "True",
        "meal_template_role": "complete",
        "context_correction_notes": "corrected_as_ikan_berkuah",
    },
    "gulai pliek": {
        "food_category": "sayuran",
        "food_category_source": "manual_real_food_curation",
        "main_ingredient": "sayuran",
        "base_ingredient": "sayuran",
        "base_ingredient_tags": "sayuran|santan",
        "meal_template_role": "vegetable",
        "context_correction_notes": "corrected_gulai_pliek_as_vegetable_curry",
    },
    "sop saudara masakan": {
        "food_category": "berkuah",
        "food_category_source": "manual_real_food_curation",
        "main_ingredient": "sapi",
        "base_ingredient": "sapi",
        "base_ingredient_tags": "sapi",
        "meal_template_role": "complete",
        "context_correction_notes": "corrected_sop_saudara_as_sapi_berkuah",
    },
    "soto banjar masakan": {
        "food_category": "berkuah",
        "food_category_source": "manual_real_food_curation",
        "main_ingredient": "ayam",
        "base_ingredient": "ayam",
        "base_ingredient_tags": "ayam",
        "meal_template_role": "complete",
        "context_correction_notes": "corrected_soto_banjar_as_ayam_berkuah",
    },
    "soto kudus masakan": {
        "food_category": "berkuah",
        "food_category_source": "manual_real_food_curation",
        "main_ingredient": "ayam",
        "base_ingredient": "ayam",
        "base_ingredient_tags": "ayam",
        "meal_template_role": "complete",
        "context_correction_notes": "corrected_soto_kudus_as_ayam_berkuah",
    },
    "soto madura masakan": {
        "food_category": "berkuah",
        "food_category_source": "manual_real_food_curation",
        "main_ingredient": "sapi",
        "base_ingredient": "sapi",
        "base_ingredient_tags": "sapi",
        "meal_template_role": "complete",
        "context_correction_notes": "corrected_soto_madura_as_sapi_berkuah",
    },
    "soto pekalongan masakan": {
        "food_category": "berkuah",
        "food_category_source": "manual_real_food_curation",
        "main_ingredient": "sapi",
        "base_ingredient": "sapi",
        "base_ingredient_tags": "sapi",
        "meal_template_role": "complete",
        "context_correction_notes": "corrected_soto_pekalongan_as_sapi_berkuah",
    },
    "soto pemalang masakan": {
        "food_category": "berkuah",
        "food_category_source": "manual_real_food_curation",
        "main_ingredient": "ayam",
        "base_ingredient": "ayam",
        "base_ingredient_tags": "ayam",
        "meal_template_role": "complete",
        "context_correction_notes": "corrected_soto_pemalang_as_ayam_berkuah",
    },
    "soto sukaraja masakan": {
        "food_category": "berkuah",
        "food_category_source": "manual_real_food_curation",
        "main_ingredient": "sapi",
        "base_ingredient": "sapi",
        "base_ingredient_tags": "sapi",
        "meal_template_role": "complete",
        "context_correction_notes": "corrected_soto_sukaraja_as_sapi_berkuah",
    },
    "soto tanpa daging": {
        "food_category": "berkuah",
        "food_category_source": "manual_real_food_curation",
        "main_ingredient": "sayuran",
        "base_ingredient": "sayuran",
        "base_ingredient_tags": "sayuran",
        "meal_template_role": "complete",
        "context_correction_notes": "corrected_soto_without_meat_as_vegetable_soup",
    },
    "sate kulit": {
        "food_category": "lauk_hewani",
        "food_category_source": "manual_real_food_curation",
        "main_ingredient": "ayam",
        "base_ingredient": "ayam",
        "base_ingredient_tags": "ayam",
        "meal_template_role": "protein",
        "context_correction_notes": "corrected_sate_kulit_as_chicken_skin_satay",
    },
    "sate usus": {
        "food_category": "lauk_hewani",
        "food_category_source": "manual_real_food_curation",
        "main_ingredient": "ayam",
        "base_ingredient": "ayam",
        "base_ingredient_tags": "ayam",
        "meal_template_role": "protein",
        "context_correction_notes": "corrected_sate_usus_as_chicken_intestine_satay",
    },
    "oncom hitam goreng bertepung": {
        "ingredient_only_flag": "False",
        "raw_ingredient_flag": "False",
        "recommendation_item_type": "snack",
        "meal_template_role": "snack",
        "context_correction_notes": "corrected_oncom_goreng_as_snack"
    },
    "oncom merah goreng bertepung": {
        "ingredient_only_flag": "False",
        "raw_ingredient_flag": "False",
        "recommendation_item_type": "snack",
        "meal_template_role": "snack",
        "context_correction_notes": "corrected_oncom_goreng_as_snack"
    },
}


EXCLUSION_PATTERNS = [
    (r"\b(babi|anjing|penyu)\b", "not_suitable_for_default_indonesian_recommendation"),
    (r"\bkuda\b", "uncommon_meat_not_default_indonesian_menu"),
    (r"\b(jagung .*giling|jagung pipil .*kering|jagung pipil .*segar|bekatul jagung|katul jagung)\b", "raw_or_dry_corn_ingredient_not_menu"),
    (r"\b(jamur kuping kering|daun teh .*kering|bubuk|serbuk|jam selai|selai kacang)\b", "ingredient_not_standalone_menu"),
    (r"\b(keju cheddar|sosis|wurst|liverwurst|kornet|daging asap)\b", "processed_or_ingredient_item_not_menu"),
    (r"\b(kacang .*kering|kacang .*segar|kacang .*berkulit|kelapa .*kering|bonggol .*kering)\b", "raw_or_dry_ingredient_not_menu"),
    (r"\b(gadung kukus|ganyong kukus|ganyong rebus|suweg kukus|tales kukus|paria putih kukus)\b", "ingredient_like_single_food_not_menu"),
]

EXCLUSION_NAMES = {
    "agar-agar": "zero_calorie_or_plain_ingredient_not_menu",
    "jagung kuning muda": "raw_corn_ingredient_not_menu",
    "jagung muda": "raw_corn_ingredient_not_menu",
    "jagung putih muda": "raw_corn_ingredient_not_menu",
    "jagung giling kuning": "raw_or_dry_corn_ingredient_not_menu",
    "jagung giling putih": "raw_or_dry_corn_ingredient_not_menu",
    "jagung pipil kuning segar": "raw_corn_ingredient_not_menu",
    "jagung pipil kuning kering": "raw_or_dry_corn_ingredient_not_menu",
    "jagung pipil putih segar": "raw_corn_ingredient_not_menu",
    "jagung pipil putih kering": "raw_or_dry_corn_ingredient_not_menu",
    "jagung pipil kering": "raw_or_dry_corn_ingredient_not_menu",
    "jagung pipil kering metro": "raw_or_dry_corn_ingredient_not_menu",
    "bekatul jagung": "raw_or_dry_corn_ingredient_not_menu",
    "ikan katombo asin": "salted_raw_fish_not_standalone_menu",
    "kacang tanah kering": "raw_or_dry_ingredient_not_menu",
    "kacang babi kering": "raw_or_dry_ingredient_not_menu",
    "kacang belimbing kecipir kering": "raw_or_dry_ingredient_not_menu",
    "kacang mete mentah": "raw_or_dry_ingredient_not_menu",
    "jamur kuping kering": "raw_or_dry_ingredient_not_menu",
    "daun teh hijau kering": "raw_or_dry_ingredient_not_menu",
    "daun teh melati kering": "raw_or_dry_ingredient_not_menu",
    "bonggol pisang kering": "raw_or_dry_ingredient_not_menu",
    "kelapa hutan kering": "raw_or_dry_ingredient_not_menu",
    "djibokum masakan": "obscure_unknown_ingredient_not_default_menu",
    "kaholeo masakan": "obscure_unknown_ingredient_not_default_menu",
    "oramu ninahu ndawa olaho masakan": "obscure_unknown_ingredient_not_default_menu",
    "pinda masakan": "obscure_unknown_ingredient_not_default_menu",
    "sepi masakan": "obscure_unknown_ingredient_not_default_menu",
    "tinoransak masakan": "obscure_or_non_halal_risk_not_default_menu",
    "gete kuah asam masakan": "obscure_unknown_ingredient_not_default_menu",
    "gulai asam keueung masakan": "obscure_unknown_ingredient_not_default_menu",
    "paniki masak santan masakan": "uncommon_non_halal_risk_not_default_menu",
    "pindang kenari masakan": "obscure_unknown_ingredient_not_default_menu",
    "kerupuk sayong": "obscure_unknown_ingredient_not_default_menu",
    "kerupuk urat": "obscure_unknown_ingredient_not_default_menu",
    "permen": "candy_not_real_food_menu",
    "spaghetti": "not_indonesian_default_menu",
    "biji nangkabiji salak": "obscure_unknown_ingredient_not_default_menu",
    "kacang kedelai basah": "raw_or_dry_ingredient_not_menu",
}

RESTORE_RECOMMENDABLE_NAMES = {
    "ayam goreng tepung sayap",
    "ayam goreng tepung sayap ala texas",
    "ayam goreng tepung dada ala texas",
    "ayam goreng tepung dada",
    "ayam goreng tepung paha",
}


NEW_FOODS = [
    {
        "food_name": "nasi liwet solo",
        "calories": 178.0,
        "protein": 6.0,
        "fat": 5.0,
        "carbohydrate": 27.3,
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Nasi%20Liwet.jpg",
        "cooking_category": "olahan",
        "food_category": "karbohidrat_pokok",
        "main_ingredient": "beras",
        "base_ingredient": "beras",
        "base_ingredient_tags": "beras|ayam|santan",
        "meal_time_tags": "breakfast|lunch|dinner",
        "primary_meal_time": "lunch",
        "contains_dairy": "False",
        "contains_egg": "False",
        "contains_seafood": "False",
        "meal_template_role": "complete",
    },
    {
        "food_name": "nasi kuning komplit",
        "calories": 171.0,
        "protein": 5.0,
        "fat": 5.0,
        "carbohydrate": 25.3,
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Nasi%20kuning.JPG",
        "cooking_category": "olahan",
        "food_category": "karbohidrat_pokok",
        "main_ingredient": "beras",
        "base_ingredient": "beras",
        "base_ingredient_tags": "beras|telur|ayam",
        "meal_time_tags": "breakfast|lunch|dinner",
        "primary_meal_time": "breakfast",
        "contains_egg": "True",
        "meal_template_role": "complete",
    },
    {
        "food_name": "bubur ayam",
        "calories": 130.0,
        "protein": 7.5,
        "fat": 4.0,
        "carbohydrate": 16.0,
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Bubur%20ayam.jpg",
        "cooking_category": "berkuah",
        "food_category": "karbohidrat_pokok",
        "main_ingredient": "beras",
        "base_ingredient": "beras",
        "base_ingredient_tags": "beras|ayam",
        "meal_time_tags": "breakfast",
        "primary_meal_time": "breakfast",
        "meal_template_role": "complete",
    },
    {
        "food_name": "soto lamongan",
        "calories": 110.0,
        "protein": 8.0,
        "fat": 4.5,
        "carbohydrate": 9.5,
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Soto%20Lamongan.jpg",
        "cooking_category": "berkuah",
        "food_category": "berkuah",
        "main_ingredient": "ayam",
        "base_ingredient": "ayam",
        "base_ingredient_tags": "ayam",
        "meal_time_tags": "breakfast|lunch|dinner",
        "primary_meal_time": "lunch",
        "meal_template_role": "complete",
    },
    {
        "food_name": "sate ayam madura",
        "calories": 220.0,
        "protein": 16.0,
        "fat": 11.0,
        "carbohydrate": 14.5,
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Sate%20Ayam%20Madura.jpg",
        "cooking_category": "bakar",
        "food_category": "lauk_hewani",
        "main_ingredient": "ayam",
        "base_ingredient": "ayam",
        "base_ingredient_tags": "ayam|kacang",
        "meal_time_tags": "lunch|dinner",
        "primary_meal_time": "lunch",
        "contains_peanut": "True",
        "contains_nuts": "True",
        "meal_template_role": "protein",
    },
    {
        "food_name": "sate padang",
        "calories": 185.0,
        "protein": 12.0,
        "fat": 7.0,
        "carbohydrate": 18.5,
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Sate%20Padang.JPG",
        "cooking_category": "bakar",
        "food_category": "lauk_hewani",
        "main_ingredient": "sapi",
        "base_ingredient": "sapi",
        "base_ingredient_tags": "sapi|beras",
        "meal_time_tags": "lunch|dinner",
        "primary_meal_time": "dinner",
        "meal_template_role": "complete",
    },
    {
        "food_name": "ayam penyet",
        "calories": 260.0,
        "protein": 18.0,
        "fat": 17.0,
        "carbohydrate": 8.5,
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Ayam%20penyet.JPG",
        "cooking_category": "gorengan",
        "food_category": "lauk_hewani",
        "main_ingredient": "ayam",
        "base_ingredient": "ayam",
        "base_ingredient_tags": "ayam",
        "meal_time_tags": "lunch|dinner",
        "primary_meal_time": "lunch",
        "meal_template_role": "protein",
    },
    {
        "food_name": "ayam geprek",
        "calories": 285.0,
        "protein": 19.0,
        "fat": 18.0,
        "carbohydrate": 11.8,
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Ayam%20geprek.jpg",
        "cooking_category": "gorengan",
        "food_category": "lauk_hewani",
        "main_ingredient": "ayam",
        "base_ingredient": "ayam",
        "base_ingredient_tags": "ayam|gandum",
        "meal_time_tags": "lunch|dinner",
        "primary_meal_time": "lunch",
        "contains_gluten": "True",
        "meal_template_role": "protein",
    },
    {
        "food_name": "pecel lele",
        "calories": 210.0,
        "protein": 14.0,
        "fat": 12.0,
        "carbohydrate": 11.5,
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Pecel%20Lele%201.JPG",
        "cooking_category": "gorengan",
        "food_category": "lauk_hewani",
        "main_ingredient": "ikan",
        "base_ingredient": "ikan",
        "base_ingredient_tags": "ikan|beras",
        "meal_time_tags": "lunch|dinner",
        "primary_meal_time": "dinner",
        "contains_seafood": "True",
        "meal_template_role": "complete",
    },
    {
        "food_name": "lontong sayur",
        "calories": 160.0,
        "protein": 5.0,
        "fat": 7.0,
        "carbohydrate": 19.0,
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Lontong%20sayur.jpg",
        "cooking_category": "berkuah",
        "food_category": "berkuah",
        "main_ingredient": "beras",
        "base_ingredient": "beras",
        "base_ingredient_tags": "beras|sayuran|santan",
        "meal_time_tags": "breakfast|lunch",
        "primary_meal_time": "breakfast",
        "meal_template_role": "complete",
    },
    {
        "food_name": "ketoprak jakarta",
        "calories": 170.0,
        "protein": 7.0,
        "fat": 6.0,
        "carbohydrate": 22.0,
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Ketoprak.jpg",
        "cooking_category": "olahan",
        "food_category": "lauk_nabati",
        "main_ingredient": "kedelai",
        "base_ingredient": "kedelai",
        "base_ingredient_tags": "kedelai|kacang|beras",
        "meal_time_tags": "breakfast|lunch|dinner",
        "primary_meal_time": "lunch",
        "contains_peanut": "True",
        "contains_nuts": "True",
        "contains_soy": "True",
        "meal_template_role": "complete",
    },
    {
        "food_name": "karedok",
        "calories": 122.0,
        "protein": 5.0,
        "fat": 6.0,
        "carbohydrate": 12.0,
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Karedok.JPG",
        "cooking_category": "olahan",
        "food_category": "sayuran",
        "main_ingredient": "sayuran",
        "base_ingredient": "sayuran",
        "base_ingredient_tags": "sayuran|kacang",
        "meal_time_tags": "lunch|dinner",
        "primary_meal_time": "lunch",
        "contains_peanut": "True",
        "contains_nuts": "True",
        "meal_template_role": "vegetable",
    },
    {
        "food_name": "pepes ikan",
        "calories": 150.0,
        "protein": 20.0,
        "fat": 6.0,
        "carbohydrate": 4.0,
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/IkanPepes.JPG",
        "cooking_category": "rebus_kukus",
        "food_category": "lauk_hewani",
        "main_ingredient": "ikan",
        "base_ingredient": "ikan",
        "base_ingredient_tags": "ikan",
        "meal_time_tags": "lunch|dinner",
        "primary_meal_time": "dinner",
        "contains_seafood": "True",
        "meal_template_role": "protein",
    },
    {
        "food_name": "tumis kangkung",
        "calories": 70.0,
        "protein": 2.5,
        "fat": 4.0,
        "carbohydrate": 6.0,
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Tumis%20kangkung.JPG",
        "cooking_category": "tumis",
        "food_category": "sayuran",
        "main_ingredient": "sayuran",
        "base_ingredient": "sayuran",
        "base_ingredient_tags": "sayuran",
        "meal_time_tags": "lunch|dinner",
        "primary_meal_time": "lunch",
        "meal_template_role": "vegetable",
    },
    {
        "food_name": "pempek kapal selam",
        "calories": 190.0,
        "protein": 9.0,
        "fat": 6.0,
        "carbohydrate": 25.0,
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Pempek%20kapal%20selam.jpg",
        "cooking_category": "olahan",
        "food_category": "snack_dessert",
        "main_ingredient": "ikan",
        "base_ingredient": "ikan",
        "base_ingredient_tags": "ikan|telur",
        "meal_time_tags": "lunch|dinner",
        "primary_meal_time": "lunch",
        "contains_egg": "True",
        "contains_seafood": "True",
        "meal_template_role": "snack",
    },
    {
        "food_name": "tekwan",
        "calories": 88.0,
        "protein": 7.5,
        "fat": 2.0,
        "carbohydrate": 10.0,
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Tekwan.JPG",
        "cooking_category": "berkuah",
        "food_category": "berkuah",
        "main_ingredient": "ikan",
        "base_ingredient": "ikan",
        "base_ingredient_tags": "ikan|seafood",
        "meal_time_tags": "lunch|dinner",
        "primary_meal_time": "lunch",
        "contains_seafood": "True",
        "meal_template_role": "complete",
    },
    {
        "food_name": "tahu campur",
        "calories": 159.0,
        "protein": 7.0,
        "fat": 7.0,
        "carbohydrate": 17.0,
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Tahu%20campur%20Ambarawa.jpg",
        "cooking_category": "berkuah",
        "food_category": "lauk_nabati",
        "main_ingredient": "kedelai",
        "base_ingredient": "kedelai",
        "base_ingredient_tags": "kedelai|beras",
        "meal_time_tags": "lunch|dinner",
        "primary_meal_time": "lunch",
        "contains_soy": "True",
        "meal_template_role": "complete",
    },
    {
        "food_name": "capcay kuah",
        "calories": 82.0,
        "protein": 3.5,
        "fat": 4.0,
        "carbohydrate": 8.0,
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Cap%20Cay%20%28Sayur%20Cap%20Chay%29%202.jpg",
        "cooking_category": "berkuah",
        "food_category": "sayuran",
        "main_ingredient": "sayuran",
        "base_ingredient": "sayuran",
        "base_ingredient_tags": "sayuran",
        "meal_time_tags": "lunch|dinner",
        "primary_meal_time": "lunch",
        "meal_template_role": "vegetable",
    },
    {
        "food_name": "telur balado",
        "calories": 161.0,
        "protein": 10.0,
        "fat": 11.0,
        "carbohydrate": 5.5,
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Telur%20Balado.jpg",
        "cooking_category": "olahan",
        "food_category": "lauk_hewani",
        "main_ingredient": "telur",
        "base_ingredient": "telur",
        "base_ingredient_tags": "telur",
        "meal_time_tags": "breakfast|lunch|dinner",
        "primary_meal_time": "lunch",
        "contains_egg": "True",
        "meal_template_role": "protein",
    },
    {
        "food_name": "tempe orek",
        "calories": 211.0,
        "protein": 12.0,
        "fat": 11.0,
        "carbohydrate": 16.0,
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Tempe%20Orek.jpg",
        "cooking_category": "tumis",
        "food_category": "lauk_nabati",
        "main_ingredient": "kedelai",
        "base_ingredient": "kedelai",
        "base_ingredient_tags": "kedelai",
        "meal_time_tags": "breakfast|lunch|dinner",
        "primary_meal_time": "lunch",
        "contains_soy": "True",
        "meal_template_role": "protein",
    },
    {
        "food_name": "ikan bakar dabu-dabu",
        "calories": 145.0,
        "protein": 22.0,
        "fat": 5.0,
        "carbohydrate": 3.0,
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Ikan%20Tude%20Bakar.JPG",
        "cooking_category": "bakar",
        "food_category": "lauk_hewani",
        "main_ingredient": "ikan",
        "base_ingredient": "ikan",
        "base_ingredient_tags": "ikan",
        "meal_time_tags": "lunch|dinner",
        "primary_meal_time": "dinner",
        "contains_seafood": "True",
        "meal_template_role": "protein",
    },
    {
        "food_name": "nasi campur bali",
        "calories": 237.0,
        "protein": 10.0,
        "fat": 9.0,
        "carbohydrate": 29.0,
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Nasi%20campur%20bali.jpg",
        "cooking_category": "olahan",
        "food_category": "karbohidrat_pokok",
        "main_ingredient": "beras",
        "base_ingredient": "beras",
        "base_ingredient_tags": "beras|ayam|sayuran",
        "meal_time_tags": "lunch|dinner",
        "primary_meal_time": "lunch",
        "meal_template_role": "complete",
    },
    {
        "food_name": "tongseng sapi",
        "calories": 179.0,
        "protein": 12.0,
        "fat": 10.0,
        "carbohydrate": 10.3,
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Tongseng%20Sapi.jpg",
        "cooking_category": "berkuah",
        "food_category": "berkuah",
        "main_ingredient": "sapi",
        "base_ingredient": "sapi",
        "base_ingredient_tags": "sapi|santan|sayuran",
        "meal_time_tags": "lunch|dinner",
        "primary_meal_time": "dinner",
        "meal_template_role": "complete",
    },
    {
        "food_name": "semur daging sapi",
        "calories": 195.0,
        "protein": 13.0,
        "fat": 11.0,
        "carbohydrate": 11.5,
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Semur%20Daging%20Kentang.JPG",
        "cooking_category": "berkuah",
        "food_category": "berkuah",
        "main_ingredient": "sapi",
        "base_ingredient": "sapi",
        "base_ingredient_tags": "sapi|kentang",
        "meal_time_tags": "lunch|dinner",
        "primary_meal_time": "dinner",
        "meal_template_role": "complete",
    },
    {
        "food_name": "sop iga sapi",
        "calories": 120.0,
        "protein": 9.0,
        "fat": 7.0,
        "carbohydrate": 5.3,
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Beef%20soup%20may%202021.jpg",
        "cooking_category": "berkuah",
        "food_category": "berkuah",
        "main_ingredient": "sapi",
        "base_ingredient": "sapi",
        "base_ingredient_tags": "sapi|sayuran",
        "meal_time_tags": "lunch|dinner",
        "primary_meal_time": "lunch",
        "meal_template_role": "complete",
    },
    {
        "food_name": "soto ayam bening",
        "calories": 95.0,
        "protein": 8.0,
        "fat": 4.0,
        "carbohydrate": 6.8,
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Soto%20ayam.JPG",
        "cooking_category": "berkuah",
        "food_category": "berkuah",
        "main_ingredient": "ayam",
        "base_ingredient": "ayam",
        "base_ingredient_tags": "ayam",
        "meal_time_tags": "breakfast|lunch|dinner",
        "primary_meal_time": "lunch",
        "meal_template_role": "complete",
    },
    {
        "food_name": "sop ayam sayuran",
        "calories": 85.0,
        "protein": 7.0,
        "fat": 3.0,
        "carbohydrate": 7.8,
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Chicken%20soup%20with%20vegetables.jpg",
        "cooking_category": "berkuah",
        "food_category": "berkuah",
        "main_ingredient": "ayam",
        "base_ingredient": "ayam",
        "base_ingredient_tags": "ayam|sayuran",
        "meal_time_tags": "lunch|dinner",
        "primary_meal_time": "lunch",
        "meal_template_role": "complete",
    },
    {
        "food_name": "opor ayam",
        "calories": 178.0,
        "protein": 10.0,
        "fat": 12.0,
        "carbohydrate": 7.3,
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Opor%20ayam.jpg",
        "cooking_category": "berkuah",
        "food_category": "berkuah",
        "main_ingredient": "ayam",
        "base_ingredient": "ayam",
        "base_ingredient_tags": "ayam|santan",
        "meal_time_tags": "lunch|dinner",
        "primary_meal_time": "dinner",
        "meal_template_role": "complete",
    },
    {
        "food_name": "kari ayam",
        "calories": 165.0,
        "protein": 11.0,
        "fat": 10.0,
        "carbohydrate": 9.0,
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Gulai%20ayam.jpg",
        "cooking_category": "berkuah",
        "food_category": "berkuah",
        "main_ingredient": "ayam",
        "base_ingredient": "ayam",
        "base_ingredient_tags": "ayam|santan",
        "meal_time_tags": "lunch|dinner",
        "primary_meal_time": "dinner",
        "meal_template_role": "complete",
    },
    {
        "food_name": "garang asem ayam",
        "calories": 118.0,
        "protein": 10.0,
        "fat": 5.0,
        "carbohydrate": 8.3,
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Garang%20asem%20ayam.jpg",
        "cooking_category": "berkuah",
        "food_category": "berkuah",
        "main_ingredient": "ayam",
        "base_ingredient": "ayam",
        "base_ingredient_tags": "ayam",
        "meal_time_tags": "lunch|dinner",
        "primary_meal_time": "lunch",
        "meal_template_role": "complete",
    },
    {
        "food_name": "pindang ikan patin",
        "calories": 120.0,
        "protein": 14.0,
        "fat": 5.0,
        "carbohydrate": 6.3,
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Pindang%20patin.jpg",
        "cooking_category": "berkuah",
        "food_category": "berkuah",
        "main_ingredient": "ikan",
        "base_ingredient": "ikan",
        "base_ingredient_tags": "ikan",
        "meal_time_tags": "lunch|dinner",
        "primary_meal_time": "lunch",
        "contains_seafood": "True",
        "meal_template_role": "complete",
    },
    {
        "food_name": "ikan kuah kuning",
        "calories": 112.0,
        "protein": 16.0,
        "fat": 4.0,
        "carbohydrate": 3.0,
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Papeda%2C%20Kuah%20Kuning%2C%20Ikan%20Tude%20Bakar%202.jpg",
        "cooking_category": "berkuah",
        "food_category": "berkuah",
        "main_ingredient": "ikan",
        "base_ingredient": "ikan",
        "base_ingredient_tags": "ikan",
        "meal_time_tags": "lunch|dinner",
        "primary_meal_time": "lunch",
        "contains_seafood": "True",
        "meal_template_role": "complete",
    },
    {
        "food_name": "sop ikan batam",
        "calories": 95.0,
        "protein": 13.0,
        "fat": 3.0,
        "carbohydrate": 6.5,
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Sop%20ikan%20Batam.jpg",
        "cooking_category": "berkuah",
        "food_category": "berkuah",
        "main_ingredient": "ikan",
        "base_ingredient": "ikan",
        "base_ingredient_tags": "ikan|sayuran",
        "meal_time_tags": "lunch|dinner",
        "primary_meal_time": "lunch",
        "contains_seafood": "True",
        "meal_template_role": "complete",
    },
    {
        "food_name": "mangut lele",
        "calories": 165.0,
        "protein": 13.0,
        "fat": 10.0,
        "carbohydrate": 8.3,
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Mangut%20lele.jpg",
        "cooking_category": "berkuah",
        "food_category": "berkuah",
        "main_ingredient": "ikan",
        "base_ingredient": "ikan",
        "base_ingredient_tags": "ikan|santan",
        "meal_time_tags": "lunch|dinner",
        "primary_meal_time": "dinner",
        "contains_seafood": "True",
        "meal_template_role": "complete",
    },
    {
        "food_name": "gulai kepala ikan",
        "calories": 145.0,
        "protein": 12.0,
        "fat": 9.0,
        "carbohydrate": 4.8,
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Gulai%20kepala%20ikan.jpg",
        "cooking_category": "berkuah",
        "food_category": "berkuah",
        "main_ingredient": "ikan",
        "base_ingredient": "ikan",
        "base_ingredient_tags": "ikan|santan",
        "meal_time_tags": "lunch|dinner",
        "primary_meal_time": "dinner",
        "contains_seafood": "True",
        "meal_template_role": "complete",
    },
    {
        "food_name": "tongseng kambing",
        "calories": 188.0,
        "protein": 12.0,
        "fat": 12.0,
        "carbohydrate": 8.0,
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Tongseng%20kambing.JPG",
        "cooking_category": "berkuah",
        "food_category": "berkuah",
        "main_ingredient": "kambing",
        "base_ingredient": "kambing",
        "base_ingredient_tags": "kambing|santan|sayuran",
        "meal_time_tags": "lunch|dinner",
        "primary_meal_time": "dinner",
        "meal_template_role": "complete",
    },
    {
        "food_name": "tengkleng kambing",
        "calories": 155.0,
        "protein": 13.0,
        "fat": 9.0,
        "carbohydrate": 7.0,
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Tengkleng%20kambing.jpg",
        "cooking_category": "berkuah",
        "food_category": "berkuah",
        "main_ingredient": "kambing",
        "base_ingredient": "kambing",
        "base_ingredient_tags": "kambing",
        "meal_time_tags": "lunch|dinner",
        "primary_meal_time": "dinner",
        "meal_template_role": "complete",
    },
    {
        "food_name": "bakwan jagung",
        "calories": 210.0,
        "protein": 5.0,
        "fat": 10.0,
        "carbohydrate": 25.0,
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Bakwan%20jagung.jpg",
        "cooking_category": "gorengan",
        "food_category": "gorengan",
        "main_ingredient": "sayuran",
        "base_ingredient": "sayuran",
        "base_ingredient_tags": "jagung|sayuran|gandum",
        "meal_time_tags": "lunch|dinner",
        "primary_meal_time": "lunch",
        "contains_gluten": "True",
        "meal_template_role": "side",
    },
    {
        "food_name": "perkedel jagung",
        "calories": 185.0,
        "protein": 4.5,
        "fat": 8.0,
        "carbohydrate": 23.8,
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Perkedel%20jagung.jpg",
        "cooking_category": "gorengan",
        "food_category": "gorengan",
        "main_ingredient": "sayuran",
        "base_ingredient": "sayuran",
        "base_ingredient_tags": "jagung|sayuran",
        "meal_time_tags": "lunch|dinner",
        "primary_meal_time": "lunch",
        "meal_template_role": "side",
    },
    {
        "food_name": "sayur asem jagung",
        "calories": 50.0,
        "protein": 2.0,
        "fat": 1.0,
        "carbohydrate": 8.5,
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Sayur%20asem.JPG",
        "cooking_category": "berkuah",
        "food_category": "sayuran",
        "main_ingredient": "sayuran",
        "base_ingredient": "sayuran",
        "base_ingredient_tags": "sayuran|jagung",
        "meal_time_tags": "lunch|dinner",
        "primary_meal_time": "lunch",
        "meal_template_role": "vegetable",
    },
    {
        "food_name": "sup jagung ayam",
        "calories": 90.0,
        "protein": 6.0,
        "fat": 3.0,
        "carbohydrate": 9.8,
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Chicken%20corn%20soup.jpg",
        "cooking_category": "berkuah",
        "food_category": "berkuah",
        "main_ingredient": "ayam",
        "base_ingredient": "ayam",
        "base_ingredient_tags": "ayam|jagung",
        "meal_time_tags": "lunch|dinner",
        "primary_meal_time": "lunch",
        "meal_template_role": "complete",
    },
    {
        "food_name": "sayur lodeh",
        "calories": 80.0,
        "protein": 2.5,
        "fat": 5.0,
        "carbohydrate": 6.5,
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Sayur%20lodeh.JPG",
        "cooking_category": "berkuah",
        "food_category": "sayuran",
        "main_ingredient": "sayuran",
        "base_ingredient": "sayuran",
        "base_ingredient_tags": "sayuran|santan",
        "meal_time_tags": "lunch|dinner",
        "primary_meal_time": "lunch",
        "meal_template_role": "vegetable",
    },
    {
        "food_name": "urap sayur",
        "calories": 92.0,
        "protein": 3.0,
        "fat": 6.0,
        "carbohydrate": 6.5,
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Urap%20sayur.jpg",
        "cooking_category": "olahan",
        "food_category": "sayuran",
        "main_ingredient": "sayuran",
        "base_ingredient": "sayuran",
        "base_ingredient_tags": "sayuran|kelapa",
        "meal_time_tags": "lunch|dinner",
        "primary_meal_time": "lunch",
        "meal_template_role": "vegetable",
    },
    {
        "food_name": "pecel sayur",
        "calories": 125.0,
        "protein": 5.0,
        "fat": 6.0,
        "carbohydrate": 12.8,
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Pecel%20sayur.jpg",
        "cooking_category": "olahan",
        "food_category": "sayuran",
        "main_ingredient": "sayuran",
        "base_ingredient": "sayuran",
        "base_ingredient_tags": "sayuran|kacang",
        "meal_time_tags": "breakfast|lunch|dinner",
        "primary_meal_time": "lunch",
        "contains_peanut": "True",
        "contains_nuts": "True",
        "meal_template_role": "complete",
    },
    {
        "food_name": "nasi pecel",
        "calories": 190.0,
        "protein": 6.0,
        "fat": 5.0,
        "carbohydrate": 30.3,
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Nasi%20pecel.jpg",
        "cooking_category": "olahan",
        "food_category": "karbohidrat_pokok",
        "main_ingredient": "beras",
        "base_ingredient": "beras",
        "base_ingredient_tags": "beras|sayuran|kacang",
        "meal_time_tags": "breakfast|lunch|dinner",
        "primary_meal_time": "breakfast",
        "contains_peanut": "True",
        "contains_nuts": "True",
        "meal_template_role": "complete",
    },
    {
        "food_name": "ayam rica-rica",
        "calories": 185.0,
        "protein": 16.0,
        "fat": 11.0,
        "carbohydrate": 5.5,
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Ayam%20rica-rica.jpg",
        "cooking_category": "olahan",
        "food_category": "lauk_hewani",
        "main_ingredient": "ayam",
        "base_ingredient": "ayam",
        "base_ingredient_tags": "ayam",
        "meal_time_tags": "lunch|dinner",
        "primary_meal_time": "dinner",
        "meal_template_role": "protein",
    },
    {
        "food_name": "ayam betutu",
        "calories": 210.0,
        "protein": 18.0,
        "fat": 13.0,
        "carbohydrate": 5.3,
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Ayam%20Betutu.jpg",
        "cooking_category": "olahan",
        "food_category": "lauk_hewani",
        "main_ingredient": "ayam",
        "base_ingredient": "ayam",
        "base_ingredient_tags": "ayam",
        "meal_time_tags": "lunch|dinner",
        "primary_meal_time": "dinner",
        "meal_template_role": "protein",
    },
    {
        "food_name": "ayam bumbu rujak",
        "calories": 195.0,
        "protein": 16.0,
        "fat": 12.0,
        "carbohydrate": 5.5,
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Ayam%20bumbu%20rujak.jpg",
        "cooking_category": "olahan",
        "food_category": "lauk_hewani",
        "main_ingredient": "ayam",
        "base_ingredient": "ayam",
        "base_ingredient_tags": "ayam",
        "meal_time_tags": "lunch|dinner",
        "primary_meal_time": "lunch",
        "meal_template_role": "protein",
    },
    {
        "food_name": "tahu telur",
        "calories": 180.0,
        "protein": 10.0,
        "fat": 11.0,
        "carbohydrate": 10.3,
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Tahu%20telur.jpg",
        "cooking_category": "olahan",
        "food_category": "lauk_nabati",
        "main_ingredient": "kedelai",
        "base_ingredient": "kedelai",
        "base_ingredient_tags": "kedelai|telur|kacang",
        "meal_time_tags": "lunch|dinner",
        "primary_meal_time": "lunch",
        "contains_egg": "True",
        "contains_soy": "True",
        "contains_peanut": "True",
        "contains_nuts": "True",
        "meal_template_role": "complete",
    },
    {
        "food_name": "tahu gejrot",
        "calories": 120.0,
        "protein": 7.0,
        "fat": 6.0,
        "carbohydrate": 9.5,
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Tahu%20gejrot.jpg",
        "cooking_category": "olahan",
        "food_category": "lauk_nabati",
        "main_ingredient": "kedelai",
        "base_ingredient": "kedelai",
        "base_ingredient_tags": "kedelai",
        "meal_time_tags": "lunch|dinner",
        "primary_meal_time": "lunch",
        "contains_soy": "True",
        "meal_template_role": "snack",
    },
    {
        "food_name": "rujak buah",
        "calories": 95.0,
        "protein": 1.0,
        "fat": 1.5,
        "carbohydrate": 19.3,
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Rujak%20buah.jpg",
        "cooking_category": "olahan",
        "food_category": "buah",
        "main_ingredient": "buah",
        "base_ingredient": "buah",
        "base_ingredient_tags": "buah|kacang",
        "meal_time_tags": "breakfast|lunch|dinner",
        "primary_meal_time": "lunch",
        "contains_peanut": "True",
        "contains_nuts": "True",
        "meal_template_role": "snack",
    },
    {
        "food_name": "bubur kacang hijau",
        "calories": 118.0,
        "protein": 5.0,
        "fat": 3.0,
        "carbohydrate": 17.8,
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Bubur%20kacang%20hijau.jpg",
        "cooking_category": "berkuah",
        "food_category": "snack_dessert",
        "main_ingredient": "kacang",
        "base_ingredient": "kacang",
        "base_ingredient_tags": "kacang|santan",
        "meal_time_tags": "breakfast|lunch|dinner",
        "primary_meal_time": "breakfast",
        "contains_nuts": "True",
        "meal_template_role": "snack",
    },
]


def normalize_text(value: object) -> str:
    text = "" if pd.isna(value) else str(value).lower()
    text = re.sub(r"[^a-z0-9\s_-]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def is_blank(value: object) -> bool:
    if pd.isna(value):
        return True
    text = str(value).strip().lower()
    return text in {"", "nan", "none", "unknown"}


def format_float(value: float) -> str:
    return f"{value:.1f}"


def macro_diff(calories: float, protein: float, fat: float, carbohydrate: float) -> str:
    calculated = protein * 4 + fat * 9 + carbohydrate * 4
    return format_float(round(calories - calculated, 1))


def next_food_id(existing_ids: pd.Series, offset: int) -> str:
    max_id = 0
    for raw_id in existing_ids.dropna().astype(str):
        match = re.fullmatch(r"FD(\d+)", raw_id.strip())
        if match:
            max_id = max(max_id, int(match.group(1)))
    return f"FD{max_id + offset:04d}"


def base_row(columns: list[str]) -> dict[str, str]:
    row = {column: "" for column in columns}
    row.update(
        {
            "source": CURATION_SOURCE,
            "zero_calorie_flag": "0",
            "calorie_inconsistent_flag": "0",
            "meal_time": "lunch,dinner",
            "contains_gluten": "False",
            "contains_dairy": "False",
            "contains_nuts": "False",
            "contains_peanut": "False",
            "contains_seafood": "False",
            "contains_egg": "False",
            "contains_soy": "False",
            "contains_celery": "False",
            "contains_mustard": "False",
            "contains_sesame": "False",
            "contains_sulfite": "False",
            "contains_other": "False",
            "contains_unknown": "False",
            "confidence": "manual_reviewed",
            "allergen_sources": "manual_real_food_curation",
            "label_sources": "manual_real_food_curation",
            "allergen_match_count": "0",
            "merge_status": "manual_added",
            "food_category_source": "manual_real_food_curation",
            "recipe_reference_match": "False",
            "suitable_breakfast": "False",
            "suitable_lunch": "True",
            "suitable_dinner": "True",
            "feature_rule_version": "manual_real_food_curation_v1",
            "menu_reference_match": "False",
            "ingredient_only_flag": "False",
            "raw_ingredient_flag": "False",
            "is_recommendable_food": "True",
            "recommendation_item_type": "menu",
            "recommendation_confidence": "high",
            "halal_status": "halal_candidate",
            "is_halal_candidate": "True",
            "contains_non_halal_ingredient": "False",
            "halal_confidence": "medium",
            "halal_rule_version": "halal_context_rules_v1",
            "menu_ready_rule_version": "manual_real_food_menu_ready_v1",
            "pairing_group": "complete_menu",
            "pairing_role": "complete",
            "pairing_notes": "standalone_complete_menu",
            "pairing_suitability_notes": "complete_menu_all_meals",
            "cleaning_action": "keep",
            "meal_template_role": "complete",
            "meal_combo_valid": "True",
            "image_url_status": "ok",
            "image_url_source": "manual_food_specific_wikimedia",
            "image_url_rule_version": IMAGE_RULE_VERSION,
        }
    )
    return row


def apply_meal_flags(row: dict[str, str], meal_time_tags: str) -> None:
    tags = set(meal_time_tags.split("|"))
    row["suitable_breakfast"] = str("breakfast" in tags)
    row["suitable_lunch"] = str("lunch" in tags)
    row["suitable_dinner"] = str("dinner" in tags)
    row["meal_time"] = ",".join(tag for tag in ["breakfast", "lunch", "dinner"] if tag in tags)


def apply_pairing(row: dict[str, str], meal_template_role: str) -> None:
    role_map = {
        "complete": ("complete_menu", "complete", "standalone_complete_menu", "complete_menu_all_meals", "menu"),
        "protein": (
            "traditional_protein",
            "protein",
            "traditional_protein_for_rice_noodle",
            "main_meal_component",
            "menu",
        ),
        "vegetable": (
            "cooked_or_ready_vegetable",
            "vegetable",
            "vegetable_side_for_complete_meal",
            "needs_protein_and_staple_pairing",
            "menu",
        ),
        "side": ("side_dish", "side", "side_dish_for_complete_meal", "needs_staple_or_protein_pairing", "menu"),
        "snack": ("savory_snack", "snack", "savory_snack_or_side", "snack_or_side_item", "snack"),
    }
    group, role, notes, suitability, item_type = role_map[meal_template_role]
    row["pairing_group"] = group
    row["pairing_role"] = role
    row["pairing_notes"] = notes
    row["pairing_suitability_notes"] = suitability
    row["meal_template_role"] = meal_template_role
    row["recommendation_item_type"] = item_type


def apply_name_corrections(df: pd.DataFrame) -> int:
    corrected = 0
    existing_names = set(df["food_name_clean"].map(normalize_text))

    for old_clean_name, updates in NAME_CORRECTIONS.items():
        mask = df["food_name_clean"].eq(old_clean_name)
        if not mask.any():
            continue

        new_name = updates.get("food_name")
        if new_name:
            new_clean_name = normalize_text(new_name)
            conflicting_names = existing_names - {old_clean_name}
            if new_clean_name in conflicting_names:
                continue
            df.loc[mask, "food_name"] = new_name
            df.loc[mask, "food_name_clean"] = new_clean_name
            existing_names.discard(old_clean_name)
            existing_names.add(new_clean_name)

        for column, value in updates.items():
            if column in {"food_name", "food_name_clean"}:
                continue
            if column in df.columns:
                df.loc[mask, column] = value
        corrected += int(mask.sum())

    return corrected


def apply_recommendation_exclusions(df: pd.DataFrame) -> int:
    changed = 0

    for idx, row in df.iterrows():
        clean_name = normalize_text(row.get("food_name_clean", row.get("food_name", "")))
        reason = EXCLUSION_NAMES.get(clean_name)
        if not reason:
            for pattern, pattern_reason in EXCLUSION_PATTERNS:
                if re.search(pattern, clean_name):
                    reason = pattern_reason
                    break
        if not reason:
            continue

        was_recommendable = str(row.get("is_recommendable_food", "")).strip().lower() == "true"
        if was_recommendable:
            changed += 1

        df.at[idx, "is_recommendable_food"] = "False"
        df.at[idx, "recommendation_exclusion_reason"] = reason
        df.at[idx, "recommendation_confidence"] = "low"
        df.at[idx, "meal_combo_valid"] = "False"
        df.at[idx, "cleaning_action"] = "drop"
        df.at[idx, "cleaning_reason"] = reason
        if "ingredient" in reason or "raw" in reason or "processed" in reason or "zero_calorie" in reason:
            df.at[idx, "ingredient_only_flag"] = "True"
            df.at[idx, "recommendation_item_type"] = "ingredient"
        else:
            df.at[idx, "recommendation_item_type"] = "excluded"

    return changed


def restore_known_menu_items(df: pd.DataFrame) -> int:
    restored = 0
    for idx, row in df.iterrows():
        clean_name = normalize_text(row.get("food_name_clean", row.get("food_name", "")))
        if clean_name not in RESTORE_RECOMMENDABLE_NAMES:
            continue
        was_recommendable = str(row.get("is_recommendable_food", "")).strip().lower() == "true"
        df.at[idx, "is_recommendable_food"] = "True"
        df.at[idx, "recommendation_exclusion_reason"] = ""
        df.at[idx, "recommendation_confidence"] = "high"
        df.at[idx, "recommendation_item_type"] = "menu"
        df.at[idx, "ingredient_only_flag"] = "False"
        df.at[idx, "cleaning_action"] = "keep"
        df.at[idx, "cleaning_reason"] = ""
        df.at[idx, "meal_combo_valid"] = "True"
        if not was_recommendable:
            restored += 1
    return restored


def ensure_taxonomy_columns(df: pd.DataFrame) -> None:
    if "meal_component" not in df.columns:
        insert_at = df.columns.get_loc("food_category") + 1 if "food_category" in df.columns else len(df.columns)
        df.insert(insert_at, "meal_component", "")
    if "dish_type" not in df.columns:
        insert_at = df.columns.get_loc("cooking_category") + 1 if "cooking_category" in df.columns else len(df.columns)
        df.insert(insert_at, "dish_type", "")


def infer_dish_type(row: pd.Series) -> str:
    name = normalize_text(row.get("food_name", ""))
    cooking = normalize_text(row.get("cooking_category", ""))
    recommendation_type = normalize_text(row.get("recommendation_item_type", ""))
    raw_ingredient = str(row.get("raw_ingredient_flag", "")).strip().lower() == "true"
    ingredient_only = str(row.get("ingredient_only_flag", "")).strip().lower() == "true"

    if raw_ingredient or ingredient_only or recommendation_type == "ingredient":
        return "bahan_non_menu"
    if any(keyword in name for keyword in ["soto", "sop", "sup", "gulai", "kuah", "kari", "opor", "rawon", "laksa", "tekwan", "tongseng", "tengkleng", "lodeh", "pindang", "bubur"]):
        return "berkuah"
    if any(keyword in name for keyword in ["goreng", "bakwan", "perkedel", "rempeyek", "keripik", "kerupuk", "emping", "rengginang"]):
        return "gorengan"
    if any(keyword in name for keyword in ["bakar", "panggang", "sate"]):
        return "bakar_panggang"
    if "tumis" in name or "orek" in name:
        return "tumis"
    if any(keyword in name for keyword in ["rebus", "kukus", "pepes", "presto"]):
        return "rebus_kukus"
    if any(keyword in name for keyword in ["segar", "salad", "rujak"]) and "bumbu rujak" not in name:
        return "mentah_segar"
    if any(keyword in name for keyword in ["dodol", "kue", "biskuit", "cokelat", "permen", "nopia", "gemblong", "barongko", "bika", "bagea", "selai"]):
        return "jajanan_manis"
    if cooking == "berkuah":
        return "berkuah"
    if cooking == "gorengan":
        return "gorengan"
    if cooking == "bakar":
        return "bakar_panggang"
    if cooking == "tumis":
        return "tumis"
    if cooking == "rebus_kukus":
        return "rebus_kukus"
    if cooking == "mentah_segar":
        return "mentah_segar"
    if recommendation_type in {"snack", "sweet_snack"}:
        return "jajanan"
    return "olahan"


def infer_meal_component(row: pd.Series, dish_type: str) -> str:
    name = normalize_text(row.get("food_name", ""))
    role = normalize_text(row.get("meal_template_role", ""))
    pairing_role = normalize_text(row.get("pairing_role", ""))
    recommendation_type = normalize_text(row.get("recommendation_item_type", ""))
    base = normalize_text(row.get("base_ingredient", ""))
    tags = normalize_text(row.get("base_ingredient_tags", ""))

    if dish_type == "bahan_non_menu" or recommendation_type in {"ingredient", "excluded"}:
        return "bahan_non_menu"
    if dish_type == "gorengan" and (base in {"buah", "umbi", "sagu"} or "kacang" in base or "pisang" in name or "keripik" in name):
        return "snack"
    if role == "fruit" or pairing_role == "fruit" or base == "buah":
        return "buah"
    if role == "dairy" or pairing_role == "dairy" or base == "susu":
        return "minuman_susu"
    if role == "staple" or pairing_role == "staple" or base in {"beras", "gandum", "umbi", "singkong", "sagu"}:
        return "karbohidrat_utama"
    if role == "vegetable" or pairing_role == "vegetable" or base == "sayuran":
        return "sayuran"
    if base in {"ayam", "sapi", "ikan", "seafood", "telur", "kambing", "daging_lain", "unggas_lain"}:
        return "lauk_hewani"
    if base in {"kedelai", "kacang"}:
        return "lauk_nabati" if role in {"protein", "complete"} or "tahu" in name or "tempe" in name else "snack"
    if role == "complete" or pairing_role == "complete":
        if "beras" in tags or any(keyword in name for keyword in ["nasi", "lontong", "ketoprak", "gado-gado", "pecel"]):
            return "menu_lengkap"
        return "lauk_berkuah" if dish_type == "berkuah" else "menu_lengkap"
    if role == "side" or pairing_role == "side":
        return "snack"
    if role in {"snack", "sweet_snack"} or recommendation_type == "snack":
        return "snack"
    return "lainnya"


def apply_consistent_taxonomy(df: pd.DataFrame) -> None:
    ensure_taxonomy_columns(df)
    for idx, row in df.iterrows():
        dish_type = infer_dish_type(row)
        meal_component = infer_meal_component(row, dish_type)
        df.at[idx, "dish_type"] = dish_type
        df.at[idx, "meal_component"] = meal_component
        df.at[idx, "food_category"] = meal_component
        df.at[idx, "food_category_source"] = "consistent_meal_component_taxonomy_v1"


def curated_rows(df: pd.DataFrame) -> list[dict[str, str]]:
    columns = list(df.columns)
    existing_names = set(df["food_name_clean"].map(normalize_text))
    rows: list[dict[str, str]] = []
    offset = 1

    for food in NEW_FOODS:
        clean_name = normalize_text(food["food_name"])
        if clean_name in existing_names:
            continue

        row = base_row(columns)
        row["food_id"] = next_food_id(df["food_id"], offset)
        offset += 1
        row["food_name"] = food["food_name"]
        row["food_name_clean"] = clean_name
        row["calories_100g"] = format_float(food["calories"])
        row["protein_100g"] = format_float(food["protein"])
        row["fat_100g"] = format_float(food["fat"])
        row["carbohydrate_100g"] = format_float(food["carbohydrate"])
        row["calorie_macro_diff"] = macro_diff(food["calories"], food["protein"], food["fat"], food["carbohydrate"])
        row["image_url"] = food["image_url"]
        row["cooking_category"] = food["cooking_category"]
        row["main_ingredient"] = food["main_ingredient"]
        row["food_category"] = food["food_category"]
        row["base_ingredient"] = food["base_ingredient"]
        row["base_ingredient_tags"] = food["base_ingredient_tags"]
        row["meal_time_tags"] = food["meal_time_tags"]
        row["primary_meal_time"] = food["primary_meal_time"]
        row["menu_reference_match"] = "True"
        row["menu_reference_source"] = "wikimedia_commons_manual_curation"
        row["menu_reference_title"] = food["food_name"]
        row["menu_reference_category"] = food["food_category"]
        row["menu_reference_meal_time"] = food["primary_meal_time"]
        row["context_correction_notes"] = "added_as_real_food_menu_with_matching_image_and_macro_checked_nutrition"

        for allergen_column in [
            "contains_gluten",
            "contains_dairy",
            "contains_nuts",
            "contains_peanut",
            "contains_seafood",
            "contains_egg",
            "contains_soy",
        ]:
            if allergen_column in food:
                row[allergen_column] = food[allergen_column]

        allergen_count = sum(row[column] == "True" for column in row if column.startswith("contains_"))
        row["allergen_match_count"] = str(allergen_count)

        apply_meal_flags(row, food["meal_time_tags"])
        apply_pairing(row, food["meal_template_role"])
        rows.append(row)
        existing_names.add(clean_name)

    return rows


def apply_existing_field_corrections(df: pd.DataFrame) -> int:
    corrected = 0
    complete_pairing = {
        "pairing_group": "complete_menu",
        "pairing_role": "complete",
        "pairing_notes": "standalone_complete_menu",
        "pairing_suitability_notes": "complete_menu_all_meals",
        "recommendation_item_type": "menu",
        "meal_combo_valid": "True",
    }

    for clean_name, updates in FIELD_CORRECTIONS.items():
        mask = df["food_name_clean"].eq(clean_name)
        if not mask.any():
            continue

        final_updates = dict(updates)
        if updates.get("meal_template_role") == "complete":
            final_updates.update(complete_pairing)

        for column, value in final_updates.items():
            if column in df.columns:
                df.loc[mask, column] = value
        corrected += int(mask.sum())

    return corrected


def backfill_base_ingredients(df: pd.DataFrame) -> int:
    main_to_base = {
        "ayam": "ayam",
        "sapi": "sapi",
        "ikan": "ikan",
        "seafood": "seafood",
        "telur": "telur",
        "kedelai": "kedelai",
        "kacang": "kacang",
        "beras": "beras",
        "singkong": "singkong",
        "umbi": "umbi",
        "sayuran": "sayuran",
        "buah": "buah",
        "susu": "susu",
        "kambing": "kambing",
        "terigu": "gandum",
    }
    tag_overrides = {
        "terigu": "gandum|terigu",
    }

    corrected = 0
    for idx, row in df.iterrows():
        main = normalize_text(row.get("main_ingredient", ""))
        if main not in main_to_base:
            continue
        if not is_blank(row.get("base_ingredient", "")) and not is_blank(row.get("base_ingredient_tags", "")):
            continue

        base = main_to_base[main]
        if is_blank(row.get("base_ingredient", "")):
            df.at[idx, "base_ingredient"] = base
        if is_blank(row.get("base_ingredient_tags", "")):
            df.at[idx, "base_ingredient_tags"] = tag_overrides.get(main, base)
        corrected += 1

    return corrected


def backfill_meal_time_tags(df: pd.DataFrame) -> int:
    valid_tags = ["breakfast", "lunch", "dinner"]
    corrected = 0

    for idx, row in df.iterrows():
        if not is_blank(row.get("meal_time_tags", "")):
            continue

        meal_time = "" if pd.isna(row.get("meal_time", "")) else str(row.get("meal_time", "")).lower()
        tags = [tag for tag in valid_tags if re.search(rf"(?<![a-z]){tag}(?![a-z])", meal_time)]

        if not tags:
            tags = [
                tag
                for tag in valid_tags
                if str(row.get(f"suitable_{tag}", "")).strip().lower() in {"true", "1", "yes", "ya"}
            ]

        primary = normalize_text(row.get("primary_meal_time", ""))
        if not tags and primary in valid_tags:
            tags = [primary]

        if not tags:
            continue

        df.at[idx, "meal_time_tags"] = "|".join(tags)
        df.at[idx, "meal_time"] = ",".join(tags)
        for tag in valid_tags:
            df.at[idx, f"suitable_{tag}"] = str(tag in tags)
        if primary not in valid_tags:
            df.at[idx, "primary_meal_time"] = "lunch" if "lunch" in tags else tags[0]
        corrected += 1

    return corrected


def curate_dataset() -> pd.DataFrame:
    df = pd.read_csv(FINAL_DATASET_PATH, dtype=str).fillna("")
    df["food_name_clean"] = df["food_name_clean"].map(normalize_text)
    ensure_taxonomy_columns(df)

    corrected_fields = apply_existing_field_corrections(df)
    base_backfills = backfill_base_ingredients(df)
    meal_tag_backfills = backfill_meal_time_tags(df)

    fixed_images = 0
    for clean_name, image_url in IMAGE_REPLACEMENTS.items():
        mask = df["food_name_clean"].eq(clean_name)
        fixed_images += int(mask.sum())
        df.loc[mask, "image_url"] = image_url
        df.loc[mask, "image_url_status"] = "ok"
        df.loc[mask, "image_url_source"] = "manual_food_specific_wikimedia"
        df.loc[mask, "image_url_rule_version"] = IMAGE_RULE_VERSION
        note = "fixed_non_matching_chicken_placeholder_image"
        if "context_correction_notes" in df.columns:
            existing = df.loc[mask, "context_correction_notes"].astype(str)
            df.loc[mask, "context_correction_notes"] = existing.mask(existing.eq(""), note)

    renamed_items = apply_name_corrections(df)

    additions = curated_rows(df)
    if additions:
        df = pd.concat([df, pd.DataFrame(additions, columns=df.columns)], ignore_index=True)

    restored_items = restore_known_menu_items(df)
    excluded_items = apply_recommendation_exclusions(df)
    apply_consistent_taxonomy(df)

    df.to_csv(FINAL_DATASET_PATH, index=False)
    DASHBOARD_DATASET_PATH.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(FINAL_DATASET_PATH, DASHBOARD_DATASET_PATH)
    sync_image_access_report(df)

    print(f"fixed_images={fixed_images}")
    print(f"corrected_fields={corrected_fields}")
    print(f"base_backfills={base_backfills}")
    print(f"meal_tag_backfills={meal_tag_backfills}")
    print(f"renamed_items={renamed_items}")
    print(f"added_rows={len(additions)}")
    print(f"restored_items={restored_items}")
    print(f"excluded_items={excluded_items}")
    print(f"final_rows={len(df)}")
    print(f"updated={FINAL_DATASET_PATH}")
    print(f"synced={DASHBOARD_DATASET_PATH}")
    return df


def sync_image_access_report(df: pd.DataFrame) -> None:
    if not IMAGE_ACCESS_CHECK_PATH.exists():
        return

    report = pd.read_csv(IMAGE_ACCESS_CHECK_PATH, dtype=str).fillna("")
    report_by_id = {row["food_id"]: row.to_dict() for _, row in report.iterrows()}
    report_rows: list[dict[str, str]] = []

    for _, dataset_row in df.iterrows():
        food_id = dataset_row["food_id"]
        current = report_by_id.get(food_id, {}).copy()
        current.setdefault("food_id", food_id)
        current.setdefault("food_name", "")
        current.setdefault("image_url", "")
        current.setdefault("declared_status", "")
        current.setdefault("http_status", "")
        current.setdefault("content_type", "")
        current.setdefault("content_length", "")
        current.setdefault("access_status", "")
        current.setdefault("reason", "")

        image_changed = current["image_url"] != dataset_row["image_url"]
        manual_row = dataset_row.get("source", "") == CURATION_SOURCE
        if image_changed or manual_row:
            current.update(
                {
                    "food_id": food_id,
                    "food_name": dataset_row["food_name"],
                    "image_url": dataset_row["image_url"],
                    "declared_status": dataset_row.get("image_url_status", "ok"),
                    "http_status": "",
                    "content_type": "",
                    "content_length": "",
                    "access_status": "not_checked",
                    "reason": "manual_real_food_curation_not_live_checked",
                }
            )
        report_rows.append(current)

    synced = pd.DataFrame(report_rows, columns=report.columns)
    synced.to_csv(IMAGE_ACCESS_CHECK_PATH, index=False)

    summary = {
        "dataset": str(DASHBOARD_DATASET_PATH.relative_to(PROJECT_ROOT)),
        "rows_checked": int(len(synced)),
        "summary": {str(key): int(value) for key, value in synced["access_status"].value_counts(dropna=False).items()},
        "seconds": None,
        "output_csv": str(IMAGE_ACCESS_CHECK_PATH.relative_to(PROJECT_ROOT)),
        "notes": [
            "Report rows were synchronized after manual real-food curation.",
            "Rows with changed or newly added image URLs are marked not_checked until the live checker is rerun.",
        ],
    }
    IMAGE_ACCESS_SUMMARY_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")


if __name__ == "__main__":
    curate_dataset()
