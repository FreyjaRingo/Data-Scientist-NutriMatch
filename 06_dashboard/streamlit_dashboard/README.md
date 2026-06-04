# NutriMatch Streamlit Dashboard

Dashboard interaktif untuk audit dataset train-ready NutriMatch.

Repo ini adalah versi publish-ready untuk Streamlit Cloud. Struktur folder dibuat flat agar Streamlit bisa langsung menjalankan `app.py` dari root repository.

## Isi folder

- `app.py` - aplikasi Streamlit utama.
- `data/train_ready_dataset.csv` - dataset final siap training yang dipakai dashboard.
- `data/user_profile_features_schema.csv` - sample schema profil user untuk BMR, TDEE, target kalori, dan target makro.
- `data/README.md` - catatan ringkas dataset dashboard.
- `requirements.txt` - dependency untuk Streamlit Cloud.
- `.streamlit/config.toml` - konfigurasi tema dan server.

## Dataset

Dashboard membaca dataset dari:

```text
data/train_ready_dataset.csv
data/user_profile_features_schema.csv
```

Dataset makanan adalah salinan dari folder Data Science final:

```text
Final data scientist/03_final_datasets/main/train_ready_dataset.csv
```

Schema profil user adalah salinan dari:

```text
Final data scientist/03_final_datasets/main/user_profile_features_schema.csv
```

State dataset aktif:

- 484 baris
- 80 kolom
- `image_url_status` hanya berisi `ok` dan `refreshed`
- `halal_status` mayoritas `halal_candidate`

Catatan: kalori, protein, lemak, karbohidrat, dan flag alergen berasal dari dataset makanan. BMR, TDEE, target kalori, dan target makro berasal dari schema profil user, sehingga ditampilkan di tab dashboard yang terpisah.

## Fitur Dashboard

- Overview dataset dan KPI utama.
- Tab `Nutrisi & Alergi` untuk distribusi kalori/makro, flag alergen, BMR, TDEE, dan target makro user.
- Food Explorer dengan filter dan download CSV.
- Recommendation QA untuk audit pairing dan variasi rekomendasi.
- Dataset Audit untuk status cleaning, halal, dan image URL.

## Jalankan lokal

```bash
pip install -r requirements.txt
streamlit run app.py
```

Jika dataset dipindah, set environment variable:

- `NUTRIMATCH_DATASET_PATH` untuk path CSV makanan.
- `NUTRIMATCH_PROFILE_SCHEMA_PATH` untuk path CSV schema profil user.

## Deploy lewat GitHub dan Streamlit Cloud

1. Push repo ini ke GitHub.
2. Buka Streamlit Cloud.
3. Pilih repository `FreyjaRingo/CC26-Dashboard-Streamlit`.
4. Set branch ke `main`.
5. Set main file path ke `app.py`.
6. Deploy.

Dashboard akan membaca `data/train_ready_dataset.csv` secara default.
