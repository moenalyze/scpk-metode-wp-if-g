import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --- Layout & Judul ---
st.set_page_config(page_title="SPK Weighted Product - Tanaman", layout="wide")
st.title("🌱 Sistem Pendukung Keputusan: Pemilihan Lahan Terbaik untuk Tanaman")

st.markdown(
  """
  <style>
  /* Import Google Font */
  @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');
  
  /* Apply font ke semua teks */
  html, body, .stApp, .stMarkdown, .stButton>button, .stSelectbox, .stTextInput, .stSlider {
      font-family: 'Poppins', sans-serif !important;
  }
  
  /* Judul lebih tebal */
  h1 {
      font-weight: 600 !important;
      color: #D4A373 !important;  # Warna cokelat tanah
  }
  </style>
  """,
  unsafe_allow_html=True
)

# --- Load Dataset ---
df = pd.read_csv("Smart_Farming_Crop_Yield_2024.csv")

# --- Sidebar: Konfigurasi Kriteria ---
with st.sidebar:
    st.header("🔧 Konfigurasi Kriteria")
    nama_tanaman = st.text_input("🌶️ Nama Tanaman", placeholder="Misal: Cabai")

    kriteria_alias = {
        "soil_pH": "pH Tanah",
        "soil_moisture_%": "Kelembapan Tanah (%)",
        "temperature_C": "Suhu (°C)",
        "rainfall_mm": "Curah Hujan (mm)",
        "sunlight_hours": "Jam Matahari (per Hari)"
    }

    kriteria_values = []
    bobot = []

    for col in kriteria_alias:
        st.markdown("___")  # Garis pemisah
        tipe = st.selectbox(f"Tipe Kriteria untuk {kriteria_alias[col]}", ["Benefit", "Cost"], key=f"tipe_{col}")

        # Penjelasan tiap kriteria
        penjelasan = {
            "soil_pH": "pH yang baik untuk tanaman berkisar antara 6.0 hingga 7.0.",
            "soil_moisture_%": "Kelembapan yang ideal untuk pertumbuhan tanaman.",
            "temperature_C": "Suhu yang stabil baik untuk pertumbuhan tanaman.",
            "rainfall_mm": "Jumlah hujan yang diterima selama siklus tanam.",
            "sunlight_hours": "Pencahayaan yang diterima tanaman setiap hari."
        }
        st.markdown(f"**{kriteria_alias[col]}**: {penjelasan[col]}")

        # Slider bobot
        bobot_val = st.slider(f"Bobot {kriteria_alias[col]}", 1, 5, 3, key=f"bobot_{col}")
        bobot.append(bobot_val)
        kriteria_values.append(1 if tipe == "Benefit" else -1)

    if nama_tanaman:
        st.success(f"Analisis akan dilakukan untuk tanaman **{nama_tanaman}**")

# --- Proses Utama Jika Tanaman Diisi ---
if nama_tanaman:
  st.markdown("Metode yang digunakan: **Weighted Product (WP)**")
  with st.expander("ℹ️ Apa itu Metode Weighted Product (WP)?"):
    st.markdown("""
    Metode **Weighted Product** (WP) adalah teknik pengambilan keputusan multikriteria 
    yang menggunakan perkalian terberat dari tiap nilai alternatif terhadap bobot kriteria.

    Rumus utama:
    - Vektor S: `S = ∏(x_ij ^ wj)`
    - Vektor V: `V_i = S_i / ΣS`

    Cocok untuk kasus evaluasi berbasis skor seperti pemilihan lahan.
    """
  )

  # Normalisasi bobot
  norm_bobot = [b / sum(bobot) for b in bobot]

  # Ambil data alternatif dan kriteria
  alternatif = df["farm_id"]
  region = df["region"]
  data_kriteria = df[list(kriteria_alias.keys())].copy()

  st.info("⏳ Sedang memproses data...")

  # Hitung Vektor S
  s = []
  for i in range(len(data_kriteria)):
    s_value = 1
    for j in range(len(kriteria_alias)):
      nilai = data_kriteria.iloc[i, j]
      pangkat = kriteria_values[j] * norm_bobot[j]
      s_value *= nilai ** pangkat
    s.append(s_value)

  # Dataframe hasil S
  s_df = pd.DataFrame({
      "Farm ID": alternatif,
      "Region": region,
      "Vektor S": s
  })

  # Hitung Vektor V
  v = [val / sum(s) for val in s]
  v_df = pd.DataFrame({
      "Farm ID": alternatif,
      "Region": region,
      "Vektor V": v
  })
  
  v_df_sorted = v_df.sort_values(by="Vektor V", ascending=False).reset_index(drop=True)

  # --- Output Utama ---
  st.subheader(f"📊 Hasil Keputusan Lahan Terbaik untuk **{nama_tanaman}**")
  best_farm = v_df_sorted.iloc[v_df_sorted.index[0]]  # Ambil berdasarkan urutan V tertinggi
  st.success(f"""
  ✅ **Keputusan Terbaik**:
  Tanaman **{nama_tanaman}** sebaiknya ditanam di **{best_farm['Farm ID']}**  
  📍 Lokasi: **{best_farm['Region']}**
  """)

  with st.expander("📦 Informasi Dataset"):
    st.markdown(f"""
    - Jumlah data: **{df.shape[0]} baris**
    - Jumlah kriteria: **{len(kriteria_alias)}**
    - Sumber: *Smart_Farming_Crop_Yield_2024.csv (https://www.kaggle.com/datasets/atharvasoundankar/smart-farming-sensor-data-for-yield-prediction/data)*
    """
  )
  
  with st.expander("📂 Lihat Dataset"):
    # jml_data = st.number_input("Masukkan jumlah data yang ingin ditampilkan:", 1, len(df), 10)
  
    # selected_cols = ["farm_id", "region"] + list(kriteria_alias.keys())
    # st.dataframe(df[selected_cols].head(jml_data))
    region_options = df["region"].unique().tolist()
    selected_region = st.selectbox("🔍 Filter berdasarkan Region:", ["Semua"] + region_options)

    # Filter berdasarkan region jika dipilih
    if selected_region != "Semua":
      filtered_df = df[df["region"] == selected_region]
    else:
      filtered_df = df

    jml_data = st.number_input("Masukkan jumlah data yang ingin ditampilkan:", 1, len(filtered_df), 10)

    selected_cols = ["farm_id", "region"] + list(kriteria_alias.keys())
    st.dataframe(
      filtered_df[selected_cols].head(jml_data).reset_index(drop=True),
      hide_index=True
    )
    
    if "latitude" in df.columns and "longitude" in df.columns:
      st.subheader("🗺️ Lokasi Lahan pada Peta")
      st.map(df[["latitude", "longitude"]])

  # --- Expandable Detail ---
  with st.expander("📉 Lihat Detail Perhitungan"):
    tabs = st.tabs(["Matriks Keputusan", "Normalisasi Bobot", "Vektor S", "Vektor V", "Ranking"])

    with tabs[0]:  # Matriks Keputusan
      data_kriteria_indexed = data_kriteria.copy()
      data_kriteria_indexed.index = alternatif
      data_kriteria_indexed.rename(columns=kriteria_alias, inplace=True)
      data_kriteria_indexed.index.name = "Farm ID"
      st.dataframe(data_kriteria_indexed)

    with tabs[1]:  # Normalisasi Bobot
      norm_df = pd.DataFrame({
        "Kriteria": list(kriteria_alias.values()),
        "Bobot": bobot,
        "Normalisasi": norm_bobot
      })
      # norm_df.set_index("Kriteria", inplace=True)
      st.dataframe(norm_df, hide_index=True)
      
      # Pie Chart dengan ukuran lebih kecil dan label kecil
      st.subheader("🧁 Distribusi Bobot (Pie Chart)")
      fig, ax = plt.subplots(figsize=(2, 2))  # Ukuran pie chart lebih kecil
      wedges, texts, autotexts = ax.pie(
        norm_df["Normalisasi"],
        labels=norm_df.index,
        autopct="%1.1f%%",
        startangle=90,
        textprops={'fontsize': 5}  # Mengatur ukuran font label
      )
      ax.axis("equal")  # Biar bulat sempurna

      # Menyesuaikan ukuran font untuk angka persentase
      for autotext in autotexts:
        autotext.set_fontsize(5)  # Mengatur ukuran font angka persentase

      st.pyplot(fig)

    with tabs[2]:  # Vektor S
      s_df_indexed = s_df.copy()
      # s_df_indexed.set_index("Farm ID", inplace=True)
      st.dataframe(s_df_indexed, hide_index=True)

    with tabs[3]:  # Vektor V
      v_df_indexed = v_df.copy()
      # v_df_indexed.set_index("Farm ID", inplace=True)
      st.dataframe(v_df_indexed, hide_index=True)

    with tabs[4]:  # Ranking
      top = st.number_input("Jumlah data teratas:", 1, len(s_df), 10)
      rank_df = v_df.sort_values(by="Vektor V", ascending=False).reset_index(drop=True).copy()
      # rank_df.set_index("Farm ID", inplace=True)
      # st.dataframe(rank_df.head(top))
      st.dataframe(rank_df.head(top).style.apply(
        lambda x: ["background-color: #4E71FF" if i == 0 else "" for i in range(len(x))], axis=0
      ), hide_index=True)
      
      # csv = rank_df.reset_index().to_csv(index=False)
      st.download_button("📥 Download Ranking CSV",rank_df.to_csv(index=False), file_name="ranking_lahan.csv")
      # st.download_button("⬇️ Unduh Hasil Ranking", )


      # Visualisasi Ranking
      # st.subheader("📈 Visualisasi Ranking Farm")
      # st.bar_chart(rank_df["Vektor V"].head(top))


# --- Jika Nama Tanaman Belum Diisi ---
else:  
  st.warning("⚠️ **Waduh, kamu belum masukkan nama tanaman nih** 🌱")
  col1, col2, col3 = st.columns([3, 3, 2])
  with col2:
    st.image("crop.png", caption="Isi nama tanaman terlebih dahulu untuk melanjutkan", width=250)
