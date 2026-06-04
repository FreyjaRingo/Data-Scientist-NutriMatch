# Cara Menyatukan Dataset Orang A dan Orang B

## Output final

File final hasil gabungan akan dibuat di:

```text
outputs/merged/train_ready_dataset.csv
```

File ini berisi:

- fitur makanan/nutrisi dari Orang A,
- label alergen dari Orang B,
- status kualitas merge,
- confidence label,
- fitur konteks makanan untuk membantu variasi rekomendasi.

Schema fitur pengguna dari Orang A juga disalin ke:

```text
outputs/merged/user_profile_features_schema.csv
```

## Cara 1 - Jika file Orang A sudah ada lokal

Buka notebook:

```text
notebooks/merge_orang_a_b_train_ready.ipynb
```

Lalu isi:

```python
FOOD_MASTER_PATH = PROJECT_ROOT / "path" / "ke" / "food_master_clean.csv"
SEARCH_ROOT = PROJECT_ROOT
```

Jalankan semua cell.

## Cara 2 - Jika repo Orang A sudah diclone

Misalnya repo Orang A diclone ke:

```text
external/nutrimatch-capstone-cc26-psu084
```

Isi notebook seperti ini:

```python
FOOD_MASTER_PATH = None
SEARCH_ROOT = PROJECT_ROOT / "external" / "nutrimatch-capstone-cc26-psu084"
```

Script akan mencari otomatis CSV yang paling mirip `food_master_clean.csv`.

## Kolom kunci

Kolom penggabungan utama:

```text
food_name_clean
```

Orang A perlu punya nama makanan yang sudah dinormalisasi. Jika belum ada, script akan membuat otomatis dari kolom nama makanan.

## Status merge

Kolom `merge_status` punya tiga kemungkinan:

- `exact_name`: nama makanan cocok langsung dengan label Orang B.
- `keyword_fallback`: tidak cocok langsung, tapi terdeteksi dari keyword alergen pada nama makanan.
- `not_matched`: tidak ditemukan label alergen yang cukup.

Untuk keamanan alergi, jika `not_matched`, maka `contains_unknown=True` saat `CONSERVATIVE_UNKNOWN=True`.

## File pendukung

Selain `train_ready_dataset.csv`, folder ini juga berisi:

- `merge_summary.csv`: ringkasan jumlah match/unmatched.
- `food_master_standardized.csv`: versi standar dari output Orang A.
- `user_profile_features_schema.csv`: schema fitur profil user/BMR/TDEE dari Orang A.
- `feature_enrichment_summary.csv`: ringkasan fitur kategori makanan, bahan dasar, dan waktu makan.
- `feature_enrichment_metadata.json`: metadata rule enrichment.
- `allergen_labels_aggregated.csv`: label Orang B yang sudah diagregasi per nama makanan.
- `merge_metadata.json`: metadata file input dan output.

## Fitur konteks tambahan

Untuk mengurangi rekomendasi yang monoton, `train_ready_dataset.csv` ditambah fitur:

- `food_category`: kategori makanan, misalnya `berkuah`, `gorengan`, `sayuran`, `buah`, `lauk_hewani`, `lauk_nabati`, `karbohidrat_pokok`, `minuman`, `snack_dessert`, `bumbu_sambal`, atau `lainnya`.
- `base_ingredient`: bahan dasar utama, misalnya `ayam`, `sapi`, `ikan`, `seafood`, `telur`, `kedelai`, `kacang`, `beras`, `gandum`, `umbi`, `sayuran`, atau `buah`.
- `suitable_breakfast`, `suitable_lunch`, `suitable_dinner`: multilabel boolean untuk waktu makan yang cocok.
- `meal_time_tags`: gabungan label waktu makan, misalnya `breakfast|lunch`.
- `primary_meal_time`: kelas utama waktu makan, yaitu `breakfast`, `lunch`, atau `dinner`.

Fitur ini dibuat secara rule-based dengan versi `food_context_rules_v1`. AI Engineer bisa memakai `food_category`, `base_ingredient`, dan `primary_meal_time` untuk diversifikasi ranking, sementara kolom `suitable_*` bisa dipakai sebagai filter meal plan.
