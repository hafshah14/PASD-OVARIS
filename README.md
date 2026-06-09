# OVARIS-PCOS API

**OVARIS-PCOS** adalah *Ovarian Risk Assessment and Screening System*, yaitu sistem skrining risiko PCOS berbasis model Machine Learning. Versi ini merupakan hasil refactoring dari aplikasi Streamlit menjadi **Web Service API** agar dapat diintegrasikan dengan aplikasi Android maupun Web Frontend.

> Catatan: Hasil prediksi merupakan skrining awal dan bukan diagnosis medis. Pemeriksaan dan interpretasi klinis tetap perlu dilakukan oleh tenaga kesehatan.

---

## 1. Struktur File

```text
OVARIS-PCOS-API/
├── model.pkl                  # File binary model Machine Learning
├── predictor.py               # Modul load model, preprocessing, error handling, dan prediksi
├── main.py                    # Web Service API menggunakan FastAPI
├── requirements.txt           # Daftar dependensi/library
├── sample_payload_valid.json  # Contoh payload JSON valid
├── sample_payload_error.json  # Contoh payload JSON error
└── README.md                  # Dokumentasi teknis
```

---

## 2. Persiapan File Model

Repository asal menggunakan file model bernama:

```text
pcos_streamlit_package.pkl
```

Agar sesuai instruksi praktikum, rename file tersebut menjadi:

```text
model.pkl
```

Lalu letakkan file `model.pkl` di folder yang sama dengan `main.py` dan `predictor.py`.

---

## 3. Instalasi Dependensi

Buka terminal pada folder project, lalu jalankan:

```bash
python -m venv .venv
```

Aktifkan virtual environment.

Untuk macOS/Linux:

```bash
source .venv/bin/activate
```

Untuk Windows:

```bash
.venv\Scripts\activate
```

Install semua library:

```bash
pip install -r requirements.txt
```

---

## 4. Menjalankan Server API

Jalankan server dengan perintah:

```bash
uvicorn main:app --reload
```

Jika berhasil, server berjalan di:

```text
http://127.0.0.1:8000
```

Dokumentasi interaktif FastAPI dapat dibuka di:

```text
http://127.0.0.1:8000/docs
```

---

## 5. Endpoint API

### GET `/`

Digunakan untuk mengecek informasi dasar API.

Contoh respons:

```json
{
  "app": "OVARIS-PCOS API",
  "description": "Sistem skrining risiko PCOS berbasis model Machine Learning.",
  "main_endpoint": "POST /predict",
  "documentation": "/docs",
  "model_loaded": true
}
```

### GET `/health`

Digunakan untuk mengecek apakah server dan model siap digunakan.

Contoh respons sukses:

```json
{
  "status": "ok",
  "model_loaded": true,
  "model_file": "model.pkl",
  "message": "Model siap digunakan."
}
```

### POST `/predict`

Digunakan untuk mengirim data pasien dalam format JSON dan menerima hasil prediksi risiko PCOS.

---

## 6. Contoh Payload Valid

```json
{
  "patient_name": "Alya",
  "age": 24,
  "weight": 62,
  "height": 158,
  "blood_group": 13,
  "pulse_rate": 78,
  "rr": 18,
  "hb": 12.8,
  "cycle": "Ya",
  "cycle_length": 35,
  "marriage_status": 0,
  "pregnant": "Tidak",
  "abortions": 0,
  "beta_hcg_1": 1.99,
  "beta_hcg_2": 1.99,
  "fsh": 6.5,
  "lh": 8.2,
  "tsh": 2.1,
  "amh": 5.8,
  "prl": 18.5,
  "vitd": 24.5,
  "prg": 0.7,
  "rbs": 92,
  "waist": 32,
  "hip": 38,
  "weight_gain": "Ya",
  "hair_growth": "Ya",
  "skin_darkening": "Tidak",
  "hair_loss": "Tidak",
  "pimples": "Ya",
  "fast_food": "Ya",
  "reg_exercise": "Tidak",
  "systolic_bp": 120,
  "diastolic_bp": 80,
  "follicle_l": 8,
  "follicle_r": 10,
  "avg_f_size_l": 12,
  "avg_f_size_r": 13,
  "endometrium": 8.5
}
```

Keterangan khusus:

- `cycle` dapat diisi `Ya` jika siklus tidak teratur dan `Tidak` jika siklus teratur.
- Input Ya/Tidak lain seperti `pregnant`, `weight_gain`, `hair_growth`, `skin_darkening`, `hair_loss`, `pimples`, `fast_food`, dan `reg_exercise` dapat dikirim dalam bentuk `Ya/Tidak`, `true/false`, atau `1/0`.
- `height` dalam cm.
- `waist` dan `hip` dalam inch.
- `lh` dan `hip` tidak boleh 0 karena digunakan dalam perhitungan rasio.

---

## 7. Contoh Respons Prediksi Sukses

```json
{
  "status": "success",
  "patient_name": "Alya",
  "prediction": 1,
  "risk_label": "Risiko PCOS Tinggi",
  "risk_score_percent": 86.42,
  "top_features": [
    "Kadar AMH",
    "Jumlah Folikel Ovarium Kanan",
    "Jumlah Folikel Ovarium Kiri",
    "Siklus Menstruasi Tidak Teratur",
    "Kenaikan Berat Badan"
  ],
  "recommendation": [
    "Konsultasikan hasil skrining kepada dokter spesialis kandungan.",
    "Pertimbangkan pemeriksaan hormon reproduksi lanjutan.",
    "Lakukan pemantauan siklus menstruasi secara rutin.",
    "Terapkan pola makan sehat dan aktivitas fisik teratur.",
    "Hasil ini merupakan skrining awal dan bukan diagnosis medis."
  ]
}
```

Nilai `risk_score_percent` dapat berbeda bergantung pada model dan data input yang dikirimkan.

---

## 8. Contoh Respons Error

Jika field numerik dikirim sebagai teks, misalnya:

```json
{
  "patient_name": "Alya",
  "age": "dua puluh empat",
  "weight": 62,
  "height": 158
}
```

Maka API akan mengembalikan respons seperti:

```json
{
  "status": "error",
  "message": "Field 'age' harus berupa angka.",
  "required_fields": [
    "age",
    "weight",
    "height",
    "blood_group",
    "pulse_rate",
    "rr",
    "hb",
    "cycle",
    "cycle_length",
    "marriage_status",
    "pregnant",
    "abortions",
    "beta_hcg_1",
    "beta_hcg_2",
    "fsh",
    "lh",
    "tsh",
    "amh",
    "prl",
    "vitd",
    "prg",
    "rbs",
    "waist",
    "hip",
    "weight_gain",
    "hair_growth",
    "skin_darkening",
    "hair_loss",
    "pimples",
    "fast_food",
    "reg_exercise",
    "systolic_bp",
    "diastolic_bp",
    "follicle_l",
    "follicle_r",
    "avg_f_size_l",
    "avg_f_size_r",
    "endometrium"
  ]
}
```

---

## 9. Cara Menguji Melalui Swagger UI

1. Jalankan server:

   ```bash
   uvicorn main:app --reload
   ```

2. Buka browser:

   ```text
   http://127.0.0.1:8000/docs
   ```

3. Pilih endpoint `POST /predict`.
4. Klik **Try it out**.
5. Masukkan payload JSON valid.
6. Klik **Execute**.
7. Periksa hasil prediksi pada bagian response body.

---

## 10. Cara Menguji Melalui cURL

```bash
curl -X POST "http://127.0.0.1:8000/predict" \
  -H "Content-Type: application/json" \
  -d @sample_payload_valid.json
```

---

## 11. Ringkasan Alur Sistem

1. Client mengirim data pasien dalam format JSON ke endpoint `/predict`.
2. `main.py` menerima request JSON dari client.
3. Data dikirim ke `predictor.py`.
4. `predictor.py` melakukan validasi input, konversi tipe data, perhitungan BMI, rasio FSH/LH, dan rasio pinggang-pinggul.
5. Data disusun sesuai urutan fitur model.
6. Model menghasilkan prediksi risiko PCOS.
7. API mengembalikan hasil prediksi, skor risiko, faktor utama, dan rekomendasi dalam format JSON.

---

## 12. Catatan Pengembangan

Versi ini mempertahankan tema dan isi utama OVARIS-PCOS, yaitu skrining risiko PCOS. Perubahan yang dilakukan hanya pada struktur implementasi, dari aplikasi Streamlit monolitik menjadi Web Service API yang lebih modular, siap diuji, dan lebih mudah diintegrasikan dengan frontend.
