import streamlit as st
import pandas as pd
import altair as alt

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    layout="wide",
    page_title="Dashboard Analisis Data",
    page_icon="📊"
)

# --- JUDUL UTAMA DASHBOARD ---
st.title('📊 Sistem Visualisasi Dinamis')
st.write('Visualisasi dan Tabel interaktif untuk data hasil Survei Potensi Desa.')

# --- SIDEBAR UNTUK KONTROL ---
with st.sidebar:
    st.header("📤 Unggah & Filter Data")
    uploaded_file = st.file_uploader(
        "Pilih file Excel atau CSV",
        type=['xlsx', 'csv'],
        help="Pastikan file Anda memiliki kolom 'nama_kec' dan 'nama_desa'."
    )

# Jika file belum diupload
if uploaded_file is None:
    st.info("Silakan unggah file dataset Data Anda di sidebar untuk memulai analisis.")
    st.stop()

# --- PROSES DATA SETELAH FILE DIUPLOAD ---
try:
    with st.spinner('⏳ Memproses data Anda...'):
        df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file, low_memory=False)

        # Validasi kolom wajib
        if 'nama_kec' not in df.columns or 'nama_desa' not in df.columns:
            st.error("⚠️ Error: Pastikan dataset Anda memiliki kolom 'nama_kec' dan 'nama_desa'.")
            st.stop()

        # Pembersihan data
        original_row_count = len(df)
        df.dropna(subset=['nama_kec', 'nama_desa'], inplace=True)
        rows_dropped = original_row_count - len(df)

        # Konversi ke numerik
        for col in df.columns:
            if col not in ['nama_kec', 'nama_desa']:
                df[col] = pd.to_numeric(df[col], errors='coerce')

    st.success('✅ Data berhasil diproses!')
    if rows_dropped > 0:
        st.warning(f"⚠️ {rows_dropped} baris dihapus karena data 'nama_kec' atau 'nama_desa' kosong.")

    # --- FILTER DATA ---
    with st.sidebar:
        list_kecamatan = sorted(df['nama_kec'].unique().tolist())
        list_kecamatan.insert(0, "Semua Kecamatan")
        selected_kecamatan = st.selectbox('Pilih Kecamatan:', list_kecamatan)

        all_columns = [col for col in df.columns if col not in ['nama_kec', 'nama_desa']]
        selected_columns = st.multiselect('Pilih variabel yang ingin dianalisis:', all_columns)

    if selected_kecamatan == "Semua Kecamatan":
        filtered_df = df.copy()
    else:
        filtered_df = df[df['nama_kec'] == selected_kecamatan]

    # --- RINGKASAN DATA ---
    st.header(f"📈 Ringkasan Data: {selected_kecamatan}")
    col1, col2, col3 = st.columns(3)
    col1.metric("Jumlah Baris Data", f"{len(filtered_df):,}")
    col2.metric("Jumlah Desa/Kelurahan", f"{filtered_df['nama_desa'].nunique():,}")
    col3.metric("Jumlah Variabel Dipilih", f"{len(selected_columns):,}")
    
    st.write("---")

    # --- TABEL DATA & VISUALISASI ---
    if not selected_columns:
        st.info("Silakan pilih variabel di sidebar untuk melihat data dan visualisasi.")
    else:
        with st.expander("📂 Lihat Detail Tabel Data"):
            display_columns = ['nama_kec', 'nama_desa'] + selected_columns
            st.dataframe(filtered_df[display_columns])

        st.header("🎨 Visualisasi Data")

        numeric_cols_selected = [col for col in selected_columns if pd.api.types.is_numeric_dtype(filtered_df[col])]

        if not numeric_cols_selected:
            st.warning("Pilih setidaknya satu variabel numerik untuk membuat visualisasi.")
        else:
            viz_col1, viz_col2, viz_col3 = st.columns(3)
            with viz_col1:
                y_axis = st.selectbox('Pilih variabel untuk sumbu Y:', numeric_cols_selected)
            with viz_col2:
                chart_type = st.selectbox("Pilih Tipe Visualisasi:", ["Bar Chart", "Line Chart", "Area Chart"])
            with viz_col3:
                if chart_type == "Bar Chart":
                    orientation = st.radio("Orientasi:", ["Vertikal", "Horizontal"], horizontal=True)

            if chart_type == "Bar Chart":
                sort_order = st.radio("Urutkan berdasarkan nilai:", ["Ascending", "Descending"], horizontal=True)

            if y_axis:
                chart_data = filtered_df[['nama_desa', y_axis]].copy()
                st.write(f"Menampilkan **{chart_type}** untuk variabel **'{y_axis}'**.")

                if chart_type == "Bar Chart":
                    sort_mode = "ascending" if sort_order == "Ascending" else "descending"

                    if orientation == "Vertikal":
                        chart = alt.Chart(chart_data).mark_bar().encode(
                            x=alt.X('nama_desa:N', sort=alt.SortField(field=y_axis, order=sort_mode)),
                            y=alt.Y(f'{y_axis}:Q'),
                            tooltip=['nama_desa', y_axis]
                        )
                        text = chart.mark_text(
                            align='center',
                            baseline='bottom',
                            dy=-5
                        ).encode(
                            text=f'{y_axis}:Q'
                        )
                        st.altair_chart(chart + text, use_container_width=True)

                    else:  # Horizontal
                        chart = alt.Chart(chart_data).mark_bar().encode(
                            y=alt.Y('nama_desa:N', sort=alt.SortField(field=y_axis, order=sort_mode)),
                            x=alt.X(f'{y_axis}:Q'),
                            tooltip=['nama_desa', y_axis]
                        )
                        text = chart.mark_text(
                            align='left',
                            baseline='middle',
                            dx=3
                        ).encode(
                            text=f'{y_axis}:Q'
                        )
                        st.altair_chart(chart + text, use_container_width=True)

                elif chart_type == "Line Chart":
                    st.line_chart(chart_data.set_index('nama_desa')[y_axis])

                elif chart_type == "Area Chart":
                    st.area_chart(chart_data.set_index('nama_desa')[y_axis])

except Exception as e:
    st.error(f"Terjadi kesalahan: {e}")
