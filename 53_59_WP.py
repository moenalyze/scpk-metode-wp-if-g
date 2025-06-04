import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --- Setup Page ---
def setup_page():
  st.set_page_config(page_title="SPK Weighted Product - Tanaman", layout="wide")
  st.title("🌱 Sistem Pendukung Keputusan: Pemilihan Lahan Terbaik untuk Tanaman")
  apply_custom_style()

def apply_custom_style():
  st.markdown("""
  <style>
  @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');
  html, body, .stApp, .stMarkdown, .stButton>button, .stSelectbox, .stTextInput, .stSlider {
    font-family: 'Poppins', sans-serif !important;
  }
  h1 {
    font-weight: 600 !important;
    color: #D4A373 !important;
  }
  </style>
  """, unsafe_allow_html=True)

# --- Sidebar Config ---
def sidebar_konfigurasi(kriteria_alias):
  st.sidebar.header("🔧 Konfigurasi Kriteria")
  nama_tanaman = st.sidebar.text_input("🌶️ Nama Tanaman", placeholder="Misal: Cabai")
  
  kriteria_values, bobot = [], []
  for col in kriteria_alias:
    st.sidebar.markdown("___")
    tipe = st.sidebar.selectbox(f"Tipe Kriteria untuk {kriteria_alias[col]}", ["Benefit", "Cost"], key=f"tipe_{col}")

    penjelasan = {
      "soil_pH": "pH yang baik untuk tanaman berkisar antara 6.0 hingga 7.0.",
      "soil_moisture_%": "Kelembapan yang ideal untuk pertumbuhan tanaman.",
      "temperature_C": "Suhu yang stabil baik untuk pertumbuhan tanaman.",
      "rainfall_mm": "Jumlah hujan yang diterima selama siklus tanam.",
      "sunlight_hours": "Pencahayaan yang diterima tanaman setiap hari."
    }
    st.sidebar.markdown(f"**{kriteria_alias[col]}**: {penjelasan[col]}")
    bobot_val = st.sidebar.slider(f"Bobot {kriteria_alias[col]}", 1, 5, 3, key=f"bobot_{col}")
    bobot.append(bobot_val)
    kriteria_values.append(1 if tipe == "Benefit" else -1)
  
  if nama_tanaman:
    st.sidebar.success(f"Analisis akan dilakukan untuk tanaman **{nama_tanaman}**")

  return nama_tanaman, kriteria_values, bobot

# --- Weighted Product Calculation ---
def weighted_product(data_kriteria, kriteria_values, bobot):
  norm_bobot = [b / sum(bobot) for b in bobot]
  s = []

  for i in range(len(data_kriteria)):
    s_value = 1
    for j in range(len(data_kriteria.columns)):
      nilai = data_kriteria.iloc[i, j]
      pangkat = kriteria_values[j] * norm_bobot[j]
      s_value *= nilai ** pangkat
    s.append(s_value)

  return s, norm_bobot

# --- Tampilan Hasil ---
def tampilkan_hasil(df, kriteria_alias, nama_tanaman, s, norm_bobot):
  alternatif = df["farm_id"]
  region = df["region"]
  v = [val / sum(s) for val in s]

  s_df = pd.DataFrame({"Farm ID": alternatif, "Region": region, "Vektor S": s})
  v_df = pd.DataFrame({"Farm ID": alternatif, "Region": region, "Vektor V": v})
  v_df_sorted = v_df.sort_values(by="Vektor V", ascending=False).reset_index(drop=True)

  best_farm = v_df_sorted.iloc[0]
  st.subheader(f"📊 Hasil Keputusan Lahan Terbaik untuk **{nama_tanaman}**")
  st.success(f"""
  ✅ **Keputusan Terbaik**:
  Tanaman **{nama_tanaman}** sebaiknya ditanam di **{best_farm['Farm ID']}**  
  📍 Lokasi: **{best_farm['Region']}**
  """)

  tampilkan_dataset(df, kriteria_alias)
  tampilkan_detail(df, kriteria_alias, norm_bobot, s_df, v_df)

# --- Tampilan Dataset ---
def tampilkan_dataset(df, kriteria_alias):
  with st.expander("📂 Lihat Dataset"):
    region_options = df["region"].unique().tolist()
    selected_region = st.selectbox("🔍 Filter berdasarkan Region:", ["Semua"] + region_options)

    filtered_df = df if selected_region == "Semua" else df[df["region"] == selected_region]
    jml_data = st.number_input("Masukkan jumlah data yang ingin ditampilkan:", 1, len(filtered_df), 10)

    selected_cols = ["farm_id", "region"] + list(kriteria_alias.keys())
    st.dataframe(filtered_df[selected_cols].head(jml_data).reset_index(drop=True), hide_index=True)

    if "latitude" in df.columns and "longitude" in df.columns:
      st.subheader("🗺️ Lokasi Lahan pada Peta")
      st.map(df[["latitude", "longitude"]])

# --- Detail Perhitungan ---
def tampilkan_detail(df, kriteria_alias, norm_bobot, s_df, v_df):
  with st.expander("📉 Lihat Detail Perhitungan"):
    tabs = st.tabs(["Matriks Keputusan", "Normalisasi Bobot", "Vektor S", "Vektor V", "Ranking"])

    # Matriks Keputusan
    data_kriteria = df[list(kriteria_alias.keys())]
    with tabs[0]:
      data_kriteria_indexed = data_kriteria.copy()
      data_kriteria_indexed.index = df["farm_id"]
      data_kriteria_indexed.rename(columns=kriteria_alias, inplace=True)
      data_kriteria_indexed.index.name = "Farm ID"
      st.dataframe(data_kriteria_indexed)

    # Normalisasi Bobot
    with tabs[1]:
      norm_df = pd.DataFrame({
        "Kriteria": list(kriteria_alias.values()),
        "Bobot": bobot,
        "Normalisasi": norm_bobot
      })
      st.dataframe(norm_df, hide_index=True)
      st.subheader("🧁 Distribusi Bobot (Pie Chart)")
      fig, ax = plt.subplots(figsize=(2, 2))
      wedges, texts, autotexts = ax.pie(
        norm_df["Normalisasi"],
        labels=norm_df["Kriteria"],
        autopct="%1.1f%%",
        startangle=90,
        textprops={'fontsize': 5}
      )
      for autotext in autotexts:
        autotext.set_fontsize(5)
      ax.axis("equal")
      st.pyplot(fig)

    # Vektor S
    with tabs[2]:
      st.dataframe(s_df, hide_index=True)

    # Vektor V
    with tabs[3]:
      st.dataframe(v_df, hide_index=True)

    # Ranking
    with tabs[4]:
      top = st.number_input("Jumlah data teratas:", 1, len(v_df), 10)
      rank_df = v_df.sort_values(by="Vektor V", ascending=False).reset_index(drop=True)
      st.dataframe(rank_df.head(top).style.apply(
          lambda x: ["background-color: #4E71FF" if i == 0 else "" for i in range(len(x))], axis=0
      ), hide_index=True)
      st.download_button("📥 Download Ranking CSV", rank_df.to_csv(index=False), file_name="ranking_lahan.csv")

# --- Main ---
setup_page()
df = pd.read_csv("Smart_Farming_Crop_Yield_2024.csv")

kriteria_alias = {
  "soil_pH": "pH Tanah",
  "soil_moisture_%": "Kelembapan Tanah (%)",
  "temperature_C": "Suhu (°C)",
  "rainfall_mm": "Curah Hujan (mm)",
  "sunlight_hours": "Jam Matahari (per Hari)"
}

nama_tanaman, kriteria_values, bobot = sidebar_konfigurasi(kriteria_alias)

if nama_tanaman:
  st.markdown("Metode yang digunakan: **Weighted Product (WP)**")
  with st.expander("ℹ️ Apa itu Metode Weighted Product (WP)?"):
    st.markdown("""
    Metode **Weighted Product** (WP) adalah teknik pengambilan keputusan multikriteria 
    yang menggunakan perkalian terberat dari tiap nilai alternatif terhadap bobot kriteria.
    Rumus utama:
    - Vektor S: `S = ∏(x_ij ^ wj)`
    - Vektor V: `V_i = S_i / ΣS`
    """)
  data_kriteria = df[list(kriteria_alias.keys())].copy()
  st.info("⏳ Sedang memproses data...")
  s, norm_bobot = weighted_product(data_kriteria, kriteria_values, bobot)
  tampilkan_hasil(df, kriteria_alias, nama_tanaman, s, norm_bobot)
else:
  st.warning("⚠️ **Waduh, kamu belum masukkan nama tanaman nih** 🌱")
  col1, col2, col3 = st.columns([3, 3, 2])
  with col2:
    st.image("crop.png", caption="Isi nama tanaman terlebih dahulu untuk melanjutkan", width=250)
