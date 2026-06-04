# A/B Testing Plan - NutriMatch Recommendation

## Tujuan

Menguji apakah fitur tambahan Data Science meningkatkan kualitas rekomendasi dibanding baseline yang hanya memilih makanan dengan skor nutrisi terbaik.

## Variant

| Variant | Deskripsi |
|---|---|
| A - Baseline | Ranking berdasarkan skor nutrisi dan batasan alergi dasar. |
| B - Feature-rich | Ranking memakai nutrisi, alergi, `food_category`, `base_ingredient`, `primary_meal_time`, `halal_status`, dan `pairing_group`. |

## Primary Metrics

- Acceptance rate rekomendasi.
- Diversity score makanan yang tampil.
- Jumlah rekomendasi yang berulang dalam satu sesi.
- Valid meal-combo rate berdasarkan `meal_combo_valid`.

## Guardrail Metrics

- Tidak merekomendasikan item `contains_unknown=True` untuk user alergi kritis.
- Tidak merekomendasikan `halal_status != halal_candidate` pada mode halal-only.
- Tidak menampilkan makanan dengan `image_url_status` selain `ok` atau `refreshed`.

## Segmentasi Pengujian

- User dengan alergi.
- User halal-only.
- Meal time: breakfast, lunch, dinner.
- Target kalori: defisit, maintenance, surplus.

## Rencana Eksekusi

1. AI Engineer menjalankan variant A dan B pada user profile dummy.
2. Fullstack menampilkan rekomendasi dan mencatat klik/accept.
3. Data Scientist mengevaluasi diversity, meal pairing, dan guardrail.
4. Variant B dinyatakan menang jika diversity meningkat tanpa melanggar guardrail alergi/halal.

## Output yang Diharapkan

- Tabel hasil A/B test.
- Rekomendasi rule ranking final untuk AI Engineer.
- Catatan risiko dan edge case.
