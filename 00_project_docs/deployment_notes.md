# Deployment Notes - Data Science Dataset

## Deployment Target

Dataset Data Science dideploy sebagai artefak CSV siap pakai untuk AI Engineer dan Fullstack melalui repository:

- Data Science repository: `Data-Scientist-Capstone-Project-CC26-PSU084`
- Combined NutriMatch repository: `NutriMatch`, folder `data/ready/`

## File yang Dideploy

| File | Tujuan |
|---|---|
| `train_ready_dataset.csv` | Dataset utama untuk training/rekomendasi. |
| `menu_ready_filter_summary.csv` | Ringkasan filter menu-ready. |
| `menu_ready_filter_metadata.json` | Metadata rule menu-ready dan halal guardrail. |
| `train_ready_v6_sync_summary.csv` | Ringkasan sinkronisasi dataset v6. |
| `image_url_refresh_report.csv` | Audit gambar yang diganti karena URL lama rusak. |
| `user_profile_features_schema.csv` | Schema user profile untuk AI Engineer. |

## Deployment Flow

1. Sinkronkan update teammate v6 ke `orang_b/final_datasets/train_ready_dataset.csv`.
2. Refresh image URL yang kosong/rusak.
3. Generate dashboard dan laporan teknis.
4. Commit dan push ke repository Data Science.
5. Copy file siap pakai ke `D:\PPL 1\NutriMatch_combined_repo\data\ready`.
6. Commit dan push ke branch `dev` repository gabungan.

## Validation Checklist

- Row dataset final: 591.
- Kolom dataset final: 78.
- Image URL kosong/invalid: 0.
- Status gambar: `ok` atau `refreshed`.
- Pairing columns tersedia.
- Halal guardrail tersedia.
- Dataset siap dikonsumsi API/model recommendation.
