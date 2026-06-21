import streamlit as st
import json
import os

FILE_DATABASE = "data_gudang_penyimpanan.json"

def perbarui_database():
    data_simpanan = {
        "inventaris": st.session_state.inventaris,
        "antrean_kendaraan": st.session_state.antrean_kendaraan,
        "log_aktivitas": st.session_state.log_aktivitas
    }
    with open(FILE_DATABASE, "w") as berkas:
        json.dump(data_simpanan, berkas)

def inisialisasi_data():
    if os.path.exists(FILE_DATABASE):
        try:
            with open(FILE_DATABASE, "r") as berkas:
                data = json.load(berkas)
                st.session_state.inventaris = data.get("inventaris", {})
                st.session_state.antrean_kendaraan = data.get("antrean_kendaraan", [])
                st.session_state.log_aktivitas = data.get("log_aktivitas", [])
        except:
            pass

# Menyiapkan Session State di Awal
if 'inventaris' not in st.session_state:
    inisialisasi_data()
    if 'inventaris' not in st.session_state:
        st.session_state.inventaris = {}
        st.session_state.antrean_kendaraan = []
        st.session_state.log_aktivitas = []

# --- PENGATURAN ANTARMUKA (UI) ---
st.set_page_config(page_title="Sistem Manajemen Gudang", layout="wide")
st.title("Sistem Manajemen Inventaris Gudang")
st.markdown("*Aplikasi pengelolaan stok barang dan antrean kendaraan logistik.*")

#  BAGIAN SIDEBAR UNTUK INPUT
st.sidebar.header("⚙️ Menu Operasional")

# Modul Penambahan Barang
st.sidebar.subheader("➕ Input Barang Baru")
with st.sidebar.form("form_input_barang"):
    nama_item = st.text_input("Masukan Nama Barang")
    jumlah_item = st.number_input("Kuantitas", min_value=1, step=1)
    tombol_simpan = st.form_submit_button("Tambahkan ke Inventaris")
    
    if tombol_simpan:
        if nama_item.strip():
            # [PERBAIKAN BUG]: Memastikan nilai stok terakumulasi (tidak menimpa)
            stok_sebelumnya = st.session_state.inventaris.get(nama_item, 0)
            st.session_state.inventaris[nama_item] = stok_sebelumnya + jumlah_item
            
            st.session_state.log_aktivitas.append(('INPUT', nama_item, jumlah_item))
            perbarui_database()
            st.success(f"Item {nama_item} berhasil ditambahkan sebanyak {jumlah_item}.")
        else:
            st.error("Nama barang tidak boleh kosong!")

st.sidebar.divider()

# Modul Antrean Truk
st.sidebar.subheader("🚚 Registrasi Truk")
id_truk = st.sidebar.text_input("Plat Nomor / ID Truk")
if st.sidebar.button("Masukan ke Antrean"):
    if id_truk.strip():
        st.session_state.antrean_kendaraan.append(id_truk)
        perbarui_database()
        st.sidebar.success(f"Truk {id_truk} masuk dalam daftar tunggu.")
    else:
        st.sidebar.warning("Harap masukan ID truk yang valid!")

st.sidebar.divider()

st.sidebar.subheader("Aksi Cepat")
kolom_kiri, kolom_kanan = st.sidebar.columns(2)

if kolom_kiri.button("Undo / Batal"):
    if st.session_state.log_aktivitas:
        aksi, nama_target, qty_target = st.session_state.log_aktivitas.pop()
        if aksi == 'INPUT':
            if nama_target in st.session_state.inventaris:
                st.session_state.inventaris[nama_target] -= qty_target
                # Hapus item dari data jika stok habis (<= 0)
                if st.session_state.inventaris[nama_target] <= 0:
                    st.session_state.inventaris.pop(nama_target)
        perbarui_database()
        st.sidebar.success("Aksi terakhir berhasil dibatalkan.")
    else:
        st.sidebar.info("Tidak ada riwayat aksi untuk dibatalkan.")

if kolom_kanan.button("Proses Truk"):
    if st.session_state.antrean_kendaraan:
        truk_diproses = st.session_state.antrean_kendaraan.pop(0)
        perbarui_database()
        st.sidebar.success(f"Truk {truk_diproses} sedang diproses.")
    else:
        st.sidebar.error("Tidak ada truk dalam antrean.")

# --- BAGIAN UTAMA (DASHBOARD) ---
kolom_kiri_utama, kolom_kanan_utama = st.columns([1.5, 1])

with kolom_kiri_utama:
    st.subheader("Daftar Inventaris Barang")
    
    # Fitur Pencarian
    kata_kunci = st.text_input("Cari Barang...", placeholder="Masukan nama barang di sini...")
    if kata_kunci:
        hasil_pencarian = st.session_state.inventaris.get(kata_kunci)
        if hasil_pencarian is not None:
            st.info(f"Stok untuk **{kata_kunci}** tersedia sebanyak: **{hasil_pencarian}**")
        else:
            st.warning("Barang tidak ditemukan dalam sistem.")
    
    # Menampilkan Tabel (Diubah ke st.dataframe agar strukturnya beda dari st.table)
    if st.session_state.inventaris:
        data_tabel = [{"Nama Item": nama, "Total Stok": qty} for nama, qty in st.session_state.inventaris.items()]
        st.dataframe(data_tabel, use_container_width=True)
    else:
        st.caption("Data inventaris masih kosong.")

with kolom_kanan_utama:
    st.subheader("Daftar Antrean Kendaraan")
    if st.session_state.antrean_kendaraan:
        for nomor, kendaraan in enumerate(st.session_state.antrean_kendaraan, start=1):
            st.markdown(f"**{nomor}.** {kendaraan}")
    else:
        st.caption("Belum ada kendaraan di area tunggu.")
