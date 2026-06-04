# Ready-to-Use Data Science Dataset

Folder ini berisi dataset final dari tim Data Science yang sudah siap dipakai oleh tim AI Engineer dan Fullstack.

## File Utama

| File | Keterangan |
|---|---|
| `train_ready_dataset.csv` | Dataset makanan final berisi nutrisi per 100g, label alergen multi-label, konteks makanan, dan filter item siap rekomendasi. |
| `user_profile_features_schema.csv` | Schema fitur profil pengguna untuk perhitungan BMR/TDEE, target kalori, dan target makro. |
| `food_master_standardized.csv` | Food master bersih dari Orang A sebelum digabung dengan label alergen. |
| `merge_summary.csv` | Ringkasan hasil merge Orang A + Orang B. |
| `merge_metadata.json` | Metadata input/output proses merge. |
| `feature_enrichment_summary.csv` | Ringkasan distribusi kategori makanan, bahan dasar, dan waktu makan. |
| `feature_enrichment_metadata.json` | Metadata rule enrichment fitur konteks makanan. |
| `menu_ready_filter_summary.csv` | Ringkasan filter real-food/menu-ready. |
| `menu_ready_filter_metadata.json` | Metadata rule filter agar bahan mentah tidak masuk file utama dan rule status halal. |
| `train_ready_v6_sync_summary.csv` | Ringkasan sinkronisasi dataset final v6 dari update Data Science. |
| `train_ready_v6_sync_metadata.json` | Metadata sinkronisasi dataset final v6. |
| `image_url_refresh_report.csv` | Audit image URL yang diganti karena kosong/rusak/tidak bisa dibuka. |
| `image_url_refresh_metadata.json` | Metadata proses refresh image URL. |

## Kolom Penting `train_ready_dataset.csv`

- Identitas makanan: `food_id`, `food_name`, `food_name_clean`
- Nutrisi: `calories_100g`, `protein_100g`, `fat_100g`, `carbohydrate_100g`
- Label alergen: `contains_gluten`, `contains_dairy`, `contains_nuts`, `contains_peanut`, `contains_seafood`, `contains_egg`, `contains_soy`, `contains_celery`, `contains_mustard`, `contains_sesame`, `contains_sulfite`, `contains_other`, `contains_unknown`
- Kualitas label: `confidence`, `allergen_sources`, `label_sources`, `allergen_match_count`, `merge_status`
- Konteks makanan: `food_category`, `base_ingredient`, `suitable_breakfast`, `suitable_lunch`, `suitable_dinner`, `meal_time_tags`, `primary_meal_time`
- Referensi resep: `recipe_reference_match`, `recipe_reference_source`, `recipe_reference_title`, `recipe_ingredients_reference`
- Konteks dari update Orang A: `cooking_category`, `main_ingredient`, `meal_time`
- Filter siap rekomendasi: `is_recommendable_food`, `recommendation_item_type`, `recommendation_confidence`, `ingredient_only_flag`, `raw_ingredient_flag`, `recommendation_exclusion_reason`
- Status halal: `halal_status`, `is_halal_candidate`, `contains_non_halal_ingredient`, `non_halal_ingredient_tags`, `halal_review_reason`, `halal_confidence`
- Pairing makanan: `pairing_group`, `pairing_role`, `pairing_notes`, `pairing_suitability_notes`, `meal_template_role`, `meal_combo_valid`
- Kualitas gambar: `image_url_status`, `image_url_source`, `image_url_rule_version`

## Fitur Konteks Makanan

Fitur konteks ditambahkan agar rekomendasi tidak hanya memilih makanan dengan skor gizi tertinggi yang sama terus-menerus. AI Engineer dapat memakai:

- `food_category` untuk diversifikasi jenis makanan, misalnya `berkuah`, `gorengan`, `sayuran`, `lauk_hewani`, `lauk_nabati`, `buah`, dan lainnya.
- `base_ingredient` untuk variasi bahan dasar, misalnya `ayam`, `sapi`, `ikan`, `telur`, `kedelai`, `beras`, `umbi`, dan lainnya.
- `suitable_breakfast`, `suitable_lunch`, `suitable_dinner` sebagai filter multilabel waktu makan.
- `primary_meal_time` sebagai kelas utama jika model/API butuh satu label saja.
- `recipe_reference_match` untuk menandai makanan yang berhasil diperkaya dari dataset resep tambahan.
- `recommendation_item_type` untuk membedakan menu, sayur, buah, snack, minuman, staple, dan protein dish.
- `is_recommendable_food=True` pada file utama karena row bahan mentah/bumbu sudah dipisahkan di repo Data Science sebagai audit.
- `halal_status` untuk filter halal: `halal_candidate`, `non_halal`, atau `needs_review`.
- `is_halal_candidate=True` dapat dipakai untuk mode halal-only. Nilai ini adalah rule-based guardrail, bukan sertifikasi halal resmi.
- `pairing_group` dan `meal_template_role` membantu AI Engineer membuat kombinasi makanan yang tidak monoton.
- `image_url_status` hanya berisi `ok` atau `refreshed` pada dataset final v6.

Dataset tambahan yang dipakai untuk memperkuat fitur konteks:

- Indonesian Food Recipes Dataset.
- Indonesian Food Recipes by main ingredient.
- Global Cuisine Meals with Diet Labels.
- Recipes Dataset 64k Dishes.
- South Asian Recipes with Nutrition & Steps.
- Food and Vegetable Nutrition Dataset.
- Nutrition5k Dataset.

## Catatan Keamanan Alergi

Jika `contains_unknown=True`, makanan tersebut belum punya bukti label alergen yang cukup. Untuk mode conservative, makanan seperti ini sebaiknya tidak direkomendasikan kepada pengguna yang memiliki alergi kritis.

## Ringkasan Merge

```text
food_master_rows      : 1332
train_ready_rows      : 591
train_ready_columns   : 78
exact_name_rows       : 258
keyword_fallback_rows : 3
not_matched_rows      : 1071
conservative_unknown  : True
halal_candidate_rows  : 583
non_halal_or_review   : 4
needs_review_rows     : 4
image_url_ok          : 475
image_url_refreshed   : 116
```

## Update Terbaru

Versi terbaru memakai `food_master_terbaru.csv` dari update Orang A tanggal 26 Mei 2026. Kolom tambahan dari Orang A yang sudah masuk:

- `cooking_category`
- `main_ingredient`
- `meal_time`

Update filter menu-ready menurunkan file utama dari 1332 row menjadi 975 row rekomendasi. Bahan mentah, bumbu/kondimen, tepung/beras mentah, dan protein hewani mentah tidak masuk `train_ready_dataset.csv`.

Update status halal menandai keyword eksplisit seperti babi, anjing, dan alkohol sebagai `non_halal`. Item sensitif seperti penyu, paniki, katak, keong, dan kura-kura diberi `needs_review`.

Update v6 menyelaraskan dataset dengan versi terbaru dari Data Science teammate, menambahkan fitur pairing/meal combo, dan mengganti image URL rusak dengan fallback kategori yang dapat dibuka.
