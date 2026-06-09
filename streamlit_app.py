import streamlit as st
import requests

st.set_page_config(
    page_title="OVARIS-PCOS",
    page_icon="🩺",
    layout="wide"
)

st.title("🩺 OVARIS-PCOS")
st.subheader("Ovarian Risk Assessment and Screening System")

with st.form("pcos_form"):

    st.header("👤 Data Dasar")

    col1, col2 = st.columns(2)

    with col1:
        patient_name = st.text_input("Nama Pasien")
        age = st.number_input("Usia (tahun)", 10, 60, 24)
        weight = st.number_input("Berat Badan (kg)", 20.0, 200.0, 60.0)
        height = st.number_input("Tinggi Badan (cm)", 100.0, 220.0, 160.0)

    with col2:
        blood_group = st.selectbox(
            "Golongan Darah",
            ["O", "A", "B", "AB"]
        )
        
        blood_mapping = {
            "A": 11,
            "B": 13,
            "O": 15,
            "AB": 17
        }

        blood_group_encoded = blood_mapping[blood_group]

        pulse_rate = st.number_input(
            "Detak Jantung (bpm)",
            40,
            200,
            78
        )

        rr = st.number_input(
            "Laju Pernapasan",
            10,
            40,
            18
        )

        hb = st.number_input(
            "Hemoglobin (g/dL)",
            0.0,
            20.0,
            12.8
        )

    st.header("🩸 Riwayat Reproduksi")

    col1, col2 = st.columns(2)

    with col1:
        cycle = st.selectbox(
            "Siklus Menstruasi Tidak Teratur",
            ["Ya", "Tidak"]
        )

        cycle_length = st.number_input(
            "Panjang Siklus (Hari)",
            1,
            100,
            35
        )

        marriage_status = st.number_input(
            "Lama Pernikahan (Tahun)",
            0,
            40,
            0
        )

    with col2:
        pregnant = st.selectbox(
            "Pernah Hamil",
            ["Ya", "Tidak"]
        )

        abortions = st.number_input(
            "Jumlah Keguguran",
            0,
            20,
            0
        )

    st.header("🧪 Pemeriksaan Laboratorium")

    col1, col2 = st.columns(2)

    with col1:
        beta_hcg_1 = st.number_input("Beta HCG I", value=1.99)
        beta_hcg_2 = st.number_input("Beta HCG II", value=1.99)

        fsh = st.number_input(
            "FSH",
            min_value=0.01,
            value=6.5
        )

        lh = st.number_input(
            "LH",
            min_value=0.01,
            value=8.2
        )

        tsh = st.number_input(
            "TSH",
            value=2.1
        )

    with col2:
        amh = st.number_input(
            "AMH",
            value=5.8
        )

        prl = st.number_input(
            "Prolaktin (PRL)",
            value=18.5
        )

        vitd = st.number_input(
            "Vitamin D3",
            value=24.5
        )

        prg = st.number_input(
            "Progesteron",
            value=0.7
        )

        rbs = st.number_input(
            "Gula Darah Sewaktu (RBS)",
            value=92.0
        )

    st.header("📏 Pengukuran Tubuh")

    col1, col2 = st.columns(2)

    with col1:
        waist = st.number_input(
            "Lingkar Pinggang (inch)",
            value=32.0
        )

    with col2:
        hip = st.number_input(
            "Lingkar Pinggul (inch)",
            min_value=1.0,
            value=38.0
        )

    st.header("⚠️ Gejala PCOS")

    col1, col2 = st.columns(2)

    with col1:
        weight_gain = st.selectbox(
            "Kenaikan Berat Badan",
            ["Ya", "Tidak"]
        )

        hair_growth = st.selectbox(
            "Pertumbuhan Rambut Berlebih",
            ["Ya", "Tidak"]
        )

        skin_darkening = st.selectbox(
            "Penggelapan Kulit",
            ["Ya", "Tidak"]
        )

        hair_loss = st.selectbox(
            "Kerontokan Rambut",
            ["Ya", "Tidak"]
        )

    with col2:
        pimples = st.selectbox(
            "Jerawat",
            ["Ya", "Tidak"]
        )

        fast_food = st.selectbox(
            "Sering Konsumsi Fast Food",
            ["Ya", "Tidak"]
        )

        reg_exercise = st.selectbox(
            "Olahraga Rutin",
            ["Ya", "Tidak"]
        )

    st.header("🏥 Pemeriksaan Tambahan")

    col1, col2 = st.columns(2)

    with col1:
        systolic_bp = st.number_input(
            "Tekanan Darah Sistolik",
            value=120
        )

        diastolic_bp = st.number_input(
            "Tekanan Darah Diastolik",
            value=80
        )

        follicle_l = st.number_input(
            "Jumlah Folikel Ovarium Kiri",
            value=8
        )

        follicle_r = st.number_input(
            "Jumlah Folikel Ovarium Kanan",
            value=10
        )

    with col2:
        avg_f_size_l = st.number_input(
            "Ukuran Folikel Kiri (mm)",
            value=12.0
        )

        avg_f_size_r = st.number_input(
            "Ukuran Folikel Kanan (mm)",
            value=13.0
        )

        endometrium = st.number_input(
            "Ketebalan Endometrium (mm)",
            value=8.5
        )

    submit = st.form_submit_button(
        "🔍 Prediksi Risiko PCOS"
    )

if submit:

    payload = {
        "patient_name": patient_name,
        "age": age,
        "weight": weight,
        "height": height,
        "blood_group": blood_group_encoded,
        "pulse_rate": pulse_rate,
        "rr": rr,
        "hb": hb,
        "cycle": cycle,
        "cycle_length": cycle_length,
        "marriage_status": marriage_status,
        "pregnant": pregnant,
        "abortions": abortions,
        "beta_hcg_1": beta_hcg_1,
        "beta_hcg_2": beta_hcg_2,
        "fsh": fsh,
        "lh": lh,
        "tsh": tsh,
        "amh": amh,
        "prl": prl,
        "vitd": vitd,
        "prg": prg,
        "rbs": rbs,
        "waist": waist,
        "hip": hip,
        "weight_gain": weight_gain,
        "hair_growth": hair_growth,
        "skin_darkening": skin_darkening,
        "hair_loss": hair_loss,
        "pimples": pimples,
        "fast_food": fast_food,
        "reg_exercise": reg_exercise,
        "systolic_bp": systolic_bp,
        "diastolic_bp": diastolic_bp,
        "follicle_l": follicle_l,
        "follicle_r": follicle_r,
        "avg_f_size_l": avg_f_size_l,
        "avg_f_size_r": avg_f_size_r,
        "endometrium": endometrium
    }

    try:

        response = requests.post(
            "http://127.0.0.1:8000/predict",
            json=payload
        )

        result = response.json()

        if response.status_code == 200:

            st.success(result["risk_label"])

            score = result.get(
                "risk_score_percent",
                0
            )

            st.metric(
                "Skor Risiko PCOS",
                f"{score}%"
            )

            st.progress(min(score / 100, 1.0))

            st.subheader("📊 Faktor Utama")

            for factor in result["top_features"]:
                st.write("•", factor)

            st.subheader("💡 Rekomendasi")

            for rec in result["recommendation"]:
                st.write("•", rec)

        else:
            st.error(result["message"])

    except Exception as e:
        st.error(f"Gagal terhubung ke API: {e}")