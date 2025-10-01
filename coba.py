import streamlit as st
import pandas as pd

# --- KONFIGURASI HALAMAN ---
# Mengatur layout halaman menjadi lebar, memberikan judul, dan ikon pada tab browser
st.set_page_config(
    layout="wide",
    page_title="Dashboard Analisis Data",
    page_icon="📊"
)

# --- JUDUL UTAMA DASHBOARD ---
st.title('📊 Dashboard Analisis Data Data')
st.write('Aplikasi interaktif untuk analisis cepat data hasil Survei Potensi Desa.')

# --- SIDEBAR UNTUK KONTROL ---
# Semua widget untuk input dan filter diletakkan di sidebar
with st.sidebar:
    st.header("📤 Unggah & Filter Data")
    
    # Langkah 1: Upload File
    uploaded_file = st.file_uploader(
        "Pilih file Excel atau CSV",
        type=['xlsx', 'csv'],
        help="Pastikan file Anda memiliki kolom 'nama_kec' dan 'nama_desa'."
    )

# Cek jika file belum diupload, tampilkan pesan di halaman utama
if uploaded_file is None:
    st.info("Silakan unggah file dataset Data Anda di sidebar untuk memulai analisis.")
    st.stop() # Menghentikan eksekusi script jika tidak ada file

# --- PROSES DATA SETELAH FILE DIUPLOAD ---
try:
    with st.spinner('⏳ Memproses data Anda...'):
        # Baca file sesuai formatnya
        df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file, low_memory=False)

        # Validasi kolom wajib
        if 'nama_kec' not in df.columns or 'nama_desa' not in df.columns:
            st.error("⚠️ Error: Pastikan dataset Anda memiliki kolom 'nama_kec' dan 'nama_desa'.")
            st.stop()

        # Pembersihan data
        original_row_count = len(df)
        df.dropna(subset=['nama_kec', 'nama_desa'], inplace=True)
        rows_dropped = original_row_count - len(df)
        
        # Konversi tipe data numerik
        for col in df.columns:
            if col not in ['nama_kec', 'nama_desa']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
    
    st.success('✅ Data berhasil diproses!')
    if rows_dropped > 0:
        st.warning(f"⚠️ Notifikasi: {rows_dropped} baris dihapus karena data 'nama_kec' atau 'nama_desa' kosong.")

    # --- KONTROL FILTER LANJUTAN DI SIDEBAR ---
    with st.sidebar:
        # Filter Kecamatan
        list_kecamatan = sorted(df['nama_kec'].unique().tolist())
        list_kecamatan.insert(0, "Semua Kecamatan")
        selected_kecamatan = st.selectbox('Pilih Kecamatan:', list_kecamatan)

        # Filter Kolom/Variabel
        all_columns = [col for col in df.columns if col not in ['nama_kec', 'nama_desa']]
        selected_columns = st.multiselect('Pilih variabel yang ingin dianalisis:', all_columns)

    # --- HALAMAN UTAMA: TAMPILAN HASIL ANALISIS ---

    # Filter dataframe utama berdasarkan pilihan di sidebar
    if selected_kecamatan == "Semua Kecamatan":
        filtered_df = df.copy()
    else:
        filtered_df = df[df['nama_kec'] == selected_kecamatan]

    # Menampilkan metrik/KPI
    st.header(f"📈 Ringkasan Data: {selected_kecamatan}")
    col1, col2, col3 = st.columns(3)
    col1.metric("Jumlah Baris Data", f"{len(filtered_df):,}")
    col2.metric("Jumlah Desa/Kelurahan", f"{filtered_df['nama_desa'].nunique():,}")
    col3.metric("Jumlah Variabel Dipilih", f"{len(selected_columns):,}")
    
    st.write("---")

    # Tampilkan hasil hanya jika user sudah memilih variabel
    if not selected_columns:
        st.info("Silakan pilih satu atau lebih variabel di sidebar untuk melihat data dan visualisasi.")
    else:
        # Tampilkan Tabel Data di dalam Expander
        with st.expander("📂 Lihat Detail Tabel Data"):
            display_columns = ['nama_kec', 'nama_desa'] + selected_columns
            st.dataframe(filtered_df[display_columns])

        # Tampilkan Visualisasi Data
        st.header("🎨 Visualisasi Data")
        
        numeric_cols_selected = [col for col in selected_columns if pd.api.types.is_numeric_dtype(filtered_df[col])]

        if not numeric_cols_selected:
            st.warning("Pilih setidaknya satu variabel numerik (angka) untuk membuat visualisasi.")
        else:
            viz_col1, viz_col2 = st.columns(2)
            with viz_col1:
                y_axis = st.selectbox('Pilih variabel untuk sumbu Y:', numeric_cols_selected)
            with viz_col2:
                chart_type = st.selectbox("Pilih Tipe Visualisasi:", ["Bar Chart", "Line Chart", "Area Chart"])
            
            if y_axis:
                chart_data = filtered_df.set_index('nama_desa')
                st.write(f"Menampilkan **{chart_type}** untuk variabel **'{y_axis}'**.")
                
                if chart_type == "Bar Chart":
                    st.bar_chart(chart_data, y=y_axis)
                elif chart_type == "Line Chart":
                    st.line_chart(chart_data, y=y_axis)
                elif chart_type == "Area Chart":
                    st.area_chart(chart_data, y=y_axis)

except Exception as e:
    st.error(f"Terjadi kesalahan: {e}")
