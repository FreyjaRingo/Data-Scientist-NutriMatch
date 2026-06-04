# NutriMatch Streamlit Dashboard

Dashboard interaktif untuk audit dataset train-ready NutriMatch.

## Isi folder

- `app.py` - aplikasi Streamlit utama.
- `data/train_ready_dataset.csv` - dataset final siap training yang dipakai dashboard.
- `requirements.txt` - dependency untuk Streamlit Cloud.
- `.streamlit/config.toml` - konfigurasi tema dan server.

## Jalankan lokal

```bash
streamlit run streamlit_dashboard/app.py
```

## Deploy lewat GitHub dan Streamlit Cloud

1. Push repo ini ke GitHub.
2. Buka Streamlit Cloud.
3. Pilih repo GitHub yang berisi folder ini.
4. Set branch ke `master`.
5. Set main file path ke `streamlit_dashboard/app.py`.
6. Deploy.

Dashboard akan membaca `streamlit_dashboard/data/train_ready_dataset.csv`. Jika dataset dipindah, set environment variable `NUTRIMATCH_DATASET_PATH` ke path CSV yang baru.
