# Final Data Scientist - NutriMatch

Folder ini adalah versi konsolidasi pekerjaan Data Science NutriMatch. Struktur lama `orang_a/` dan `orang_b/` tetap disimpan sebagai backup historis, tetapi folder ini menjadi rujukan baru untuk alur Data Science yang sudah disatukan.

## Tujuan

Menyatukan seluruh artefak Data Science dalam satu tempat:

- dataset original dan referensi sumber data,
- dataset processed,
- dataset final siap training/rekomendasi,
- notebook EDA dan eksperimen,
- script Python pipeline,
- dokumentasi teknis,
- dashboard audit,
- output evidence seperti grafik EDA dan metadata audit.

## Struktur Folder

```text
Final data scientist/
  00_project_docs/
  01_original_datasets/
    dataset_sources/
    raw_archives/
    new_datasets/
    orang_b_raw_datasets/
  02_processed_datasets/
    food_master/
    merge_intermediate/
  03_final_datasets/
    main/
    audit/
    metadata/
  04_notebooks/
    food_nutrition_profile/
    allergen_merge_enrichment/
    misc_final_dataset/
  05_scripts_python/
    pipeline/
  06_dashboard/
    streamlit_dashboard/
    static_html/
    publish_ready/
  07_outputs_evidence/
    eda_charts/
  08_integration_ready/
    web_app_ready_dataset/
```

## Alur Data Science Terpadu

```text
Dataset original dan referensi
  -> pembersihan food master nutrisi
  -> validasi kalori dan makronutrien
  -> pembuatan schema profil user, BMR, TDEE, target makro
  -> preprocessing alergen dan ingredient mapping
  -> merge food master + label alergen berbasis food_name_clean
  -> feature engineering konteks makanan
  -> halal guardrail
  -> filter menu-ready / real-food
  -> pairing dan meal template
  -> image URL validation dan refresh
  -> train_ready_dataset.csv
  -> dashboard audit dan dataset integrasi aplikasi
```

## Dataset Acuan

Dataset utama untuk nilai kalori dan makronutrien adalah Indonesian Food & Drink Nutrition Dataset. Dataset ini menjadi basis `food_master` karena memuat nama makanan Indonesia serta kolom nutrisi seperti kalori, protein, lemak, dan karbohidrat.

Dataset pendukung yang digunakan untuk validasi, enrichment, dan guardrail:

| Dataset / Referensi | Fungsi |
|---|---|
| Indonesian Food & Drink Nutrition Dataset | Acuan utama kalori dan makronutrien makanan lokal. |
| Food Ingredients and Allergens | Acuan ingredient dan label alergen. |
| Food Allergens and Allergies | Referensi taksonomi alergen. |
| Open Food Facts | Referensi produk, ingredient, label, dan nutrisi tambahan. |
| USDA FoodData Central | Pembanding nutrisi bahan makanan standar. |
| Comprehensive Weight Change Prediction Dataset | Referensi profil tubuh, aktivitas, dan konsep target energi. |
| Global Food & Nutrition Database 2026 | Referensi nutrisi global tambahan. |
| Recipe / dish ingredient datasets | Pengayaan konteks menu, bahan dasar, meal time, dan pairing. |

Link dan catatan sumber dataset disimpan di:

```text
01_original_datasets/dataset_sources/raw_dataset_links.md
```

## Dataset Processed

Folder `02_processed_datasets/food_master/` berisi output cleaning nutrisi:

- `food_master_clean.csv`
- `food_master_terbaru.csv`
- `user_profile_features_schema.csv`

Folder `02_processed_datasets/merge_intermediate/` berisi data antara untuk proses merge:

- `food_master_standardized.csv`
- `allergen_labels_aggregated.csv`

## Dataset Final

Folder `03_final_datasets/main/` berisi dataset utama:

- `train_ready_dataset.csv`
- `train_ready_dataset.xlsx`
- `user_profile_features_schema.csv`

Folder `03_final_datasets/audit/` berisi:

- `train_ready_dataset_full_audit.csv`

Folder `03_final_datasets/metadata/` berisi metadata dan ringkasan audit:

- `merge_summary.csv`
- `merge_metadata.json`
- `feature_enrichment_summary.csv`
- `feature_enrichment_metadata.json`
- `menu_ready_filter_summary.csv`
- `menu_ready_filter_metadata.json`
- `train_ready_v6_sync_summary.csv`
- `train_ready_v6_sync_metadata.json`
- `image_url_refresh_report.csv`
- `image_url_refresh_metadata.json`

## Notebook

Notebook pembersihan nutrisi, profil user, BMR/TDEE, feature engineering, dan EDA berada di:

```text
04_notebooks/food_nutrition_profile/
```

Notebook alergen, merge, dan eksperimen enrichment berada di:

```text
04_notebooks/allergen_merge_enrichment/
```

## Script Python Pipeline

Script utama berada di:

```text
05_scripts_python/pipeline/
```

Urutan umum regenerasi:

```bash
python orang_b_allergen_pipeline.py
python merge_orang_a_b.py
python enrich_ready_dataset_features.py
python build_menu_ready_train_dataset.py
python sync_train_ready_v6.py "C:\Users\Gateway\Downloads\train_ready_dataset_v6.csv"
python refresh_broken_image_urls.py
```

Catatan: script masih mempertahankan beberapa path historis dari struktur lama. Jika ingin menjalankan langsung dari folder ini, path input/output di script perlu disesuaikan terlebih dahulu.

## Feature Engineering Utama

| Kelompok fitur | Contoh kolom | Fungsi |
|---|---|---|
| Nutrisi | `calories_100g`, `protein_100g`, `fat_100g`, `carbohydrate_100g` | Dasar scoring kebutuhan gizi. |
| Kualitas nutrisi | `zero_calorie_flag`, `calorie_inconsistent_flag`, `calorie_macro_diff` | Audit data nutrisi tidak wajar. |
| Profil user | `bmr`, `tdee`, `target_calorie`, `protein_target_g`, `fat_target_g`, `carb_target_g` | Personalisasi target energi dan makro. |
| Alergen | `contains_gluten`, `contains_dairy`, `contains_peanut`, `contains_unknown` | Hard filter keamanan alergi sebelum ranking AI. |
| Konteks makanan | `food_category`, `base_ingredient`, `primary_meal_time`, `suitable_breakfast` | Membantu rekomendasi sesuai waktu makan dan jenis menu. |
| Halal guardrail | `halal_status`, `is_halal_candidate`, `contains_non_halal_ingredient` | Filter halal-only berbasis rule. |
| Menu-ready | `is_recommendable_food`, `recommendation_item_type`, `raw_ingredient_flag` | Mengeluarkan bahan mentah/bumbu dari dataset utama. |
| Pairing | `pairing_group`, `pairing_role`, `meal_template_role`, `meal_combo_valid` | Membantu komposisi meal plan lebih natural. |
| Media | `image_url`, `image_url_status`, `image_url_source` | Memastikan gambar dapat dipakai frontend/dashboard. |

## Dashboard

Dashboard Streamlit berada di:

```text
06_dashboard/streamlit_dashboard/
```

Cara menjalankan dari root project:

```bash
streamlit run "Final data scientist/06_dashboard/streamlit_dashboard/app.py"
```

Dashboard HTML statis berada di:

```text
06_dashboard/static_html/nutrimatch_data_science_dashboard.html
```

## Output untuk Integrasi Aplikasi

Dataset yang sudah disiapkan untuk aplikasi web disalin ke:

```text
08_integration_ready/web_app_ready_dataset/
```

Folder ini mengikuti isi `NutriMatch/data/ready/` dan bisa dipakai oleh backend/fullstack untuk integrasi rekomendasi.

## Catatan Penting

- Folder ini bersifat konsolidasi non-destruktif. Folder lama tidak dihapus agar histori kerja dan path lama tetap aman.
- `train_ready_dataset.csv` adalah dataset utama untuk AI/Backend.
- `train_ready_dataset_full_audit.csv` dipakai untuk audit, debugging, dan melihat item yang dikeluarkan.
- Label halal adalah guardrail rule-based, bukan sertifikasi halal resmi.
- Label alergen harus dipakai sebagai hard filter sebelum ranking AI.
- Nilai `contains_unknown` sebaiknya diperlakukan konservatif untuk pengguna dengan alergi kritis.
