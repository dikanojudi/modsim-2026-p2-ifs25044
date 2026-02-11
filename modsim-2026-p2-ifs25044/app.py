import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Dashboard Kuesioner", layout="wide")

st.title("📊 Dashboard Visualisasi Data Kuesioner")

# ==============================
# LOAD DATA
# ==============================
df = pd.read_excel("data_kuesioner.xlsx")

questions = [col for col in df.columns if col.startswith("Q")]

# ==============================
# KONFIGURASI SKOR & KATEGORI
# ==============================
score_map = {
    "SS": 6,
    "S": 5,
    "CS": 4,
    "CTS": 3,
    "TS": 2,
    "STS": 1
}

category_map = {
    "SS": "Positif",
    "S": "Positif",
    "CS": "Netral",
    "CTS": "Negatif",
    "TS": "Negatif",
    "STS": "Negatif"
}

# Ubah ke format long
df_long = df.melt(value_vars=questions, var_name="Pertanyaan", value_name="Jawaban")

# Tambahkan skor dan kategori
df_long["Skor"] = df_long["Jawaban"].map(score_map)
df_long["Kategori"] = df_long["Jawaban"].map(category_map)

# ==============================
# 1️⃣ BAR CHART DISTRIBUSI JAWABAN
# ==============================
st.subheader("1. Distribusi Jawaban Keseluruhan")

dist_jawaban = df_long["Jawaban"].value_counts().reset_index()
dist_jawaban.columns = ["Jawaban", "Jumlah"]

fig1 = px.bar(dist_jawaban, x="Jawaban", y="Jumlah",
              title="Distribusi Jawaban Kuesioner",
              color="Jawaban")
st.plotly_chart(fig1, use_container_width=True)

# ==============================
# 2️⃣ PIE CHART PROPORSI JAWABAN
# ==============================
st.subheader("2. Proporsi Jawaban Keseluruhan")

fig2 = px.pie(dist_jawaban,
              names="Jawaban",
              values="Jumlah",
              title="Proporsi Jawaban")
st.plotly_chart(fig2, use_container_width=True)

# ==============================
# 3️⃣ STACKED BAR PER PERTANYAAN
# ==============================
st.subheader("3. Distribusi Jawaban per Pertanyaan")

dist_per_q = df_long.groupby(["Pertanyaan", "Jawaban"]).size().reset_index(name="Jumlah")

fig3 = px.bar(dist_per_q,
              x="Pertanyaan",
              y="Jumlah",
              color="Jawaban",
              title="Distribusi Jawaban per Pertanyaan",
              barmode="stack")

st.plotly_chart(fig3, use_container_width=True)

# ==============================
# 4️⃣ RATA-RATA SKOR PER PERTANYAAN
# ==============================
st.subheader("4. Rata-rata Skor per Pertanyaan")

avg_score = df_long.groupby("Pertanyaan")["Skor"].mean().reset_index()

fig4 = px.bar(avg_score,
              x="Pertanyaan",
              y="Skor",
              title="Rata-rata Skor per Pertanyaan",
              color="Skor")

st.plotly_chart(fig4, use_container_width=True)

# ==============================
# 5️⃣ DISTRIBUSI KATEGORI
# ==============================
st.subheader("5. Distribusi Kategori Jawaban")

kategori_dist = df_long["Kategori"].value_counts().reset_index()
kategori_dist.columns = ["Kategori", "Jumlah"]

fig5 = px.bar(kategori_dist,
              x="Kategori",
              y="Jumlah",
              color="Kategori",
              title="Distribusi Kategori Jawaban")

st.plotly_chart(fig5, use_container_width=True)

# ==============================
# 🎁 BONUS: HEATMAP RATA-RATA SKOR
# ==============================
st.subheader("Bonus: Heatmap Rata-rata Skor")

heatmap_data = df_long.groupby(["Pertanyaan", "Jawaban"]).size().reset_index(name="Jumlah")

fig6 = px.density_heatmap(heatmap_data,
                          x="Pertanyaan",
                          y="Jawaban",
                          z="Jumlah",
                          title="Heatmap Distribusi Jawaban")

st.plotly_chart(fig6, use_container_width=True)
