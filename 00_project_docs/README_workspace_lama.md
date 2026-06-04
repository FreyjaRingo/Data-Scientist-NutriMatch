# DBD - NutriMatch Data Science Workspace

Workspace lokal ini dirapikan berdasarkan pembagian kerja Data Science:

```text
DBD/
  orang_a/
  orang_b/
```

## Orang A

Folder `orang_a/` berisi pekerjaan nutrisi, food master, profil pengguna, BMR/TDEE, target makro, dan EDA dari anggota Data Science pertama.

Isi utama:

```text
orang_a/
  nutrimatch-capstone-dsA/
    data/raw/
    data/processed/
    notebooks/
    output/
  notebooks/
```

Output penting dari Orang A:

- `orang_a/nutrimatch-capstone-dsA/data/processed/food_master_clean.csv`
- `orang_a/nutrimatch-capstone-dsA/data/processed/user_profile_features_schema.csv`

## Orang B

Folder `orang_b/` berisi pekerjaan preprocessing alergen, ingredient mapping, merge dataset, enrichment fitur konteks makanan, serta dataset final siap pakai.

Isi utama:

```text
orang_b/
  raw_datasets/Dataset/
  dataset_sources/
  docs/
  notebooks/
  scripts_python/
  final_datasets/
  outputs/
```

Output penting dari Orang B:

- `orang_b/final_datasets/train_ready_dataset.csv`
- `orang_b/final_datasets/user_profile_features_schema.csv`
- `orang_b/final_datasets/feature_enrichment_summary.csv`
- `orang_b/final_datasets/feature_enrichment_metadata.json`

## Dataset Baru

Dataset tambahan yang baru dimasukkan berada di:

```text
orang_b/raw_datasets/Dataset/archive/
orang_b/raw_datasets/Dataset/archive (1)/
orang_b/raw_datasets/Dataset/archive (2)/
orang_b/raw_datasets/Dataset/archive (3)/
```

Dataset tersebut sudah dipakai untuk memperkuat fitur:

- `food_category`
- `base_ingredient`
- `suitable_breakfast`
- `suitable_lunch`
- `suitable_dinner`
- `primary_meal_time`
- `recipe_reference_match`

## Catatan GitHub

Folder raw dataset berukuran sangat besar dan tidak disarankan untuk dipush ke GitHub biasa. Dataset final yang aman untuk dipakai tim AI/Fullstack ada di `orang_b/final_datasets/`.
