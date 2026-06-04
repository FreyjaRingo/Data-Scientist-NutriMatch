# Data Science Plan - NutriMatch

## Ringkasan konteks

Peran Data Scientist pada NutriMatch adalah menyiapkan data makanan, nutrisi, alergen, dan profil pengguna agar siap dipakai AI Engineer untuk training, evaluasi, dan integrasi sistem rekomendasi. Fokus utama bukan membangun model final, tetapi memastikan dataset bersih, terdokumentasi, konsisten, dan aman untuk kasus alergi.

## Inventaris dataset lokal

| Dataset | Lokasi | Ukuran | Fungsi utama | Catatan kualitas awal |
|---|---|---:|---|---|
| Indonesian Food Nutrition | `archive/nutrition.csv` | 1,346 baris, 7 kolom | Master makanan lokal Indonesia, kalori dan makro per 100g | Tidak ada missing value, tetapi perlu validasi outlier seperti carbohydrate sangat tinggi dan kalori 0 |
| Food Allergens and Allergies | `archive (2)/FoodData.csv` | 184 baris, 5 kolom | Taksonomi food item ke kategori alergi | Ada 22 missing pada kolom Allergy |
| Food Ingredients and Allergens | `archive (1)/food_ingredients_and_allergens.csv` | 399 baris, 7 kolom | Mapping produk/bahan ke alergen dan label Contains/Not Contains | Ada 90 duplikat, banyak missing pada Sweetener, Fat/Oil, Allergens |
| Weight Change Prediction | `archive (3)/weight_change_dataset.csv` | 100 baris, 13 kolom | Data simulasi profil fisik, kalori, aktivitas, perubahan berat | Kecil, cocok untuk validasi formula dan demo, bukan training utama |

## Target output untuk AI Engineer

1. `food_master_clean.csv`
   - Satu baris per makanan.
   - Kolom minimal: `food_id`, `food_name`, `calories_100g`, `protein_100g`, `fat_100g`, `carbohydrate_100g`, `source`, `image_url`.

2. `allergen_reference_clean.csv`
   - Kamus alergen standar.
   - Kolom minimal: `allergen_id`, `allergen_group`, `ingredient_keyword`, `canonical_name`, `risk_level`, `source`.

3. `food_allergen_labels.csv`
   - Label multi-label untuk training/filtering.
   - Kolom minimal: `food_id`, `contains_gluten`, `contains_dairy`, `contains_nuts`, `contains_peanut`, `contains_seafood`, `contains_egg`, `contains_soy`, `contains_other`, `label_source`, `confidence`.

4. `user_profile_features_schema.csv`
   - Skema fitur pengguna untuk model/recommender.
   - Kolom fitur: `age`, `gender`, `height_cm`, `weight_kg`, `activity_level`, `goal`, `bmr`, `tdee`, `target_calorie`, `protein_target_g`, `fat_target_g`, `carb_target_g`, `allergy_vector`.

5. `train_ready_dataset.csv`
   - Gabungan fitur makanan, label alergen, dan fitur nutrisi.
   - Dipakai AI Engineer untuk eksperimen model.

6. `data_dictionary.md`
   - Definisi kolom, tipe data, satuan, range valid, aturan missing value, dan sumber.

7. `handover_notes.md`
   - Ringkasan cleaning, asumsi, risiko, batasan dataset, dan rekomendasi penggunaan.

## Pembagian kerja dua Data Scientist

### Orang A - Nutrisi, profil pengguna, dan formula

Tanggung jawab:

- Audit dan bersihkan `nutrition.csv`.
- Standarisasi nama makanan: lowercase, trim spasi, hilangkan karakter aneh, buat `food_id` stabil.
- Validasi satuan nutrisi per 100g.
- Deteksi outlier nutrisi:
  - kalori 0 untuk makanan yang seharusnya mengandung energi,
  - makro tidak masuk akal,
  - karbohidrat, lemak, atau protein terlalu tinggi.
- Buat formula BMR dan TDEE:
  - BMR berbasis gender, umur, tinggi, berat.
  - TDEE berbasis activity multiplier.
  - Goal adjustment untuk turun, jaga, atau naik berat badan.
- Buat target makro harian:
  - protein, fat, carbohydrate dalam gram.
  - pastikan total makro mendekati target kalori.
- Siapkan `user_profile_features_schema.csv`.
- Buat EDA nutrisi:
  - distribusi kalori,
  - top makanan tinggi protein,
  - top makanan tinggi lemak,
  - kelompok makanan dengan risiko kalori tinggi,
  - coverage image URL.

Deliverable Orang A:

- `food_master_clean.csv`
- `user_profile_features_schema.csv`
- notebook/script EDA nutrisi
- bagian data dictionary untuk nutrisi dan profil pengguna

### Orang B - Alergen, ingredient mapping, dan label training

Tanggung jawab:

- Audit dan bersihkan `FoodData.csv` serta `food_ingredients_and_allergens.csv`.
- Hapus duplikat pada dataset ingredients/allergens.
- Standarisasi label alergen ke kategori yang konsisten:
  - gluten/wheat,
  - dairy/milk,
  - nuts/tree nuts,
  - peanut,
  - seafood/fish/shellfish,
  - egg,
  - soy,
  - celery,
  - mustard,
  - sesame,
  - other.
- Tangani missing `Allergy` dan `Allergens`:
  - isi dengan `unknown` jika tidak dapat disimpulkan,
  - jangan asumsikan aman jika data kosong.
- Buat kamus keyword bahan:
  - contoh dairy: milk, cheese, butter, cream, yogurt.
  - contoh gluten: wheat, flour, bread, noodle.
  - contoh seafood: fish, shrimp, shellfish, anchovy.
- Mapping makanan Indonesia ke potensi alergen dengan pendekatan:
  - exact match nama,
  - keyword match bahan,
  - manual review untuk makanan berisiko.
- Buat label multi-label alergen.
- Tentukan `confidence`:
  - `high` untuk label eksplisit dari dataset alergen,
  - `medium` untuk keyword match,
  - `low` untuk dugaan/manual yang belum tervalidasi.
- Buat EDA alergen:
  - jumlah makanan per kategori alergen,
  - distribusi label Contains/Not Contains,
  - makanan dengan label unknown,
  - potensi class imbalance.

Deliverable Orang B:

- `allergen_reference_clean.csv`
- `food_allergen_labels.csv`
- notebook/script EDA alergen
- bagian data dictionary untuk alergen dan label

## Tugas bersama

1. Gabungkan output Orang A dan Orang B menjadi `train_ready_dataset.csv`.
2. Buat aturan guardrail:
   - jika pengguna alergi X, semua makanan dengan label X harus dikeluarkan sebelum rekomendasi.
   - makanan berlabel `unknown` untuk alergi terkait harus diperlakukan sebagai tidak aman pada mode conservative.
3. Buat split data:
   - train 70 persen,
   - validation 15 persen,
   - test 15 persen.
   - gunakan stratifikasi berdasarkan label alergen utama jika memungkinkan.
4. Buat negative sampling untuk makanan aman:
   - jangan biarkan dataset hanya berisi contoh `Contains`.
   - pastikan label `Not Contains` punya bukti atau minimal lolos dari kamus alergen.
5. Buat laporan risiko:
   - data alergen tidak lengkap,
   - makanan Indonesia sering tidak punya daftar ingredient,
   - false negative alergi lebih berbahaya daripada false positive.
6. Handover ke AI Engineer:
   - jelaskan schema,
   - contoh input dan output,
   - rekomendasi metrik utama: recall per allergen class, false negative rate, macro F1.

## Timeline kerja 5 minggu

### Minggu 1 - Audit, cleaning awal, dan schema

- Orang A:
  - audit `nutrition.csv`,
  - buat schema `food_master_clean.csv`,
  - cek outlier nutrisi dan satuan.
- Orang B:
  - audit dua dataset alergen,
  - hapus duplikat,
  - buat daftar kategori alergen standar.
- Bersama:
  - sepakati schema final dengan AI Engineer.
  - buat data dictionary versi 0.1.

Output minggu 1:

- dataset bersih versi awal,
- schema final,
- daftar isu kualitas data.

### Minggu 2 - Feature engineering dan label alergen

- Orang A:
  - implementasi BMR/TDEE,
  - activity multiplier,
  - target kalori berdasarkan goal,
  - target makro.
- Orang B:
  - buat allergen keyword dictionary,
  - mapping bahan ke label multi-label,
  - tandai confidence label.
- Bersama:
  - integrasi `food_master_clean.csv` dan `food_allergen_labels.csv`.

Output minggu 2:

- `food_allergen_labels.csv`,
- `user_profile_features_schema.csv`,
- dataset gabungan versi 0.1.

### Minggu 3 - EDA, validasi, dan train-ready dataset

- Orang A:
  - EDA nutrisi dan profil target kalori.
  - validasi formula memakai `weight_change_dataset.csv` sebagai sanity check.
- Orang B:
  - EDA alergen,
  - cek class imbalance,
  - manual review makanan berisiko tinggi.
- Bersama:
  - buat `train_ready_dataset.csv`,
  - train/validation/test split,
  - dokumentasikan asumsi label.

Output minggu 3:

- train-ready dataset,
- notebook EDA,
- rekomendasi metrik untuk AI Engineer.

### Minggu 4 - Handover dan support integrasi

- Orang A:
  - siapkan contoh payload profil pengguna dan hasil fitur.
  - bantu backend/AI memahami perhitungan kalori.
- Orang B:
  - siapkan contoh kasus alergi dan guardrail.
  - bantu AI Engineer menguji false negative.
- Bersama:
  - buat `handover_notes.md`,
  - validasi sample inference bersama AI Engineer.

Output minggu 4:

- paket data handover lengkap,
- contoh input-output,
- daftar edge case.

### Minggu 5 - Finalisasi laporan dan demo data

- Orang A:
  - finalisasi visualisasi nutrisi dan formula.
- Orang B:
  - finalisasi visualisasi alergen dan confusion/error analysis bila model sudah ada.
- Bersama:
  - finalisasi laporan teknis PDF bagian data,
  - cek reproducibility notebook/script,
  - pastikan dataset final tidak berubah tanpa versioning.

Output minggu 5:

- data final,
- data dictionary final,
- laporan bagian Data Science,
- dashboard/visualisasi bila tetap dibutuhkan.

## Checklist prioritas

### Must have

- Dataset makanan bersih dan konsisten.
- Label alergen multi-label.
- Data dictionary.
- Train-ready dataset.
- Guardrail rule untuk alergi.
- Handover notes untuk AI Engineer.

### Should have

- EDA lengkap nutrisi dan alergen.
- Script reproducible untuk cleaning.
- Split train/validation/test.
- Confidence label.

### Could have

- Dashboard Streamlit untuk EDA.
- A/B testing sederhana untuk membandingkan dua strategi rekomendasi.
- Enrichment dari dataset tambahan.

### Won't have untuk scope DS data-prep

- Training model final production.
- Deployment dashboard sebagai prioritas utama.
- Diagnosis medis atau klaim kesehatan klinis.

## Dataset tambahan yang disarankan

1. Open Food Facts
   - Link: https://world.openfoodfacts.org/data
   - Fungsi: memperkaya ingredient text, allergens, traces, nutrition per 100g, brand product.
   - Cocok untuk: melatih deteksi alergen berbasis ingredient text dan validasi label produk nyata.
   - Catatan: crowdsourced, jadi perlu filtering kualitas dan jangan otomatis dianggap benar.

2. USDA FoodData Central
   - Link: https://fdc.nal.usda.gov/download-datasets/
   - Fungsi: referensi nutrisi sangat lengkap, tersedia CSV/JSON dan API.
   - Cocok untuk: melengkapi micronutrient, fiber, sugar, sodium, dan validasi nilai nutrisi global.
   - Catatan: tidak spesifik makanan Indonesia, jadi pakai sebagai enrichment atau fallback.

3. Ingredients with 16 Allergen Tags
   - Link: https://www.kaggle.com/datasets/khochawongwat/ingredients-with-17-allergen-tags
   - Fungsi: 10.000 ingredient dengan tag 16 alergen umum.
   - Cocok untuk: memperkuat keyword dictionary dan model ingredient-to-allergen.
   - Catatan: cek lisensi dan konsistensi label sebelum digabung.

4. Global Food & Nutrition Database 2026
   - Link: https://www.kaggle.com/datasets/ahsanneural/global-food-and-nutrition-database-2026
   - Fungsi: gabungan nutrisi, allergen flags, Nutri-Score, NOVA, dan health score.
   - Cocok untuk: baseline cepat jika butuh fitur allergen boolean dan nutrisi lengkap.
   - Catatan: tetap perlu verifikasi karena ini dataset turunan, bukan sumber primer.

## Rekomendasi urutan download tambahan

1. Download Open Food Facts terlebih dahulu, lalu filter kolom:
   - `product_name`
   - `ingredients_text`
   - `allergens`
   - `traces`
   - `countries_tags`
   - `energy-kcal_100g`
   - `proteins_100g`
   - `fat_100g`
   - `carbohydrates_100g`
   - `fiber_100g`
   - `sugars_100g`
   - `salt_100g`

2. Download USDA FoodData Central Foundation Foods atau Branded Foods jika butuh nutrisi lebih lengkap.

3. Download Ingredients with 16 Allergen Tags jika label alergen lokal masih terlalu sedikit.

## Catatan penting untuk keselamatan alergi

Untuk proyek ini, data kosong tidak boleh otomatis dianggap aman. Dalam konteks alergi, false negative lebih berbahaya daripada false positive. Maka, rekomendasi default yang aman adalah:

- `contains_allergen = true` berarti wajib difilter.
- `contains_allergen = unknown` berarti difilter pada mode conservative.
- AI model tidak boleh menjadi satu-satunya lapisan filter.
- Rule-based guardrail tetap wajib sebelum output dikirim ke pengguna.
