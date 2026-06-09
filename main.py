"""
main.py
Web Service API untuk OVARIS-PCOS menggunakan FastAPI.

Endpoint utama:
- GET  /        : informasi singkat API
- GET  /health  : status server dan model
- POST /predict : menerima payload JSON dan mengembalikan prediksi risiko PCOS
"""

from __future__ import annotations

from typing import Any, Dict

from fastapi import Body, FastAPI
from fastapi.responses import JSONResponse

from predictor import MODEL_PATH, PCOSPredictor, PredictorError, REQUIRED_INPUT_FIELDS


app = FastAPI(
    title="OVARIS-PCOS API",
    description="Ovarian Risk Assessment and Screening System berbasis Web Service API.",
    version="1.0.0",
)


try:
    predictor = PCOSPredictor(MODEL_PATH)
    startup_error = None
except PredictorError as exc:
    predictor = None
    startup_error = str(exc)


@app.get("/")
def root() -> Dict[str, Any]:
    return {
        "app": "OVARIS-PCOS API",
        "description": "Sistem skrining risiko PCOS berbasis model Machine Learning.",
        "main_endpoint": "POST /predict",
        "documentation": "/docs",
        "model_loaded": predictor is not None,
    }


@app.get("/health")
def health_check() -> Dict[str, Any]:
    return {
        "status": "ok" if predictor is not None else "error",
        "model_loaded": predictor is not None,
        "model_file": str(MODEL_PATH.name),
        "message": "Model siap digunakan." if predictor is not None else startup_error,
    }


@app.post("/predict")
def predict_pcos(
    payload: Dict[str, Any] = Body(
        ...,
        example={
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
            "endometrium": 8.5,
        },
    )
) -> JSONResponse:
    if predictor is None:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Model belum siap digunakan.",
                "detail": startup_error,
                "solution": "Pastikan file model.pkl sudah berada satu folder dengan main.py.",
            },
        )

    try:
        result = predictor.predict(payload)
        return JSONResponse(status_code=200, content=result)
    except PredictorError as exc:
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": str(exc),
                "required_fields": REQUIRED_INPUT_FIELDS,
            },
        )
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Terjadi kesalahan internal pada server.",
                "detail": str(exc),
            },
        )
