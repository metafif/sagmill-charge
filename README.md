# Framework Python untuk Prediksi Muatan Bola Baja SAG Mill

Framework komputasional berbasis Python untuk estimasi dan prediksi muatan bola baja Semi-Autogenous Grinding (SAG) mill secara real-time.

## Deskripsi

Framework ini mengintegrasikan:
- **Model power draw C-Shape Morrell** untuk estimasi fill level dan muatan bola baja
- **Rekonsiliasi geometri dinamis** akibat keausan liner
- **Modul prediksi penambahan bola adaptif** berbasis shift dengan logika fixed timing

Divalidasi melalui simulasi Monte Carlo time-series selama 180 hari (satu siklus liner penuh) sebagai *proof-of-concept*.

## Fitur Utama

| Modul | Fungsi |
|-------|--------|
| Model Morrell C-Shape | Forward power draw dan inverse estimation (SLSQP) |
| Rekonsiliasi Liner | Perhitungan geometri dinamis akibat keausan liner |
| Predictive Module | Prediksi penambahan bola 24 jam ke depan |
| Improvement Modules | EMA filter, rate limiter, drift compensation, adaptive wear rate |
| Monte Carlo Validation | Perbandingan skenario prediktif vs konstan |

## Prasyarat

- [Anaconda Distribution](https://www.anaconda.com/download) (Python 3.8+)
- Package: NumPy, SciPy, Pandas, Matplotlib

Package sudah tersedia secara default di Anaconda. Jika belum:

```bash
conda install numpy scipy pandas matplotlib


## Penggunaan

### 1. Clone Repository

```bash
git clone https://github.com/metafif/sagmill-charge
cd sagmill-charge
```

### 2. Jalankan Simulasi

Buka **Anaconda Prompt**, navigasi ke folder repo, lalu jalankan:

```bash
python sag_predictive_framework.py
```

Atau buka file `sag_predictive_framework.py` di **Jupyter Notebook Lab** (termasuk di Anaconda), lalu run cell/script.

### 3. Output

Terminal akan menampilkan:
- MAPE skenario konstan vs prediktif
- Error akhir hari ke-180
- Statistik penambahan harian

Grafik otomatis muncul (4 panel):
- Tracking Jb selama 180 hari
- Profil penambahan harian
- Estimation bias (raw vs filtered)
- Load cell drift compensation

## Parameter Simulasi

| Parameter | Nilai | Satuan |
|-----------|-------|--------|
| Diameter mill (pasca-reline) | 12.20 | m |
| Panjang EGL | 6.10 | m |
| Panjang cone | 1.50 | m |
| Kecepatan putar | 8.99 | rpm |
| Densitas bola baja | 7.80 | t/m³ |
| Densitas bijih | 2.65 | t/m³ |
| Porositas charge | 0.40 | — |
| Target Jb | 0.15 | fraksi |
| Target Jt | 0.35 | fraksi |
| TPH nominal | 2200 | ton/jam |
| Shift per hari | 3 | shift |
| Jam per shift | 8 | jam |
| Durasi simulasi | 180 | hari |
| Tonnase total siklus | 9.0 | juta ton |
| Tebal liner baru / akhir | 200 / 80 | mm |

Parameter dapat dimodifikasi langsung di bagian awal script (`# PARAMETER ...`).

## Struktur File

```
nama-repo/
├── sag_predictive_framework.py    # Script utama (semua fungsi dalam satu file)
├── README.md
├── LICENSE
└── .gitignore
```


## Lisensi

MIT License — lihat [LICENSE](LICENSE) untuk detail.

## Publikasi

Artikel terkait: *Framework Python untuk Prediksi dan Penambahan Muatan Bola Baja Semi-Autogenous Grinding (SAG) Mill Berbasis Model C Morrell*

## Kontak

[Muhammad 'Afif] — [me@muhammadafif.web.id]

---

**Disclaimer**: Framework ini merupakan *proof-of-concept* berbasis simulasi. Implementasi pada SAG mill komersial memerlukan kalibrasi parameter sesuai kondisi aktual dan validasi lapangan.
