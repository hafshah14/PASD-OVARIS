"""
predictor.py
Modul prediksi OVARIS-PCOS.

File ini berisi:
1. fungsi/class untuk memuat model .pkl/.joblib,
2. fungsi pra-pemrosesan input JSON,
3. error handling agar API tidak crash saat input salah,
4. fungsi prediksi yang mengembalikan output JSON-ready.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import joblib
import pandas as pd


MODEL_PATH = Path(__file__).resolve().parent / "model.pkl"


class PredictorError(Exception):
    """Error khusus untuk proses validasi, preprocessing, dan prediksi."""


# Urutan fitur mengikuti kode Streamlit asli OVARIS-PCOS.
DEFAULT_FEATURES: List[str] = [
    "_Age_yrs_",
    "Weight_Kg_",
    "Height_Cm_",
    "BMI",
    "Blood_Group",
    "Pulse_rate_bpm_",
    "RR_breaths_min_",
    "Hb_g_dl_",
    "Cycle_R_I_",
    "Cycle_length_days_",
    "Marraige_Status_Yrs_",
    "Pregnant_Y_N_",
    "No_of_aborptions",
    "_I_beta_HCG_mIU_mL_",
    "II_beta_HCG_mIU_mL_",
    "FSH_mIU_mL_",
    "LH_mIU_mL_",
    "FSH_LH",
    "Hip_inch_",
    "Waist_inch_",
    "Waist_Hip_Ratio",
    "TSH_mIU_L_",
    "AMH_ng_mL_",
    "PRL_ng_mL_",
    "Vit_D3_ng_mL_",
    "PRG_ng_mL_",
    "RBS_mg_dl_",
    "Weight_gain_Y_N_",
    "hair_growth_Y_N_",
    "Skin_darkening_Y_N_",
    "Hair_loss_Y_N_",
    "Pimples_Y_N_",
    "Fast_food_Y_N_",
    "Reg_Exercise_Y_N_",
    "BP__Systolic_mmHg_",
    "BP__Diastolic_mmHg_",
    "Follicle_No_L_",
    "Follicle_No_R_",
    "Avg_F_size_L_mm_",
    "Avg_F_size_R_mm_",
    "Endometrium_mm_",
]


# Nama input API yang wajib dikirim oleh client/frontend.
REQUIRED_INPUT_FIELDS: List[str] = [
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
    "endometrium",
]


# Alias dibuat agar payload tetap mudah disesuaikan dengan label input Streamlit lama.
ALIASES: Dict[str, List[str]] = {
    "patient_name": ["patient_name", "nama_pasien", "name", "nama"],
    "age": ["age", "usia"],
    "weight": ["weight", "berat_badan"],
    "height": ["height", "tinggi_badan"],
    "blood_group": ["blood_group", "golongan_darah"],
    "pulse_rate": ["pulse_rate", "detak_jantung"],
    "rr": ["rr", "respiratory_rate", "laju_pernapasan"],
    "hb": ["hb", "hemoglobin"],
    "cycle": ["cycle", "siklus_tidak_teratur"],
    "cycle_length": ["cycle_length", "panjang_siklus"],
    "marriage_status": ["marriage_status", "lama_pernikahan"],
    "pregnant": ["pregnant", "pernah_hamil"],
    "abortions": ["abortions", "jumlah_keguguran"],
    "beta_hcg_1": ["beta_hcg_1", "beta1", "beta_hcg_i"],
    "beta_hcg_2": ["beta_hcg_2", "beta2", "beta_hcg_ii"],
    "fsh": ["fsh"],
    "lh": ["lh"],
    "tsh": ["tsh"],
    "amh": ["amh"],
    "prl": ["prl", "prolaktin"],
    "vitd": ["vitd", "vitamin_d3"],
    "prg": ["prg", "progesteron"],
    "rbs": ["rbs", "gula_darah_sewaktu"],
    "waist": ["waist", "lingkar_pinggang"],
    "hip": ["hip", "lingkar_pinggul"],
    "weight_gain": ["weight_gain", "kenaikan_berat_badan"],
    "hair_growth": ["hair_growth", "pertumbuhan_rambut_berlebih"],
    "skin_darkening": ["skin_darkening", "penggelapan_kulit"],
    "hair_loss": ["hair_loss", "kerontokan_rambut"],
    "pimples": ["pimples", "jerawat"],
    "fast_food": ["fast_food", "konsumsi_fast_food"],
    "reg_exercise": ["reg_exercise", "olahraga_rutin"],
    "systolic_bp": ["systolic_bp", "tekanan_darah_sistolik"],
    "diastolic_bp": ["diastolic_bp", "tekanan_darah_diastolik"],
    "follicle_l": ["follicle_l", "folikel_kiri"],
    "follicle_r": ["follicle_r", "folikel_kanan"],
    "avg_f_size_l": ["avg_f_size_l", "ukuran_folikel_kiri"],
    "avg_f_size_r": ["avg_f_size_r", "ukuran_folikel_kanan"],
    "endometrium": ["endometrium", "ketebalan_endometrium"],
}


FEATURE_LABELS: Dict[str, str] = {
    "AMH_ng_mL_": "Kadar AMH",
    "Follicle_No_R_": "Jumlah Folikel Ovarium Kanan",
    "Follicle_No_L_": "Jumlah Folikel Ovarium Kiri",
    "Cycle_R_I_": "Siklus Menstruasi Tidak Teratur",
    "Weight_gain_Y_N_": "Kenaikan Berat Badan",
    "hair_growth_Y_N_": "Pertumbuhan Rambut Berlebih",
    "Skin_darkening_Y_N_": "Penggelapan Kulit",
    "LH_mIU_mL_": "Kadar LH",
    "TSH_mIU_L_": "Kadar TSH",
    "RBS_mg_dl_": "Gula Darah Sewaktu",
}


class PCOSPredictor:
    """Class utama untuk memuat model dan menjalankan inferensi PCOS."""

    def __init__(self, model_path: Path | str = MODEL_PATH) -> None:
        self.model_path = Path(model_path)
        self.model: Any = None
        self.features: List[str] = DEFAULT_FEATURES.copy()
        self.load_model()

    def load_model(self) -> None:
        """Memuat model dari file model.pkl."""
        if not self.model_path.exists():
            raise PredictorError(
                f"File model tidak ditemukan: {self.model_path.name}. "
                "Download pcos_streamlit_package.pkl dari repository GitHub, "
                "rename menjadi model.pkl, lalu letakkan sejajar dengan main.py."
            )

        try:
            package = joblib.load(self.model_path)
        except Exception as exc:
            raise PredictorError(f"Model gagal dimuat: {exc}") from exc

        # Mendukung package lama: {"model": ..., "features": ...}
        # dan juga mendukung file yang langsung berisi objek model.
        if isinstance(package, dict):
            if "model" not in package:
                raise PredictorError("Package model tidak memiliki key 'model'.")
            self.model = package["model"]
            self.features = list(package.get("features", DEFAULT_FEATURES))
        else:
            self.model = package
            self.features = DEFAULT_FEATURES.copy()

        if self.model is None:
            raise PredictorError("Objek model kosong atau tidak valid.")

    def _get_value(self, payload: Dict[str, Any], field: str, required: bool = True) -> Any:
        for key in ALIASES.get(field, [field]):
            if key in payload and payload[key] is not None:
                return payload[key]
        if required:
            raise PredictorError(f"Field '{field}' wajib diisi.")
        return None

    def _to_float(self, value: Any, field: str, min_value: Optional[float] = None) -> float:
        if isinstance(value, bool):
            raise PredictorError(f"Field '{field}' harus berupa angka, bukan boolean.")
        try:
            number = float(value)
        except (TypeError, ValueError) as exc:
            raise PredictorError(f"Field '{field}' harus berupa angka.") from exc

        if min_value is not None and number < min_value:
            raise PredictorError(f"Field '{field}' tidak boleh kurang dari {min_value}.")
        return number

    def _to_binary(self, value: Any, field: str) -> int:
        """Konversi Ya/Tidak, true/false, 1/0 menjadi 1/0."""
        if isinstance(value, bool):
            return int(value)
        if isinstance(value, (int, float)) and value in [0, 1]:
            return int(value)
        if isinstance(value, str):
            cleaned = value.strip().lower()
            if cleaned in ["ya", "yes", "y", "true", "1"]:
                return 1
            if cleaned in ["tidak", "no", "n", "false", "0"]:
                return 0
        raise PredictorError(f"Field '{field}' harus berisi Ya/Tidak, true/false, atau 1/0.")

    def _to_cycle_value(self, value: Any) -> float:
        """
        Dataset PCOS umumnya memakai kode Cycle(R/I):
        2 = regular, 4 = irregular.
        Karena UI lama menanyakan 'Siklus Tidak Teratur', maka:
        Ya -> 4, Tidak -> 2. Jika client mengirim angka, angka dipakai apa adanya.
        """
        if isinstance(value, str):
            cleaned = value.strip().lower()
            if cleaned in ["ya", "yes", "y", "true", "1", "irregular", "tidak teratur"]:
                return 4.0
            if cleaned in ["tidak", "no", "n", "false", "0", "regular", "teratur"]:
                return 2.0
        return self._to_float(value, "cycle")

    def preprocess_input(self, payload: Dict[str, Any]) -> pd.DataFrame:
        """Validasi dan transformasi payload JSON menjadi DataFrame model."""
        if not isinstance(payload, dict):
            raise PredictorError("Payload harus berbentuk JSON object/dictionary.")

        age = self._to_float(self._get_value(payload, "age"), "age", 0)
        weight = self._to_float(self._get_value(payload, "weight"), "weight", 1)
        height = self._to_float(self._get_value(payload, "height"), "height", 1)
        blood_group = self._to_float(self._get_value(payload, "blood_group"), "blood_group")
        pulse_rate = self._to_float(self._get_value(payload, "pulse_rate"), "pulse_rate", 0)
        rr = self._to_float(self._get_value(payload, "rr"), "rr", 0)
        hb = self._to_float(self._get_value(payload, "hb"), "hb", 0)

        cycle = self._to_cycle_value(self._get_value(payload, "cycle"))
        cycle_length = self._to_float(self._get_value(payload, "cycle_length"), "cycle_length", 0)
        marriage_status = self._to_float(self._get_value(payload, "marriage_status"), "marriage_status", 0)
        pregnant = self._to_binary(self._get_value(payload, "pregnant"), "pregnant")
        abortions = self._to_float(self._get_value(payload, "abortions"), "abortions", 0)

        beta_hcg_1 = self._to_float(self._get_value(payload, "beta_hcg_1"), "beta_hcg_1", 0)
        beta_hcg_2 = self._to_float(self._get_value(payload, "beta_hcg_2"), "beta_hcg_2", 0)
        fsh = self._to_float(self._get_value(payload, "fsh"), "fsh", 0)
        lh = self._to_float(self._get_value(payload, "lh"), "lh", 0)
        tsh = self._to_float(self._get_value(payload, "tsh"), "tsh", 0)
        amh = self._to_float(self._get_value(payload, "amh"), "amh", 0)
        prl = self._to_float(self._get_value(payload, "prl"), "prl", 0)
        vitd = self._to_float(self._get_value(payload, "vitd"), "vitd", 0)
        prg = self._to_float(self._get_value(payload, "prg"), "prg", 0)
        rbs = self._to_float(self._get_value(payload, "rbs"), "rbs", 0)
        waist = self._to_float(self._get_value(payload, "waist"), "waist", 0)
        hip = self._to_float(self._get_value(payload, "hip"), "hip", 0)

        if lh == 0:
            raise PredictorError("Field 'lh' tidak boleh 0 karena digunakan untuk menghitung rasio FSH/LH.")
        if hip == 0:
            raise PredictorError("Field 'hip' tidak boleh 0 karena digunakan untuk menghitung rasio pinggang-pinggul.")

        weight_gain = self._to_binary(self._get_value(payload, "weight_gain"), "weight_gain")
        hair_growth = self._to_binary(self._get_value(payload, "hair_growth"), "hair_growth")
        skin_darkening = self._to_binary(self._get_value(payload, "skin_darkening"), "skin_darkening")
        hair_loss = self._to_binary(self._get_value(payload, "hair_loss"), "hair_loss")
        pimples = self._to_binary(self._get_value(payload, "pimples"), "pimples")
        fast_food = self._to_binary(self._get_value(payload, "fast_food"), "fast_food")
        reg_exercise = self._to_binary(self._get_value(payload, "reg_exercise"), "reg_exercise")

        systolic_bp = self._to_float(self._get_value(payload, "systolic_bp"), "systolic_bp", 0)
        diastolic_bp = self._to_float(self._get_value(payload, "diastolic_bp"), "diastolic_bp", 0)
        follicle_l = self._to_float(self._get_value(payload, "follicle_l"), "follicle_l", 0)
        follicle_r = self._to_float(self._get_value(payload, "follicle_r"), "follicle_r", 0)
        avg_f_size_l = self._to_float(self._get_value(payload, "avg_f_size_l"), "avg_f_size_l", 0)
        avg_f_size_r = self._to_float(self._get_value(payload, "avg_f_size_r"), "avg_f_size_r", 0)
        endometrium = self._to_float(self._get_value(payload, "endometrium"), "endometrium", 0)

        bmi = weight / ((height / 100) ** 2)
        fsh_lh = fsh / lh
        waist_hip_ratio = waist / hip

        row = {
            "_Age_yrs_": age,
            "Weight_Kg_": weight,
            "Height_Cm_": height,
            "BMI": bmi,
            "Blood_Group": blood_group,
            "Pulse_rate_bpm_": pulse_rate,
            "RR_breaths_min_": rr,
            "Hb_g_dl_": hb,
            "Cycle_R_I_": cycle,
            "Cycle_length_days_": cycle_length,
            "Marraige_Status_Yrs_": marriage_status,
            "Pregnant_Y_N_": pregnant,
            "No_of_aborptions": abortions,
            "_I_beta_HCG_mIU_mL_": beta_hcg_1,
            "II_beta_HCG_mIU_mL_": beta_hcg_2,
            "FSH_mIU_mL_": fsh,
            "LH_mIU_mL_": lh,
            "FSH_LH": fsh_lh,
            "Hip_inch_": hip,
            "Waist_inch_": waist,
            "Waist_Hip_Ratio": waist_hip_ratio,
            "TSH_mIU_L_": tsh,
            "AMH_ng_mL_": amh,
            "PRL_ng_mL_": prl,
            "Vit_D3_ng_mL_": vitd,
            "PRG_ng_mL_": prg,
            "RBS_mg_dl_": rbs,
            "Weight_gain_Y_N_": weight_gain,
            "hair_growth_Y_N_": hair_growth,
            "Skin_darkening_Y_N_": skin_darkening,
            "Hair_loss_Y_N_": hair_loss,
            "Pimples_Y_N_": pimples,
            "Fast_food_Y_N_": fast_food,
            "Reg_Exercise_Y_N_": reg_exercise,
            "BP__Systolic_mmHg_": systolic_bp,
            "BP__Diastolic_mmHg_": diastolic_bp,
            "Follicle_No_L_": follicle_l,
            "Follicle_No_R_": follicle_r,
            "Avg_F_size_L_mm_": avg_f_size_l,
            "Avg_F_size_R_mm_": avg_f_size_r,
            "Endometrium_mm_": endometrium,
        }

        missing_model_features = [feature for feature in self.features if feature not in row]
        if missing_model_features:
            raise PredictorError(
                "Ada fitur model yang belum tersedia pada preprocessing: "
                + ", ".join(missing_model_features)
            )

        df = pd.DataFrame([row])
        return df[self.features]

    def get_top_features(self, top_n: int = 5) -> List[str]:
        """Mengambil faktor utama berdasarkan feature_importances_ jika tersedia."""
        if not hasattr(self.model, "feature_importances_"):
            return []

        try:
            imp_df = pd.DataFrame(
                {
                    "feature": self.features,
                    "importance": list(self.model.feature_importances_),
                }
            )
            top_features = imp_df.sort_values("importance", ascending=False).head(top_n)
            return [
                FEATURE_LABELS.get(str(row["feature"]), str(row["feature"]))
                for _, row in top_features.iterrows()
            ]
        except Exception:
            return []

    def predict(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Menjalankan prediksi dan mengembalikan hasil siap JSON."""
        try:
            df = self.preprocess_input(payload)
            pred = int(self.model.predict(df)[0])

            risk_score_percent = None
            if hasattr(self.model, "predict_proba"):
                probability = float(self.model.predict_proba(df)[0][1])
                risk_score_percent = round(probability * 100, 2)

            risk_label = "Risiko PCOS Tinggi" if pred == 1 else "Risiko PCOS Rendah"

            if pred == 1:
                recommendation = [
                    "Konsultasikan hasil skrining kepada dokter spesialis kandungan.",
                    "Pertimbangkan pemeriksaan hormon reproduksi lanjutan.",
                    "Lakukan pemantauan siklus menstruasi secara rutin.",
                    "Terapkan pola makan sehat dan aktivitas fisik teratur.",
                    "Hasil ini merupakan skrining awal dan bukan diagnosis medis.",
                ]
            else:
                recommendation = [
                    "Risiko PCOS tergolong rendah berdasarkan data yang dimasukkan.",
                    "Tetap pertahankan pola hidup sehat.",
                    "Lakukan pemeriksaan berkala jika muncul gejala PCOS.",
                    "Hasil ini merupakan skrining awal dan bukan diagnosis medis.",
                ]

            return {
                "status": "success",
                "patient_name": self._get_value(payload, "patient_name", required=False) or "-",
                "prediction": pred,
                "risk_label": risk_label,
                "risk_score_percent": risk_score_percent,
                "top_features": self.get_top_features(),
                "recommendation": recommendation,
            }
        except PredictorError:
            raise
        except Exception as exc:
            raise PredictorError(f"Terjadi kesalahan saat proses inferensi: {exc}") from exc
