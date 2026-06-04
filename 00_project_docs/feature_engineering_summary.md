# Feature Engineering Summary - NutriMatch Data Science

## Objective

Menyiapkan dataset makanan yang siap dipakai AI Engineer untuk rekomendasi makanan personal, dengan guardrail nutrisi, alergi, meal timing, status halal, dan pairing makanan.

## Fitur Utama yang Dibentuk

| Kelompok fitur | Kolom | Fungsi |
|---|---|---|
| Nutrisi | `calories_100g`, `protein_100g`, `fat_100g`, `carbohydrate_100g` | Basis scoring dan filtering kebutuhan kalori/makro. |
| Alergen | `contains_gluten`, `contains_dairy`, `contains_nuts`, `contains_peanut`, `contains_seafood`, `contains_egg`, `contains_soy`, `contains_unknown` | Guardrail untuk menghindari rekomendasi yang berisiko bagi user alergi. |
| Kategori makanan | `food_category`, `recommendation_item_type`, `meal_template_role` | Membantu model/API membedakan menu, protein, sayur, buah, snack, staple, dan dairy. |
| Bahan dasar | `base_ingredient`, `base_ingredient_tags`, `main_ingredient` | Diversifikasi rekomendasi agar tidak makanan itu-itu saja. |
| Waktu makan | `suitable_breakfast`, `suitable_lunch`, `suitable_dinner`, `primary_meal_time`, `meal_time_tags` | Filter breakfast/lunch/dinner. |
| Halal guardrail | `halal_status`, `is_halal_candidate`, `contains_non_halal_ingredient`, `halal_review_reason` | Filter halal-only dan review item sensitif. |
| Pairing | `pairing_group`, `pairing_role`, `pairing_notes`, `pairing_suitability_notes`, `meal_combo_valid` | Membantu AI Engineer membuat kombinasi makanan yang seimbang. |
| Kualitas gambar | `image_url_status`, `image_url_source`, `image_url_rule_version` | Menandai apakah image URL asli valid atau diganti fallback. |

## Output

- `orang_b/final_datasets/train_ready_dataset.csv`
- `orang_b/final_datasets/train_ready_dataset_full_audit.csv`
- `orang_b/final_datasets/train_ready_v6_sync_summary.csv`
- `orang_b/final_datasets/image_url_refresh_report.csv`

## Catatan

Dataset final v6 berisi 591 makanan, 78 kolom, dan semua row memiliki image URL berformat HTTP/HTTPS. Sebanyak 116 gambar lama yang rusak diganti dengan fallback kategori yang stabil.
