# Dokumentasi Teknis Data Science NutriMatch

## 1. Informasi Dokumen

| Atribut | Nilai |
|---|---|
| Nama proyek | NutriMatch |
| Jenis dokumen | Dokumentasi Teknis Data Science |
| Pemilik | Tim Data Science |
| Target pembaca | AI Engineer, Backend Engineer, Fullstack Engineer, Product Team |
| Terakhir diperbarui | 2026-06-04 |
| Versi | v2.1 - Handover final workspace DBD |

Dokumen ini menjadi rujukan teknis untuk pekerjaan Data Science NutriMatch: pembersihan data nutrisi, skema profil pengguna, pemetaan alergen, enrichment konteks makanan, guardrail halal, filter menu-ready, validasi gambar, dan dashboard audit.

## 2. Ringkasan Proyek

NutriMatch adalah sistem rekomendasi makanan yang menyesuaikan menu dengan kebutuhan nutrisi, tujuan diet, batasan alergi, preferensi halal, dan konteks waktu makan pengguna. Tanggung jawab Data Science adalah menyiapkan dataset yang bersih, kaya fitur, dan aman dipakai oleh AI Engineer untuk training, filtering, ranking, dan audit rekomendasi.

Output utama adalah:

```text
orang_b/final_datasets/train_ready_dataset.csv
```

Dataset ini berisi makanan yang layak direkomendasikan secara langsung kepada pengguna. Dataset sudah diperkaya dengan nilai nutrisi per 100 gram, label alergen multi-label, status halal rule-based, kategori makanan, bahan dasar, kecocokan waktu makan, pairing role, meal template role, serta status image URL.

## 3. Ruang Lingkup

Pekerjaan yang masuk ruang lingkup Data Science:

- Membersihkan food master dan menstandarkan fitur nutrisi.
- Menyiapkan skema profil pengguna untuk BMR, TDEE, target kalori, dan target makro.
- Membuat label alergen multi-label dengan mode konservatif.
- Menggabungkan output Orang A dan Orang B.
- Menambahkan fitur konteks makanan dari nama makanan dan referensi resep.
- Membuat guardrail halal berbasis rule.
- Memfilter bahan mentah, bumbu, kondimen, dan item tidak layak rekomendasi.
- Menyinkronkan update teammate v6.
- Memvalidasi dan memperbarui image URL yang rusak.
- Menyediakan dashboard audit interaktif berbasis Streamlit.

Di luar ruang lingkup Data Science:

- Deployment model AI ke server produksi.
- Integrasi API backend.
- Pengembangan UI mobile.
- Sertifikasi halal resmi.
- Klaim medis definitif atas alergi atau status nutrisi.

## 4. Struktur Workspace

Struktur repo yang dipakai saat ini:

```text
DBD/
  orang_a/
    nutrimatch-capstone-dsA/
      data/processed/
      notebooks/
      output/
    notebooks/

  orang_b/
    dataset_sources/
    docs/
    notebooks/
    scripts_python/
    final_datasets/
    dashboard/

  streamlit_dashboard/
    app.py
    data/train_ready_dataset.csv
    requirements.txt

  new datasets/
  requirements.txt
  README.md
```

Pembagian tanggung jawab:

| Area | Tanggung jawab |
|---|---|
| `orang_a/` | Food master, pembersihan nutrisi, validasi kalori/makro, user profile schema, BMR/TDEE, target makro, dan EDA. |
| `orang_b/` | Alergen, ingredient mapping, merge, enrichment konteks makanan, halal guardrail, filter menu-ready, pairing, image refresh, dan dataset final. |
| `streamlit_dashboard/` | Dashboard Streamlit yang membaca salinan dataset final untuk audit dan deployment cepat. |
| `new datasets/` | Referensi dataset tambahan lokal untuk resep, ingredient, menu reference, dan nutrisi tambahan. |

## 5. Artefak Final

File utama yang perlu diserahkan ke AI/Backend/Fullstack:

| File | Fungsi |
|---|---|
| `orang_b/final_datasets/train_ready_dataset.csv` | Dataset utama untuk training, filtering, ranking, dan rekomendasi. |
| `orang_b/final_datasets/train_ready_dataset_full_audit.csv` | Dataset audit lengkap berisi item diterima dan ditolak beserta alasan eksklusi. |
| `orang_b/final_datasets/user_profile_features_schema.csv` | Skema fitur profil pengguna dari Orang A. |
| `orang_b/final_datasets/merge_summary.csv` | Ringkasan hasil merge food master dan label alergen. |
| `orang_b/final_datasets/merge_metadata.json` | Metadata input/output proses merge. |
| `orang_b/final_datasets/feature_enrichment_summary.csv` | Ringkasan distribusi fitur konteks. |
| `orang_b/final_datasets/feature_enrichment_metadata.json` | Metadata rule enrichment konteks makanan. |
| `orang_b/final_datasets/menu_ready_filter_summary.csv` | Ringkasan filter item menu-ready. |
| `orang_b/final_datasets/menu_ready_filter_metadata.json` | Metadata filter menu-ready dan halal guardrail. |
| `orang_b/final_datasets/train_ready_v6_sync_summary.csv` | Ringkasan sinkronisasi update teammate v6. |
| `orang_b/final_datasets/train_ready_v6_sync_metadata.json` | Metadata sinkronisasi update v6. |
| `orang_b/final_datasets/image_url_refresh_report.csv` | Laporan image URL yang diperiksa/diperbarui. |
| `orang_b/final_datasets/image_url_refresh_metadata.json` | Metadata proses refresh image URL. |

State dataset aktif per 2026-06-04:

| Dataset | Rows | Columns | Catatan |
|---|---:|---:|---|
| `train_ready_dataset.csv` | 484 | 80 | File aktif yang juga disalin ke dashboard Streamlit. |
| `train_ready_dataset_full_audit.csv` | 1332 | 75 | File audit lengkap dengan item yang diterima/ditolak. |
| `streamlit_dashboard/data/train_ready_dataset.csv` | 484 | 80 | Salinan dataset untuk dashboard. |

Catatan penting: beberapa metadata historis masih mencatat angka tahap sebelumnya, misalnya sync v6 di 591 rows/75 columns dan image refresh di 591 rows. Untuk laporan final, gunakan angka dari CSV aktif jika terdapat perbedaan.

## 6. Data Processing Pipeline

Alur besar pipeline:

```text
Food master Orang A
  -> cleaning nutrisi dan food_name_clean
  -> user profile schema
  -> preprocessing alergen Orang B
  -> merge berbasis food_name_clean
  -> enrichment kategori, ingredient, meal time
  -> filter menu-ready dan raw ingredient
  -> halal guardrail
  -> sync update v6
  -> refresh image URL
  -> dataset final + dashboard audit
```

Skrip utama:

| Skrip | Fungsi |
|---|---|
| `orang_b/scripts_python/orang_b_allergen_pipeline.py` | Membersihkan dan mengagregasi label alergen. |
| `orang_b/scripts_python/merge_orang_a_b.py` | Menggabungkan food master Orang A dengan label alergen Orang B. |
| `orang_b/scripts_python/enrich_ready_dataset_features.py` | Menambahkan kategori makanan, bahan dasar, dan waktu makan. |
| `orang_b/scripts_python/build_menu_ready_train_dataset.py` | Memfilter item yang layak menjadi menu rekomendasi. |
| `orang_b/scripts_python/curate_real_food_dataset.py` | Kurasi tambahan untuk real-food/menu-ready. |
| `orang_b/scripts_python/sync_train_ready_v6.py` | Menyinkronkan update teammate v6, terutama pairing dan cleaning action. |
| `orang_b/scripts_python/refresh_broken_image_urls.py` | Mengecek dan mengganti image URL kosong/rusak. |
| `orang_b/scripts_python/build_interactive_dashboard.py` | Membuat dashboard HTML statis di `orang_b/dashboard/`. |

## 7. Orang A: Nutrisi dan Profil Pengguna

Fokus Orang A adalah menyiapkan dasar nutrisi dan fitur profil pengguna.

Output penting:

```text
orang_a/nutrimatch-capstone-dsA/data/processed/food_master_clean.csv
orang_a/nutrimatch-capstone-dsA/data/processed/user_profile_features_schema.csv
orang_a/nutrimatch-capstone-dsA_20260526/nutrimatch-capstone-dsA/data/processed/food_master_terbaru.csv
```

Fitur dan validasi utama:

- `food_id`, `food_name`, `food_name_clean`.
- `calories_100g`, `protein_100g`, `fat_100g`, `carbohydrate_100g`.
- `zero_calorie_flag`.
- `calorie_inconsistent_flag`.
- `calorie_macro_diff`.
- `cooking_category`, `main_ingredient`, `meal_time`.
- Notebook EDA untuk distribusi kalori, top foods, quality audit, profil user, dan korelasi.

Skema profil pengguna:

- `age`
- `gender`
- `height_cm`
- `weight_kg`
- `activity_level`
- `goal`
- `bmr`
- `tdee`
- `target_calorie`
- `protein_target_g`
- `fat_target_g`
- `carb_target_g`
- `allergy_vector`

Prinsip BMR/TDEE:

```text
TDEE = BMR x activity_multiplier
target_calorie = TDEE +/- goal_adjustment
```

Target makro diturunkan dari target kalori, dengan protein dan lemak sebagai kebutuhan prioritas, lalu karbohidrat sebagai sisa energi yang masih sesuai target.

## 8. Orang B: Alergen, Konteks, Halal, dan Dataset Final

Fokus Orang B adalah menjadikan food master siap dipakai sistem rekomendasi.

Tanggung jawab utama:

- Menstandarkan label alergen.
- Membuat one-hot-like allergen columns.
- Menentukan `confidence`, `allergen_sources`, dan `label_sources`.
- Menggabungkan data dengan food master lewat `food_name_clean`.
- Menambahkan konteks makanan dan referensi resep.
- Menentukan `is_recommendable_food`.
- Menentukan `halal_status` dan `is_halal_candidate`.
- Menambahkan pairing dan meal template.
- Mengganti image URL yang invalid.

## 9. Alergen dan Guardrail Medis

Kolom alergen utama:

```text
contains_gluten
contains_dairy
contains_nuts
contains_peanut
contains_seafood
contains_egg
contains_soy
contains_celery
contains_mustard
contains_sesame
contains_sulfite
contains_other
contains_unknown
```

Nilai `confidence`:

| Nilai | Makna |
|---|---|
| `high` | Label eksplisit dari dataset/tag alergen. |
| `medium` | Match dari ingredient/product text yang cukup kuat. |
| `low` | Sinyal keyword fallback. |
| `unknown` | Tidak ada bukti cukup; diperlakukan konservatif. |

Aturan backend yang wajib dipakai:

```text
Jika user memiliki alergi X dan contains_X == true:
  buang item sebelum ranking AI

Jika conservative_mode == true dan contains_unknown == true:
  buang item atau kirim ke review manual
```

Model AI tidak boleh menimpa hard filter alergi. Dalam konteks alergi, false negative lebih berbahaya daripada false positive.

## 10. Feature Engineering Konteks Makanan

Kolom konteks yang ditambahkan:

| Kolom | Fungsi |
|---|---|
| `food_category` | Kategori makanan seperti lauk, sayur, buah, minuman, snack, gorengan, berkuah, atau lainnya. |
| `meal_component` | Komponen umum dalam susunan makanan. |
| `base_ingredient` | Bahan dasar utama seperti ayam, sapi, ikan, seafood, telur, beras, gandum, sayur, buah. |
| `base_ingredient_tags` | Tag bahan dasar multi-label. |
| `recipe_reference_match` | Penanda apakah item cocok dengan referensi resep. |
| `recipe_ingredients_reference` | Referensi ingredient dari dataset resep tambahan. |
| `suitable_breakfast` | Cocok untuk sarapan. |
| `suitable_lunch` | Cocok untuk makan siang. |
| `suitable_dinner` | Cocok untuk makan malam. |
| `meal_time_tags` | Gabungan label waktu makan. |
| `primary_meal_time` | Waktu makan utama: breakfast, lunch, dinner, atau snack sesuai rule. |
| `feature_rule_version` | Versi rule enrichment. |

Fitur ini membantu AI Engineer mencegah rekomendasi yang monoton, misalnya hanya memilih makanan berprotein tinggi tanpa variasi pairing atau waktu makan.

## 11. Menu-ready Filter

Dataset utama hanya boleh berisi item yang wajar ditampilkan sebagai rekomendasi makanan.

Kolom penting:

- `is_recommendable_food`
- `recommendation_item_type`
- `recommendation_confidence`
- `recommendation_exclusion_reason`
- `ingredient_only_flag`
- `raw_ingredient_flag`
- `cleaning_action`
- `cleaning_reason`

Item yang dikeluarkan dari `train_ready_dataset.csv` dan tetap disimpan di audit:

- Bahan mentah murni.
- Bumbu dan kondimen.
- Tepung, beras mentah, dan bahan staple mentah.
- Protein hewani mentah.
- Item yang tidak masuk akal direkomendasikan sebagai menu mandiri.

Metadata `menu_ready_filter_metadata.json` mencatat bahwa tahap filter pernah memproses 1332 baris audit, 975 baris recommendable, dan 357 baris non-recommendable sebelum sinkronisasi/update lanjutan.

## 12. Guardrail Halal

Status halal bersifat rule-based, bukan sertifikasi halal resmi.

Kolom halal:

| Kolom | Fungsi |
|---|---|
| `halal_status` | Status rule-based: `halal_candidate`, `non_halal`, `needs_review`, atau status gabungan review pada data aktif. |
| `is_halal_candidate` | Boolean untuk filter halal-only. |
| `contains_non_halal_ingredient` | True jika terdeteksi keyword non-halal eksplisit. |
| `non_halal_ingredient_tags` | Tag alasan, misalnya pork, dog, atau alcohol. |
| `halal_review_reason` | Alasan review manual untuk item sensitif/ambigu. |
| `halal_confidence` | Tingkat keyakinan rule. |
| `halal_rule_version` | Versi rule halal. |

Distribusi dataset aktif:

| `halal_status` | Jumlah |
|---|---:|
| `halal_candidate` | 483 |
| `non_halal_or_review` | 1 |

Aturan backend untuk halal-only:

```text
Jika user memilih halal-only:
  izinkan hanya item dengan is_halal_candidate == true
  buang item non_halal, needs_review, atau non_halal_or_review
```

## 13. Pairing dan Meal Template

Kolom pairing ditambahkan dari update v6:

- `pairing_group`
- `pairing_role`
- `pairing_notes`
- `pairing_suitability_notes`
- `meal_template_role`
- `meal_combo_valid`

Tujuannya adalah membantu sistem membuat kombinasi makanan yang lebih natural, misalnya menggabungkan karbohidrat pokok, lauk protein, sayur, minuman, dan snack secara proporsional.

## 14. Image URL Validation

Kolom gambar:

- `image_url`
- `image_url_status`
- `image_url_source`
- `image_url_rule_version`

Distribusi dataset aktif:

| `image_url_status` | Jumlah |
|---|---:|
| `ok` | 411 |
| `refreshed` | 73 |

Catatan metadata historis: proses `google_image_refresh_v1` pernah memeriksa 591 baris, menemukan 116 broken URLs, memperbarui 116 baris, dan menyisakan 0 item `needs_review`. Pada CSV aktif, jumlah baris sudah berubah menjadi 484 karena update/kurasi lanjutan.

## 15. Dashboard Audit

Ada dua bentuk dashboard:

| Lokasi | Fungsi |
|---|---|
| `streamlit_dashboard/app.py` | Dashboard Streamlit interaktif untuk deploy/local run. |
| `orang_b/dashboard/nutrimatch_data_science_dashboard.html` | Dashboard HTML statis hasil build. |

Dashboard Streamlit membaca:

```text
streamlit_dashboard/data/train_ready_dataset.csv
```

Cara menjalankan lokal dari root repo:

```bash
streamlit run streamlit_dashboard/app.py
```

Untuk deploy Streamlit Cloud:

- Repo dipush ke GitHub.
- Main file path: `streamlit_dashboard/app.py`.
- Dataset yang dibaca: `streamlit_dashboard/data/train_ready_dataset.csv`.
- Jika path dataset berubah, set environment variable `NUTRIMATCH_DATASET_PATH`.

Fitur dashboard:

- KPI jumlah baris/kolom dan coverage kualitas.
- Distribusi halal status.
- Distribusi meal time.
- Distribusi pairing group dan meal template role.
- Food explorer dengan search/filter.
- Audit image URL status.

## 16. Cara Reproduksi Dataset

Jalankan dari folder `orang_b/`:

```bash
python scripts_python/orang_b_allergen_pipeline.py
python scripts_python/merge_orang_a_b.py
python scripts_python/enrich_ready_dataset_features.py
python scripts_python/build_menu_ready_train_dataset.py
python scripts_python/sync_train_ready_v6.py "C:\Users\Gateway\Downloads\train_ready_dataset_v6.csv"
python scripts_python/refresh_broken_image_urls.py
```

Jika hanya ingin membangun ulang dashboard HTML statis:

```bash
python scripts_python/build_interactive_dashboard.py
```

Setelah dataset final berubah, salin/sinkronkan dataset ke dashboard Streamlit:

```text
orang_b/final_datasets/train_ready_dataset.csv
-> streamlit_dashboard/data/train_ready_dataset.csv
```

## 17. QA Checklist

Sebelum dataset diberikan ke AI Engineer, pastikan:

- `food_id` tidak duplikat.
- `food_name` dan `food_name_clean` tidak kosong.
- Kolom nutrisi utama numerik dan tidak null.
- Kolom alergen hanya berisi nilai boolean/unknown yang konsisten.
- `contains_unknown` diperlakukan konservatif untuk user alergi.
- `halal_status` hanya memakai status yang dikenali backend.
- `is_halal_candidate` dipakai sebagai filter halal-only.
- `is_recommendable_food == true` untuk semua baris di dataset utama.
- Item bahan mentah/bumbu masuk audit, bukan dataset rekomendasi utama.
- `image_url_status` tidak menyisakan broken/invalid tanpa catatan.
- `streamlit_dashboard/data/train_ready_dataset.csv` sudah sinkron dengan dataset final jika dashboard akan dideploy.

## 18. Handover untuk AI Engineer

Urutan rekomendasi yang disarankan:

```text
Input profil pengguna
  -> hitung BMR/TDEE dan target makro
  -> hard filter alergi
  -> hard filter halal/diet preference
  -> filter konteks waktu makan
  -> ranking model AI
  -> diversifikasi pairing
  -> hasil rekomendasi final
```

Prinsip implementasi:

- Alergi wajib menjadi hard filter sebelum model ranking.
- `contains_unknown` harus dibuang pada conservative mode.
- Halal-only hanya boleh memakai `is_halal_candidate == true`.
- `primary_meal_time` dan `suitable_*` dipakai untuk konteks meal plan.
- `pairing_group`, `pairing_role`, dan `meal_template_role` dipakai untuk menjaga kombinasi makanan tetap natural.
- `image_url_status` dipakai frontend untuk menghindari broken image.

## 19. Risiko dan Keterbatasan

- Status halal masih rule-based dan bukan sertifikasi resmi.
- Banyak makanan lokal tidak memiliki ingredient list eksplisit.
- Label alergen dari dataset publik/crowdsourced perlu validasi manual untuk kasus kritis.
- `contains_unknown` dapat mengurangi jumlah rekomendasi dalam conservative mode.
- URL gambar bergantung pada sumber eksternal dan bisa berubah sewaktu-waktu.
- Dataset tambahan tidak selalu berada pada basis nutrisi per 100 gram yang sama, sehingga sebagian hanya dipakai sebagai sinyal referensi, bukan ditambahkan sebagai baris baru.
- Metadata historis bisa berbeda dari CSV aktif karena ada beberapa tahap sync dan kurasi.

## 20. Peningkatan Lanjutan

Rekomendasi berikutnya:

- Tambahkan unit test `pytest` untuk schema, null check, enum check, dan duplicate check.
- Buat data dictionary lengkap untuk 80 kolom aktif.
- Pisahkan metadata historis dan metadata current-state agar tidak membingungkan saat handover.
- Tambahkan human-in-the-loop review untuk alergen unknown dan halal needs-review.
- Gunakan DVC atau cloud storage untuk versioning dataset besar.
- Buat pipeline sync otomatis dari `orang_b/final_datasets/` ke `streamlit_dashboard/data/`.
- Tambahkan telemetry/feedback loop dari pengguna untuk memperbaiki ranking rekomendasi.

## 21. Kesimpulan

Dataset NutriMatch sudah berada pada tahap siap handover untuk AI Engineer dan Fullstack. File utama `train_ready_dataset.csv` sudah berisi nutrisi, alergen, konteks makanan, halal guardrail, pairing, dan status gambar. Prinsip utama yang harus dijaga adalah: model AI boleh melakukan ranking, tetapi tidak boleh melewati guardrail alergi dan filter keselamatan pengguna.
