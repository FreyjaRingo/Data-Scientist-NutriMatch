# Dokumentasi Teknis Data Science NutriMatch

## 1. Informasi Dokumen

| Atribut | Nilai |
|---|---|
| Nama proyek | NutriMatch |
| Jenis dokumen | Dokumentasi Teknis Data Science |
| Workspace acuan Data Science | `Final data scientist` |
| Repo aplikasi acuan | `../NutriMatch` |
| Pemilik | Tim Data Science |
| Target pembaca | AI Engineer, Backend Engineer, Fullstack Engineer, Product Team |
| Terakhir diperbarui | 2026-06-05 |
| Versi | v4.0 - disesuaikan dengan workspace DS dan repo aplikasi `NutriMatch` hasil pull GitHub |

Dokumen ini adalah rujukan teknis untuk folder Data Science NutriMatch yang sudah dikonsolidasikan dan repo aplikasi `NutriMatch` hasil pull GitHub. Fokusnya adalah menjelaskan dataset, pipeline, fitur, guardrail, dashboard, artefak integration-ready, serta cara dataset Data Science dikonsumsi oleh aplikasi Next.js.

## 2. Ringkasan Eksekutif

NutriMatch membutuhkan dataset makanan yang bisa dipakai untuk rekomendasi personal berdasarkan kebutuhan nutrisi, tujuan diet, alergi, preferensi halal, waktu makan, dan variasi menu. Folder `Final data scientist` menyimpan versi konsolidasi pekerjaan Data Science: data mentah, data olahan, dataset final, notebook, pipeline Python, dashboard audit, evidence, dan paket dataset yang siap diberikan ke tim aplikasi.

Output utama saat ini adalah:

```text
03_final_datasets/main/train_ready_dataset.csv
```

Dataset aktif berisi **484 baris** dan **80 kolom**. Dataset audit lengkap berada di:

```text
03_final_datasets/audit/train_ready_dataset_full_audit.csv
```

Dataset audit berisi **1332 baris** dan **75 kolom**. Untuk integrasi aplikasi, salinan dataset dan metadata yang siap dipakai berada di dua lokasi:

```text
08_integration_ready/web_app_ready_dataset/
../NutriMatch/data/ready/
```

Kedua lokasi tersebut saat ini memiliki `train_ready_dataset.csv` dengan ukuran aktif yang sama, yaitu 484 baris dan 80 kolom.

## 3. Struktur Workspace Saat Ini

Folder utama yang menjadi acuan teknis adalah:

| Folder | Fungsi |
|---|---|
| `00_project_docs/` | Dokumentasi proyek, technical report, deployment notes, checklist, ringkasan feature engineering, dan project plan. |
| `01_original_datasets/` | Dataset mentah dan referensi sumber data. |
| `02_processed_datasets/` | Hasil cleaning food master dan data antara untuk proses merge. |
| `03_final_datasets/` | Dataset final, audit, dan metadata. |
| `04_notebooks/` | Notebook pembersihan, EDA, feature engineering, alergi, dan eksperimen merge. |
| `05_scripts_python/pipeline/` | Script Python untuk menjalankan pipeline data. |
| `06_dashboard/` | Dashboard Streamlit, dashboard HTML statis, dan versi publish-ready. |
| `07_outputs_evidence/` | Grafik EDA dan bukti visual hasil analisis. |
| `08_integration_ready/web_app_ready_dataset/` | Paket dataset dan metadata yang disiapkan untuk AI Engineer, Backend Engineer, dan Fullstack Engineer. |

## 4. Struktur Repo Aplikasi NutriMatch

Repo aplikasi hasil pull GitHub berada satu level di atas folder ini:

```text
../NutriMatch/
```

Struktur penting repo aplikasi:

| Path | Fungsi |
|---|---|
| `src/app/` | Route Next.js App Router untuk halaman dan API. |
| `src/app/api/profile/route.ts` | API profil user, penyimpanan alergi, dan perhitungan BMR/TDEE/target kalori. |
| `src/app/api/allergens/route.ts` | API daftar alergen untuk pilihan onboarding. |
| `src/app/api/meal-recommendation/route.ts` | API rekomendasi meal plan tanpa menyimpan meal plan penuh. |
| `src/app/api/meal-plan/route.ts` | API membuat dan membaca meal plan yang disimpan ke database. |
| `src/lib/nutrition.ts` | Rumus BMR, TDEE, dan target kalori. |
| `src/lib/ai/recommendationClient.ts` | Kontrak request/response ke service AI recommendation. |
| `src/lib/recommendationPayload.ts` | Payload rekomendasi dari UI dan pilihan preferensi user. |
| `src/lib/mealPlanGenerator.ts` | Local fallback meal planner berbasis database Prisma. |
| `prisma/schema.prisma` | Schema database Supabase/PostgreSQL. |
| `prisma/seed.ts` | Seed sample food dan allergen untuk database. |
| `data/ready/` | Salinan dataset final Data Science untuk integrasi aplikasi. |
| `documentation/` | Koleksi Postman dan dokumen pendukung API. |

Stack aplikasi:

- Next.js 16
- React 19
- TypeScript
- Tailwind CSS
- Supabase Auth
- PostgreSQL melalui Prisma
- AI recommendation service eksternal

Environment penting dari `.env.example`:

- `DATABASE_URL`
- `DIRECT_URL`
- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- `NUTRIMATCH_AI_API_URL`
- `NUTRIMATCH_AI_TIMEOUT_MS`
- `ENABLE_MEAL_FALLBACK`

## 5. Artefak Final yang Harus Dipakai

Dataset utama:

- `03_final_datasets/main/train_ready_dataset.csv`
- `03_final_datasets/main/train_ready_dataset.xlsx`
- `03_final_datasets/main/user_profile_features_schema.csv`

Dataset audit:

- `03_final_datasets/audit/train_ready_dataset_full_audit.csv`

Metadata final:

- `03_final_datasets/metadata/merge_summary.csv`
- `03_final_datasets/metadata/merge_metadata.json`
- `03_final_datasets/metadata/feature_enrichment_summary.csv`
- `03_final_datasets/metadata/feature_enrichment_metadata.json`
- `03_final_datasets/metadata/menu_ready_filter_summary.csv`
- `03_final_datasets/metadata/menu_ready_filter_metadata.json`
- `03_final_datasets/metadata/train_ready_v6_sync_summary.csv`
- `03_final_datasets/metadata/train_ready_v6_sync_metadata.json`
- `03_final_datasets/metadata/image_url_refresh_report.csv`
- `03_final_datasets/metadata/image_url_refresh_metadata.json`

Paket integrasi aplikasi:

- `08_integration_ready/web_app_ready_dataset/train_ready_dataset.csv`
- `08_integration_ready/web_app_ready_dataset/user_profile_features_schema.csv`
- `08_integration_ready/web_app_ready_dataset/food_master_standardized.csv`
- `08_integration_ready/web_app_ready_dataset/*.json` dan `*.csv` metadata pendukung
- `../NutriMatch/data/ready/train_ready_dataset.csv`
- `../NutriMatch/data/ready/user_profile_features_schema.csv`
- `../NutriMatch/data/ready/*.json` dan `*.csv` metadata pendukung

Catatan penting: jika metadata historis menunjukkan angka yang berbeda, gunakan angka dari CSV aktif sebagai rujukan laporan final.

## 6. State Dataset Aktif

Ringkasan `train_ready_dataset.csv`:

| Metrik | Nilai |
|---|---:|
| Jumlah baris | 484 |
| Jumlah kolom | 80 |
| `halal_candidate` | 483 |
| `non_halal_or_review` | 1 |
| `image_url_status = ok` | 411 |
| `image_url_status = refreshed` | 73 |
| `primary_meal_time = lunch` | 451 |
| `primary_meal_time = breakfast` | 19 |
| `primary_meal_time = dinner` | 14 |

Ringkasan audit dataset:

| Metrik | Nilai |
|---|---:|
| Jumlah baris | 1332 |
| Jumlah kolom | 75 |

Interpretasi: file utama hanya berisi item yang sudah melewati kurasi menu-ready, sedangkan file audit menyimpan cakupan yang lebih lengkap untuk debugging, evaluasi, dan penelusuran item yang dikeluarkan.

Catatan untuk repo aplikasi: file `../NutriMatch/data/ready/README.md` masih memuat ringkasan historis 591 baris dan 78 kolom. Untuk laporan final dan integrasi aktual, gunakan angka dari CSV aktif, yaitu 484 baris dan 80 kolom.

## 7. Alur Data Science Terpadu

```text
Dataset original dan referensi sumber data
  -> cleaning food master dan standarisasi nama makanan
  -> validasi nutrisi per 100 g
  -> pembuatan schema profil user
  -> preprocessing ingredient dan label alergen
  -> merge food master dengan label alergen berbasis food_name_clean
  -> feature engineering kategori makanan, bahan dasar, dan waktu makan
  -> guardrail halal berbasis rule
  -> filter menu-ready agar bahan mentah/bumbu tidak masuk rekomendasi utama
  -> pairing dan meal template untuk variasi menu
  -> validasi dan refresh image URL
  -> train_ready_dataset.csv
  -> dashboard audit dan paket integration-ready
```

## 8. Pipeline Python

Script utama berada di:

```text
05_scripts_python/pipeline/
```

Urutan umum pipeline:

1. `orang_b_allergen_pipeline.py`
2. `merge_orang_a_b.py`
3. `enrich_ready_dataset_features.py`
4. `build_menu_ready_train_dataset.py`
5. `sync_train_ready_v6.py`
6. `refresh_broken_image_urls.py`
7. `build_interactive_dashboard.py`

Catatan operasional: beberapa script masih dapat membawa path historis dari struktur lama. Jika pipeline dijalankan langsung dari folder `Final data scientist`, cek dan sesuaikan path input/output terlebih dahulu agar mengarah ke `01_original_datasets`, `02_processed_datasets`, `03_final_datasets`, `06_dashboard`, dan `08_integration_ready`.

## 9. Sumber Data

Dataset utama untuk nutrisi makanan lokal adalah Indonesian Food & Drink Nutrition Dataset. Dataset pendukung dipakai untuk validasi, enrichment, ingredient mapping, dan guardrail:

- Food Ingredients and Allergens
- Food Allergens and Allergies
- Open Food Facts
- USDA FoodData Central
- Comprehensive Weight Change Prediction Dataset
- Global Food & Nutrition Database 2026
- Recipe dan dish ingredient datasets

Sumber lengkap dan catatan link berada di:

```text
01_original_datasets/dataset_sources/raw_dataset_links.md
```

## 10. Kolom Penting Dataset Utama

Identitas makanan:

- `food_id`
- `food_name`
- `food_name_clean`

Nutrisi per 100 g:

- `calories_100g`
- `protein_100g`
- `fat_100g`
- `carbohydrate_100g`

Kualitas nutrisi:

- `zero_calorie_flag`
- `calorie_inconsistent_flag`
- `calorie_macro_diff`

Alergen:

- `contains_gluten`
- `contains_dairy`
- `contains_nuts`
- `contains_peanut`
- `contains_seafood`
- `contains_egg`
- `contains_soy`
- `contains_celery`
- `contains_mustard`
- `contains_sesame`
- `contains_sulfite`
- `contains_other`
- `contains_unknown`

Konteks makanan:

- `food_category`
- `base_ingredient`
- `base_ingredient_tags`
- `suitable_breakfast`
- `suitable_lunch`
- `suitable_dinner`
- `meal_time_tags`
- `primary_meal_time`

Menu-ready dan rekomendasi:

- `is_recommendable_food`
- `recommendation_item_type`
- `recommendation_confidence`
- `ingredient_only_flag`
- `raw_ingredient_flag`
- `recommendation_exclusion_reason`

Halal guardrail:

- `halal_status`
- `is_halal_candidate`
- `contains_non_halal_ingredient`
- `non_halal_ingredient_tags`
- `halal_review_reason`
- `halal_confidence`

Pairing dan meal template:

- `pairing_group`
- `pairing_role`
- `pairing_notes`
- `pairing_suitability_notes`
- `meal_template_role`
- `meal_combo_valid`

Media:

- `image_url`
- `image_url_status`
- `image_url_source`
- `image_url_rule_version`

## 11. Feature Engineering

Fitur nutrisi dipakai sebagai basis scoring kalori dan makro. Fitur profil user mendukung perhitungan BMR, TDEE, target kalori, target protein, target lemak, dan target karbohidrat. Fitur konteks makanan dipakai agar rekomendasi tidak monoton dan tetap sesuai waktu makan.

Fitur meal time dapat digunakan dengan dua cara:

- `suitable_breakfast`, `suitable_lunch`, dan `suitable_dinner` untuk filter multi-label.
- `primary_meal_time` untuk kebutuhan model atau API yang hanya menerima satu kelas waktu makan.

Fitur pairing seperti `pairing_group`, `pairing_role`, `meal_template_role`, dan `meal_combo_valid` membantu sistem menyusun kombinasi makanan yang lebih natural, misalnya karbohidrat pokok, lauk protein, sayur, buah, minuman, atau snack.

## 12. Guardrail Alergen

Alergen harus diperlakukan sebagai hard filter sebelum model ranking. Jika pengguna memiliki alergi tertentu dan kolom `contains_X` bernilai true, makanan tersebut harus dibuang sebelum rekomendasi dihitung oleh AI.

Aturan backend yang disarankan:

- Jika user alergi gluten dan `contains_gluten == true`, buang item.
- Jika user alergi dairy dan `contains_dairy == true`, buang item.
- Jika `conservative_mode == true` dan `contains_unknown == true`, buang item atau kirim ke review manual.

Prinsip utama: dalam konteks alergi, false negative lebih berbahaya daripada false positive. Model AI tidak boleh menimpa hard filter alergen.

## 13. Guardrail Halal

Status halal bersifat rule-based dan bukan sertifikasi halal resmi. Untuk mode halal-only, backend sebaiknya hanya mengizinkan item dengan `is_halal_candidate == true`.

Aturan backend yang disarankan:

- Jika user memilih halal-only, gunakan hanya item dengan `is_halal_candidate == true`.
- Item `non_halal`, `needs_review`, atau `non_halal_or_review` harus dibuang dari rekomendasi halal-only.
- `halal_review_reason` tetap perlu ditampilkan di dashboard audit untuk evaluasi manual.

Pada dataset aktif, 483 dari 484 item berstatus `halal_candidate` dan 1 item masuk `non_halal_or_review`.

## 14. Menu-ready Filter

`train_ready_dataset.csv` hanya berisi item yang wajar ditampilkan sebagai rekomendasi makanan. Bahan mentah, bumbu, kondimen, tepung mentah, beras mentah, atau protein hewani mentah tidak dimasukkan ke dataset rekomendasi utama.

Item yang dikeluarkan tetap dapat ditelusuri melalui:

```text
03_final_datasets/audit/train_ready_dataset_full_audit.csv
```

Kolom yang membantu audit filter:

- `is_recommendable_food`
- `recommendation_item_type`
- `recommendation_confidence`
- `ingredient_only_flag`
- `raw_ingredient_flag`
- `cleaning_action`
- `cleaning_reason`
- `recommendation_exclusion_reason`

## 15. Image URL Validation

Dataset aktif sudah memiliki status `image_url_status` yang hanya berisi `ok` atau `refreshed`. Artinya gambar yang rusak atau kosong sudah diganti dengan fallback yang lebih stabil.

Distribusi aktif:

- `ok`: 411
- `refreshed`: 73

Frontend dapat memakai `image_url_status` untuk menampilkan gambar, melakukan fallback tambahan, atau menandai item yang perlu dicek ulang di masa depan.

## 16. Dashboard Audit

Dashboard Streamlit berada di:

```text
06_dashboard/streamlit_dashboard/app.py
```

Dataset dashboard berada di:

```text
06_dashboard/streamlit_dashboard/data/train_ready_dataset.csv
```

Versi publish-ready berada di:

```text
06_dashboard/publish_ready/
```

Dashboard HTML statis berada di:

```text
06_dashboard/static_html/nutrimatch_data_science_dashboard.html
```

Dashboard digunakan untuk memeriksa KPI dataset, distribusi halal, distribusi meal time, pairing, food explorer, dan status image URL. Dashboard adalah alat audit, bukan sumber data utama. Sumber data utama tetap `03_final_datasets/main/train_ready_dataset.csv` dan salinan integration-ready.

## 17. Kontrak Integrasi dengan Aplikasi NutriMatch

### 17.1 Sumber Dataset untuk Aplikasi

Repo aplikasi membaca artefak Data Science dari:

```text
../NutriMatch/data/ready/
```

Folder ini sebaiknya diperlakukan sebagai salinan dari:

```text
08_integration_ready/web_app_ready_dataset/
```

Kontrak minimum untuk integrasi:

- `train_ready_dataset.csv` harus sinkron antara workspace DS dan repo aplikasi.
- Kolom nutrisi, alergen, halal, meal time, pairing, dan image URL harus tetap ada.
- Jika CSV final berubah, salin ulang file dan metadata ke `../NutriMatch/data/ready/`.
- Setelah salin ulang, validasi row count, column count, `image_url_status`, dan `halal_status`.

### 17.2 Database dan Prisma

Schema Prisma aplikasi menyimpan entity utama:

- `User`
- `UserProfile`
- `Allergen`
- `UserAllergy`
- `Food`
- `FoodAllergen`
- `MealPlan`
- `MealPlanItem`

Mapping utama dari dataset DS ke model `Food`:

| Dataset DS | Prisma `Food` |
|---|---|
| `food_name` | `name` |
| `food_category` atau mapping kategori aplikasi | `category` |
| `image_url` | `imageUrl` |
| `calories_100g` | `caloriesPer100g` |
| `protein_100g` | `proteinPer100g` |
| `carbohydrate_100g` | `carbsPer100g` |
| `fat_100g` | `fatPer100g` |

Mapping alergen:

| Dataset DS | Prisma `Allergen.slug` |
|---|---|
| `contains_gluten` | `gluten` |
| `contains_dairy` | `dairy` |
| `contains_nuts` | `nuts` |
| `contains_peanut` | `peanut` |
| `contains_seafood` | `seafood` |
| `contains_egg` | `telur` atau `egg`, perlu konsistensi mapping |
| `contains_soy` | `kedelai` atau `soy`, perlu konsistensi mapping |
| `contains_celery` | `celery` |

Catatan penting: `prisma/seed.ts` saat ini berisi sample manual makanan dan alergen, bukan importer penuh dari `data/ready/train_ready_dataset.csv`. Jika aplikasi ingin memakai seluruh 484 item final, perlu dibuat script seed/import khusus dari CSV Data Science ke tabel `foods`, `allergens`, dan `food_allergens`.

### 17.3 API Profile dan Perhitungan Nutrisi

`src/app/api/profile/route.ts` menyimpan profil user dan menghitung nutrisi memakai `src/lib/nutrition.ts`.

Rumus yang dipakai aplikasi:

- BMR memakai Mifflin-St Jeor.
- TDEE = BMR x activity multiplier.
- Target kalori = TDEE + goal adjustment.

Enum aplikasi:

- `Gender`: `MALE`, `FEMALE`
- `ActivityLevel`: `SEDENTARY`, `LIGHTLY_ACTIVE`, `MODERATELY_ACTIVE`, `VERY_ACTIVE`
- `HealthGoal`: `LOSE_WEIGHT`, `MAINTAIN_WEIGHT`, `GAIN_WEIGHT`

Adjustment target kalori:

- `LOSE_WEIGHT`: -500 kcal/hari
- `MAINTAIN_WEIGHT`: 0
- `GAIN_WEIGHT`: +300 kcal/hari

### 17.4 API Rekomendasi AI

Kontrak request ke AI recommendation service berada di `src/lib/ai/recommendationClient.ts`.

Payload utama:

```json
{
  "target_macros": {
    "calories": 1800,
    "protein_g": 113,
    "fat_g": 60,
    "carb_g": 203
  },
  "allergies": {
    "gluten": 0,
    "dairy": 0,
    "nuts": 0,
    "peanut": 0,
    "seafood": 0,
    "egg": 0,
    "soy": 0,
    "celery": 0
  },
  "breakfast_prefs": {
    "food_category": [],
    "main_ingredients": []
  },
  "lunch_prefs": {
    "food_category": [],
    "main_ingredients": []
  },
  "dinner_prefs": {
    "food_category": [],
    "main_ingredients": []
  },
  "user_text": "Generate balanced daily meal recommendations.",
  "start_date": "2026-06-05",
  "days": 7,
  "variety_penalty": 0.15,
  "halal_only": false
}
```

Response AI yang diharapkan:

```json
{
  "daily_plan": [
    {
      "meal_name": "LUNCH",
      "target_calories": 630,
      "recommendations": [
        {
          "food_name": "Nasi Ayam Panggang",
          "food_id": "F001",
          "image_url": "https://example.com/image.jpg",
          "calories_100g": 180,
          "ideal_grams": 150,
          "ideal_calories": 270,
          "ideal_protein": 18,
          "ideal_fat": 7.5,
          "ideal_carb": 33,
          "match_score": 0.92,
          "pairing_group": "main_meal",
          "pairing_role": "protein"
        }
      ]
    }
  ],
  "narrative_summary": "Ringkasan rekomendasi."
}
```

Field `match_score`, `pairing_group`, dan `pairing_role` bersifat opsional di client saat ini, tetapi tetap sebaiknya dikirim oleh AI service jika tersedia karena membantu explainability dan meal composition.

### 17.5 Endpoint yang Relevan

| Endpoint | Fungsi |
|---|---|
| `GET /api/allergens` | Mengambil daftar alergen dari database. |
| `GET /api/profile` | Mengambil profil user login. |
| `POST /api/profile` | Membuat/update profil, menghitung BMR/TDEE/target kalori, dan menyimpan alergi user. |
| `POST /api/meal-recommendation` | Meminta rekomendasi AI dan mengembalikan hasil normalized tanpa membuat record meal plan penuh. |
| `GET /api/meal-plan` | Mengambil meal plan terbaru user dari database. |
| `POST /api/meal-plan` | Meminta rekomendasi AI, menyimpan food/meal plan/meal item ke database, lalu mengembalikan ringkasan. |

### 17.6 Local Fallback

`src/lib/mealPlanGenerator.ts` menyediakan fallback meal planner berbasis tabel `foods` dan `food_allergens`. Fallback ini:

- Mengambil food yang tidak punya alergen yang dipilih user.
- Membagi target kalori harian menjadi breakfast 25%, lunch 35%, dinner 30%, snack 10%.
- Menghitung porsi dengan rumus `(targetCalories / caloriesPer100g) * 100`.
- Membatasi porsi antara 80 g sampai 400 g.

Karena fallback memakai data dari database, kualitas fallback bergantung pada proses seed/import database. Jika database hanya berisi sample dari `prisma/seed.ts`, fallback tidak merepresentasikan seluruh dataset final 484 item.

## 18. Handover untuk AI Engineer dan Backend

Urutan pemakaian dataset yang disarankan:

1. Terima profil pengguna: umur, gender, tinggi, berat, aktivitas, goal, alergi, preferensi halal, dan waktu makan.
2. Hitung BMR, TDEE, target kalori, target protein, target lemak, dan target karbohidrat.
3. Terapkan hard filter alergen.
4. Terapkan hard filter halal jika halal-only aktif.
5. Terapkan filter waktu makan memakai `suitable_*` atau `primary_meal_time`.
6. Lakukan ranking makanan berdasarkan target nutrisi dan preferensi pengguna.
7. Gunakan `pairing_group`, `pairing_role`, dan `meal_template_role` untuk diversifikasi hasil.
8. Kirim rekomendasi final beserta nutrisi, label alergen, status halal, dan `image_url`.

## 19. Contoh Output API Rekomendasi

Contoh struktur response yang dapat disesuaikan Backend Engineer:

```json
{
  "user_id": "U001",
  "meal_time": "lunch",
  "recommendations": [
    {
      "food_id": "F001",
      "food_name": "Nasi Ayam Panggang",
      "calories_100g": 180,
      "protein_100g": 12,
      "fat_100g": 5,
      "carbohydrate_100g": 22,
      "allergen_flags": {
        "contains_gluten": false,
        "contains_dairy": false,
        "contains_unknown": false
      },
      "halal_status": "halal_candidate",
      "food_category": "lauk_hewani",
      "primary_meal_time": "lunch",
      "pairing_role": "protein",
      "image_url": "https://example.com/image.jpg"
    }
  ]
}
```

## 20. QA Checklist

Sebelum dataset diberikan ke AI Engineer, pastikan:

- `train_ready_dataset.csv` memakai versi aktif dari `03_final_datasets/main/`.
- Jumlah baris dan kolom sesuai CSV aktif.
- `food_id` tidak duplikat.
- `food_name` dan `food_name_clean` tidak kosong.
- Kolom nutrisi utama numerik dan tidak null.
- Kolom alergen konsisten dan dipakai sebagai hard filter.
- `contains_unknown` diperlakukan konservatif untuk alergi kritis.
- `is_halal_candidate` dipakai untuk mode halal-only.
- `image_url_status` tidak menyisakan broken atau invalid tanpa catatan.
- Dataset dashboard dan integration-ready sudah sinkron dengan dataset final jika akan dipakai aplikasi.
- `../NutriMatch/data/ready/train_ready_dataset.csv` sudah sama dengan `08_integration_ready/web_app_ready_dataset/train_ready_dataset.csv`.
- Jika aplikasi memakai database Prisma untuk fallback, pastikan ada importer CSV final ke tabel `foods` dan `food_allergens`.
- Mapping `contains_egg` ke slug `telur/egg` dan `contains_soy` ke slug `kedelai/soy` harus konsisten antara Data Science, seed, UI, dan API.
- `NUTRIMATCH_AI_API_URL` mengarah ke service rekomendasi yang memahami payload Data Science.

## 21. Risiko dan Keterbatasan

- Status halal masih rule-based dan bukan sertifikasi resmi.
- Banyak makanan lokal tidak memiliki ingredient list eksplisit.
- Label alergen dari dataset publik perlu validasi manual untuk kasus kritis.
- `contains_unknown` dapat mengurangi jumlah rekomendasi jika conservative mode aktif.
- URL gambar bergantung pada sumber eksternal dan perlu pengecekan berkala.
- Metadata historis dapat berbeda dari CSV aktif karena ada beberapa tahap sync dan kurasi.
- Script pipeline masih perlu audit path jika dijalankan penuh dari struktur konsolidasi baru.
- `../NutriMatch/data/ready/README.md` masih memuat beberapa angka historis sehingga perlu diperbarui agar tidak bertentangan dengan CSV aktif.
- `prisma/seed.ts` masih sample manual sehingga belum otomatis mengisi database dari 484 item final.
- Fallback lokal aplikasi belum memakai seluruh fitur Data Science seperti `halal_status`, `primary_meal_time`, `pairing_group`, dan `meal_template_role` kecuali mapping/import diperluas.

## 22. Rekomendasi Pengembangan Lanjutan

- Tambahkan data dictionary lengkap untuk 80 kolom aktif.
- Tambahkan unit test schema, null check, enum check, duplicate check, dan row count sanity check.
- Pisahkan metadata historis dan metadata current-state agar handover lebih mudah dibaca.
- Tambahkan human review untuk alergen unknown dan halal needs-review.
- Buat pipeline sync otomatis dari `03_final_datasets/main` ke `06_dashboard` dan `08_integration_ready`.
- Tambahkan versioning dataset dengan DVC atau cloud storage.
- Tambahkan feedback loop dari pengguna untuk memperbaiki ranking rekomendasi.
- Buat script importer `data/ready/train_ready_dataset.csv` ke Prisma agar tabel `foods` dan `food_allergens` memakai dataset final, bukan sample manual.
- Update README di `../NutriMatch/data/ready/README.md` agar row count dan column count mengikuti CSV aktif 484 x 80.
- Perluas fallback planner agar memakai `primary_meal_time`, `suitable_*`, `halal_status`, dan `pairing_role`.
- Tambahkan automated check di repo aplikasi untuk memastikan `data/ready/train_ready_dataset.csv` tidak stale terhadap export Data Science.

## 23. Kesimpulan

Folder `Final data scientist` sudah dapat dijadikan rujukan utama pekerjaan Data Science NutriMatch. Dataset utama `train_ready_dataset.csv` sudah memuat nutrisi, alergen, konteks makanan, halal guardrail, pairing, dan status gambar. Untuk integrasi aplikasi hasil pull GitHub, gunakan `../NutriMatch/data/ready/` sebagai lokasi konsumsi aplikasi, dengan `08_integration_ready/web_app_ready_dataset/` sebagai paket export dari sisi Data Science.

Prinsip terpenting untuk implementasi adalah sederhana: model AI boleh melakukan ranking, tetapi tidak boleh melewati guardrail alergi dan halal yang sudah disediakan oleh Data Science. Selain itu, repo aplikasi perlu menjaga sinkronisasi antara CSV final, seed/import database, payload AI, dan fallback meal planner supaya rekomendasi yang muncul di UI benar-benar memakai dataset Data Science terbaru.
