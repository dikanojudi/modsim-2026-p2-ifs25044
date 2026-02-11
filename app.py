import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from pathlib import Path

# Konfigurasi halaman Streamlit
st.set_page_config(
    page_title="Dashboard Kuesioner",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Fungsi untuk memuat dan memproses data
@st.cache_data
def load_and_process_data():
    try:
        # Cek keberadaan file
        data_path = Path("data_kuesioner.xlsx")
        if not data_path.exists():
            st.error("File 'data_kuesioner.xlsx' tidak ditemukan!")
            return None
        
        # Baca data Excel
        df = pd.read_excel(data_path)
        
        # Identifikasi kolom kuesioner (kolom yang memiliki nilai SS, S, CS, dll)
        valid_responses = ['SS', 'S', 'CS', 'CTS', 'TS', 'STS']
        question_cols = []
        
        for col in df.columns:
            # Cek apakah kolom berisi respons valid (minimal 50% nilai valid)
            valid_count = df[col].isin(valid_responses).sum()
            if valid_count > len(df) * 0.5:
                question_cols.append(col)
        
        if not question_cols:
            st.error("Tidak ada kolom kuesioner yang terdeteksi! Pastikan data memiliki kolom dengan respons: SS, S, CS, CTS, TS, STS")
            return None
        
        # Buat dataframe hanya untuk kolom kuesioner
        df_questions = df[question_cols].copy()
        
        # Mapping skor dan kategori
        score_mapping = {
            'SS': 6, 'S': 5, 'CS': 4, 'CTS': 3, 'TS': 2, 'STS': 1
        }
        
        category_mapping = {
            'SS': 'positif', 'S': 'positif', 
            'CS': 'netral', 
            'CTS': 'negatif', 'TS': 'negatif', 'STS': 'negatif'
        }
        
        # Buat dataframe skor dan kategori
        df_scores = df_questions.replace(score_mapping)
        df_categories = df_questions.replace(category_mapping)
        
        return df_questions, df_scores, df_categories, question_cols
    
    except Exception as e:
        st.error(f"Terjadi kesalahan saat memproses data: {str(e)}")
        return None

# Fungsi untuk membuat visualisasi
def create_visualizations(df_questions, df_scores, df_categories, question_cols):
    # Palet warna kustom
    color_scale = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
    category_colors = {'positif': '#2ecc71', 'netral': '#f39c12', 'negatif': '#e74c3c'}
    
    # ============================================
    # 1. BAR CHART - Distribusi Jawaban Keseluruhan
    # ============================================
    st.subheader("📊 Distribusi Jawaban Keseluruhan (Bar Chart)")
    
    # Gabungkan semua jawaban dan hitung frekuensi
    all_answers = df_questions.values.flatten()
    all_answers = all_answers[~pd.isnull(all_answers)]
    answer_counts = pd.Series(all_answers).value_counts().reindex(
        ['SS', 'S', 'CS', 'CTS', 'TS', 'STS'], fill_value=0
    )
    
    fig1 = px.bar(
        x=answer_counts.index,
        y=answer_counts.values,
        labels={'x': 'Jawaban', 'y': 'Jumlah Responden'},
        title='Distribusi Frekuensi Jawaban Keseluruhan',
        color=answer_counts.index,
        color_discrete_sequence=color_scale,
        text=answer_counts.values
    )
    fig1.update_traces(textposition='outside')
    fig1.update_layout(
        yaxis_title='Jumlah Responden',
        xaxis_title='Kategori Jawaban',
        uniformtext_minsize=8,
        uniformtext_mode='hide',
        plot_bgcolor='white',
        height=450
    )
    st.plotly_chart(fig1, use_container_width=True)
    
    # ============================================
    # 2. PIE CHART - Proporsi Jawaban Keseluruhan
    # ============================================
    st.subheader("🥧 Proporsi Jawaban Keseluruhan (Pie Chart)")
    
    fig2 = px.pie(
        values=answer_counts.values,
        names=answer_counts.index,
        title='Proporsi Jawaban Keseluruhan',
        color=answer_counts.index,
        color_discrete_sequence=color_scale,
        hole=0.4
    )
    fig2.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hoverinfo='label+value+percent'
    )
    fig2.update_layout(
        height=450,
        annotations=[dict(text='Jawaban', x=0.5, y=0.5, font_size=16, showarrow=False)]
    )
    st.plotly_chart(fig2, use_container_width=True)
    
    # ============================================
    # 3. STACKED BAR - Distribusi Jawaban per Pertanyaan
    # ============================================
    st.subheader("📦 Distribusi Jawaban per Pertanyaan (Stacked Bar)")
    
    # Siapkan data untuk stacked bar
    stacked_data = []
    for col in question_cols:
        counts = df_questions[col].value_counts().reindex(
            ['SS', 'S', 'CS', 'CTS', 'TS', 'STS'], fill_value=0
        )
        for ans, count in counts.items():
            stacked_data.append({
                'Pertanyaan': col,
                'Jawaban': ans,
                'Jumlah': count
            })
    
    df_stacked = pd.DataFrame(stacked_data)
    
    fig3 = px.bar(
        df_stacked,
        x='Pertanyaan',
        y='Jumlah',
        color='Jawaban',
        title='Distribusi Jawaban untuk Setiap Pertanyaan',
        labels={'Jumlah': 'Jumlah Responden', 'Pertanyaan': 'Pertanyaan'},
        color_discrete_sequence=color_scale,
        text='Jumlah'
    )
    fig3.update_layout(
        barmode='stack',
        xaxis_tickangle=-45,
        height=500,
        plot_bgcolor='white'
    )
    fig3.update_traces(textposition='inside')
    st.plotly_chart(fig3, use_container_width=True)
    
    # ============================================
    # 4. BAR CHART - Rata-rata Skor per Pertanyaan
    # ============================================
    st.subheader("⭐ Rata-rata Skor per Pertanyaan")
    
    avg_scores = df_scores.mean(numeric_only=True).sort_values(ascending=False)
    
    # Tentukan warna berdasarkan skor
    colors = []
    for score in avg_scores.values:
        if score >= 5.0:
            colors.append('#2ecc71')  # Hijau
        elif score >= 4.0:
            colors.append('#f39c12')  # Kuning
        else:
            colors.append('#e74c3c')  # Merah
    
    fig4 = px.bar(
        x=avg_scores.index,
        y=avg_scores.values,
        labels={'x': 'Pertanyaan', 'y': 'Rata-rata Skor'},
        title='Rata-rata Skor per Pertanyaan (Skala 1-6)',
        text=np.round(avg_scores.values, 2),
        color=avg_scores.index,
        color_discrete_sequence=colors
    )
    fig4.update_traces(textposition='outside')
    fig4.update_layout(
        yaxis_range=[1, 6],
        yaxis_title='Rata-rata Skor',
        xaxis_title='Pertanyaan',
        plot_bgcolor='white',
        height=450,
        showlegend=False
    )
    # Tambahkan garis referensi
    fig4.add_hline(y=4.0, line_dash="dash", line_color="orange", annotation_text="Batas Netral (4.0)")
    fig4.add_hline(y=5.0, line_dash="dash", line_color="green", annotation_text="Batas Sangat Baik (5.0)")
    st.plotly_chart(fig4, use_container_width=True)
    
    # ============================================
    # 5. BAR CHART - Distribusi Kategori Keseluruhan
    # ============================================
    st.subheader("📈 Distribusi Kategori Jawaban Keseluruhan")
    
    # Hitung kategori keseluruhan
    all_categories = df_categories.values.flatten()
    all_categories = all_categories[~pd.isnull(all_categories)]
    category_counts = pd.Series(all_categories).value_counts().reindex(
        ['positif', 'netral', 'negatif'], fill_value=0
    )
    
    fig5 = px.bar(
        x=category_counts.index,
        y=category_counts.values,
        labels={'x': 'Kategori', 'y': 'Jumlah Responden'},
        title='Distribusi Kategori Jawaban Keseluruhan',
        color=category_counts.index,
        color_discrete_sequence=[category_colors[cat] for cat in category_counts.index],
        text=category_counts.values
    )
    fig5.update_traces(textposition='outside')
    fig5.update_layout(
        yaxis_title='Jumlah Responden',
        xaxis_title='Kategori Jawaban',
        plot_bgcolor='white',
        height=450,
        showlegend=False
    )
    st.plotly_chart(fig5, use_container_width=True)
    
    # ============================================
    # BONUS 1: RADAR CHART - Profil Skor Pertanyaan
    # ============================================
    st.subheader("🎯 Bonus 1: Profil Skor Pertanyaan (Radar Chart)")
    
    # Siapkan data untuk radar chart
    radar_data = avg_scores.reset_index()
    radar_data.columns = ['Pertanyaan', 'Skor']
    
    fig_bonus1 = go.Figure()
    
    fig_bonus1.add_trace(go.Scatterpolar(
        r=radar_data['Skor'].tolist() + [radar_data['Skor'].iloc[0]],  # Close the loop
        theta=radar_data['Pertanyaan'].tolist() + [radar_data['Pertanyaan'].iloc[0]],
        fill='toself',
        name='Rata-rata Skor',
        line_color='#2ecc71'
    ))
    
    fig_bonus1.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[1, 6],
                tickmode='linear',
                tick0=1,
                dtick=1,
                showline=True,
                linewidth=2,
                gridcolor='lightgray'
            )
        ),
        title='Profil Skor Rata-rata per Pertanyaan',
        height=500,
        showlegend=False
    )
    st.plotly_chart(fig_bonus1, use_container_width=True)
    
    # ============================================
    # BONUS 2: HEATMAP - Korelasi Antar Pertanyaan
    # ============================================
    st.subheader("🔍 Bonus 2: Korelasi Antar Pertanyaan (Heatmap)")
    
    # Hitung korelasi antar pertanyaan
    corr_matrix = df_scores.corr()
    
    fig_bonus2 = px.imshow(
        corr_matrix,
        text_auto='.2f',
        color_continuous_scale='RdBu_r',
        aspect='auto',
        title='Matriks Korelasi Antar Pertanyaan'
    )
    fig_bonus2.update_layout(
        height=600,
        xaxis_title='Pertanyaan',
        yaxis_title='Pertanyaan'
    )
    st.plotly_chart(fig_bonus2, use_container_width=True)
    
    # ============================================
    # BONUS 3: BOX PLOT - Sebaran Skor per Pertanyaan
    # ============================================
    st.subheader("📦 Bonus 3: Sebaran Skor per Pertanyaan (Box Plot)")
    
    # Siapkan data untuk box plot
    df_melted = df_scores.melt(var_name='Pertanyaan', value_name='Skor')
    
    fig_bonus3 = px.box(
        df_melted,
        x='Pertanyaan',
        y='Skor',
        title='Distribusi Skor untuk Setiap Pertanyaan',
        color='Pertanyaan',
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    fig_bonus3.update_layout(
        yaxis_range=[0.5, 6.5],
        yaxis_title='Skor',
        xaxis_title='Pertanyaan',
        height=500,
        showlegend=False
    )
    st.plotly_chart(fig_bonus3, use_container_width=True)

# Main app
def main():
    st.title("📊 Dashboard Visualisasi Kuesioner")
    st.markdown("### Analisis Data Kuesioner dengan Streamlit dan Plotly")
    
    # Informasi sidebar
    with st.sidebar:
        st.header("ℹ️ Informasi")
        st.markdown("""
        **Skala Penilaian:**
        - SS (Sangat Setuju) = 6
        - S (Setuju) = 5
        - CS (Cukup Setuju) = 4
        - CTS (Cenderung Tidak Setuju) = 3
        - TS (Tidak Setuju) = 2
        - STS (Sangat Tidak Setuju) = 1
        
        **Kategori:**
        - ✅ Positif: SS, S
        - ⚪ Netral: CS
        - ❌ Negatif: CTS, TS, STS
        """)
        
        st.header("🛠️ Panduan Penggunaan")
        st.markdown("""
        1. Pastikan file `data_kuesioner.xlsx` berada di direktori yang sama
        2. Dashboard akan otomatis memuat dan memproses data
        3. Gunakan kontrol di sidebar untuk navigasi
        4. Hover pada chart untuk melihat detail
        5. Gunakan tombol di pojok kanan chart untuk download atau fullscreen
        """)
        
        st.header("💡 Insight")
        st.markdown("""
        - Pertanyaan dengan skor rata-rata < 4.0 perlu perhatian khusus
        - Proporsi jawaban negatif > 30% mengindikasikan area perbaikan
        - Korelasi tinggi antar pertanyaan menunjukkan pola respons yang konsisten
        """)
    
    # Muat dan proses data
    data_result = load_and_process_data()
    
    if data_result is None:
        st.warning("Silakan perbaiki file data dan refresh halaman")
        return
    
    df_questions, df_scores, df_categories, question_cols = data_result
    
    # Tampilkan ringkasan data
    st.markdown("### 📋 Ringkasan Data")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Jumlah Responden", len(df_questions))
    col2.metric("Jumlah Pertanyaan", len(question_cols))
    col3.metric("Total Respons", df_questions.notna().sum().sum())
    col4.metric("Rata-rata Skor Keseluruhan", f"{df_scores.mean().mean():.2f}")
    
    # Tampilkan visualisasi
    create_visualizations(df_questions, df_scores, df_categories, question_cols)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray; padding: 10px;'>
        Dashboard Kuesioner • Dibuat dengan Streamlit dan Plotly • © 2026
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
