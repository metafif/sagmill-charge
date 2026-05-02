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
