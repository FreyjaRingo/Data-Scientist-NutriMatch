# Contribution Matrix - NutriMatch Data Science

## Ringkasan Peran

| Anggota | Fokus | Output utama |
|---|---|---|
| Orang A | Nutrisi, food master, profil pengguna, BMR/TDEE, target makro, EDA nutrisi | `food_master_clean.csv`, `user_profile_features_schema.csv`, notebook food master, notebook user profile, notebook EDA |
| Orang B | Alergen, ingredient mapping, label multi-label, confidence label, merge final | `food_allergen_labels.csv`, `allergen_reference_clean.csv`, `ingredient_allergen_training.csv`, `train_ready_dataset.csv`, notebook alergen, notebook merge |

## Detail Pekerjaan Orang A

| Area | Pekerjaan | Artefak |
|---|---|---|
| Cleaning nutrisi | Membersihkan dataset makanan Indonesia, menstandarkan kolom nutrisi per 100g, membuat `food_id`, dan mengecek anomali kalori/makro. | `final/final_datasets/food_master_standardized.csv`, `final/notebooks/orang_a/01_foodmaster_clean.ipynb` |
| Feature profil pengguna | Menerjemahkan data usia, gender, tinggi, berat, aktivitas, dan goal menjadi fitur BMR/TDEE, target kalori, dan target makro. | `final/final_datasets/user_profile_features_schema.csv`, `final/notebooks/orang_a/02_userprofile_clean.ipynb` |
| EDA nutrisi | Membuat visualisasi distribusi kalori, top foods, audit kualitas data, profil pengguna, dan korelasi. | `final/notebooks/orang_a/03_EDA_nutrimatch.ipynb` |

## Detail Pekerjaan Orang B

| Area | Pekerjaan | Artefak |
|---|---|---|
| Cleaning alergen | Membersihkan dataset alergen, menghapus duplikat, menangani missing value, dan menstandarkan label alergen. | `final/notebooks/orang_b_and_merge/orang_b_allergen_preprocessing.ipynb` |
| Allergen dictionary | Membuat kamus keyword alergen untuk gluten, dairy, nuts, peanut, seafood, egg, soy, celery, mustard, sesame, sulfite, dan other. | `final/scripts_python/orang_b_allergen_pipeline.py` |
| Multi-label dataset | Membuat label `contains_*` dan `confidence` untuk setiap makanan/produk. | Output intermediate di pipeline Orang B; dataset final ada pada `final/final_datasets/train_ready_dataset.csv` |
| Merge final | Menggabungkan food master Orang A dengan label alergen Orang B memakai `food_name_clean`, exact match, dan keyword fallback. | `final/notebooks/orang_b_and_merge/merge_orang_a_b_train_ready.ipynb`, `final/scripts_python/merge_orang_a_b.py` |

## Output Final Bersama

| File | Keterangan |
|---|---|
| `final/final_datasets/train_ready_dataset.csv` | Dataset final untuk AI Engineer, berisi nutrisi, label alergen, confidence, dan status merge. |
| `final/final_datasets/user_profile_features_schema.csv` | Schema fitur profil user untuk BMR/TDEE dan target makro. |
| `final/final_datasets/merge_summary.csv` | Ringkasan jumlah exact match, keyword fallback, dan not matched. |
| `final/dataset_sources/raw_dataset_links.md` | Daftar sumber dataset mentah tanpa menyimpan file besar di repo. |

## Catatan Kolaborasi

- Orang A menyediakan data makanan bersih dan fitur pengguna.
- Orang B menyediakan label alergen dan guardrail `contains_unknown`.
- Dataset final adalah hasil penggabungan dua jalur tersebut.
- Baris yang tidak punya bukti alergen cukup diberi `contains_unknown=True` untuk menjaga keamanan rekomendasi.
