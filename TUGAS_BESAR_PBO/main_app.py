import streamlit as st
import datetime
import pandas as pd
import time
from model import Pembelian, Keranjang, Nota
import database

# ===== USER LOGIN (super simple, satu admin saja) =====
if 'login' not in st.session_state:
    st.session_state['login'] = False
if not st.session_state['login']:
    st.title("Login Admin")
    user = st.text_input("Username", max_chars=20)
    pw = st.text_input("Password", type="password")
    if st.button("Login"):
        if user.strip() == "admin" and pw == "admin123":
            st.session_state['login'] = True
            st.rerun()
        else:
            st.error("Username atau password salah!")
    st.stop()

st.set_page_config(page_title="Minimarket POS", page_icon="🛒", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Poppins', 'Segoe UI', Arial, sans-serif !important;
    }
    .stApp {
        background: linear-gradient(135deg, #a86b3c 0%, #6c4320 100%) !important;
    }
    h1, h2, h3, h4, h5 {
        color: #fff !important;
        font-family: 'Poppins', 'Segoe UI', Arial, sans-serif !important;
        letter-spacing: 1px;
    }
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #bc6c25, #a86b3c 90%);
        color: #fff;
        border: none;
        border-radius: 14px;
        font-size: 1.15rem;
        font-weight: bold;
        padding: 0.5em 2em;
        margin-top: 1em;
        margin-bottom: 2em;
        box-shadow: 0 4px 14px #bc6c2533;
        transition: 0.3s;
    }
    div.stButton > button:first-child:hover {
        filter: brightness(1.2);
        border: 2px solid #fff;
    }
    section[data-testid="stSidebar"] {
        background: linear-gradient(150deg, #474747 70%, #232323 100%) !important;
        border-radius: 0 36px 36px 0;
        color: #fff;
        box-shadow: 0 8px 32px #0008;
    }
    .stApp > header, .stApp > main {
        background: none !important;
    }
    .css-1v0mbdj, .e1y5xkzn3 {background-color: #cfb48c !important;}
    [data-testid="stSpinner"] > div > div {
        color: #bc6c25 !important;
    }
    .stAlert {
        border-radius:12px;
        box-shadow: 0 4px 24px #bc6c2514;
    }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/shopping-cart-loaded.png", width=70)
    st.markdown("<h2 style='color:#fff;margin-top:-10px;margin-bottom:20px;'>Menu Navigasi</h2>", unsafe_allow_html=True)
    menu = st.radio(
        "Pilih Menu:",
        ["🛒 Input Pembelian", "📑 Riwayat Pembelian", "📊 Rekap Pembelian"]
    )
    if st.button("Logout"):
        st.session_state['login'] = False
        st.rerun()
    st.markdown("---")
    st.info("Aplikasi sederhana kasir minimarket.\n\nBy [Gadhang]", icon="🛒")

def format_rp(angka):
    try:
        import locale
        locale.setlocale(locale.LC_ALL, 'id_ID.UTF-8')
        return locale.currency(angka or 0, grouping=True, symbol='Rp ')[:-3]
    except:
        return f"Rp {angka or 0:,.0f}".replace(",", ".")

def struk_html_func(struk_items):
    total_harga = struk_items.apply(
        lambda row: row['harga'] * row['jumlah'] if (row['jenis'] == "Barang" and row['jumlah'] is not None) else row['harga'], axis=1
    ).sum()
    baris_item = ""
    for i, row in struk_items.iterrows():
        baris_item += (
            f"<tr><td>{row['nama']}</td><td align='center'>{row['jumlah'] if row['jumlah'] is not None else '-'}</td>"
            f"<td align='right'>{format_rp(row['harga'])}</td>"
            f"<td align='right'>{format_rp(row['harga'] * row['jumlah']) if (row['jenis'] == 'Barang' and row['jumlah'] is not None) else format_rp(row['harga'])}</td></tr>"
        )
    struk_html = f"""
    <div id="strukku" style='width:370px; background:white; color:#222; padding:16px 12px 8px 12px; font-family:Consolas,monospace; border:1px solid #ddd; border-radius:7px;'>
    <div style="font-weight:bold; font-size:20px; text-align:center; color:#e62b1e; letter-spacing:2px;">MINIMARKETKU</div>
    <div style="font-size:10px; text-align:center; color:#7d4f21;">Jl. Pandanaran No. 99, Kel. Pekunden, Kec. Semarang Tengah, Kota Semarang, Jawa Tengah 50134</div>
    <div style="font-size:11px; text-align:center; color:#111; margin-bottom:7px;">NPWP: 12.345.678.9-012.000</div>
    <div style="border-top:dashed 1px #aaa; margin:4px 0 7px 0;"></div>
    <div style="font-size:13px;">
        Tanggal  : {struk_items.iloc[0]['tanggal']}<br>
        Kasir    : Admin<br>
        ID Nota  : {struk_items.iloc[0]['id_nota']}
    </div>
    <div style="border-top:dashed 1px #aaa; margin:7px 0;"></div>
    <table style="width:100%;font-size:13px;margin-bottom:7px;">
    <tr><th align='left'>Nama</th><th>Qty</th><th>Harga</th><th>Total</th></tr>
    {baris_item}
    </table>
    <div style="border-top:dashed 1px #aaa; margin:7px 0;"></div>
    <div style="font-size:15px; font-weight:bold; text-align:right;">
        Total: {format_rp(total_harga)}
    </div>
    <div style="border-top:dashed 1px #aaa; margin:7px 0 6px 0;"></div>
    <div style="font-size:11px; text-align:center; letter-spacing:1px;">
        *** TERIMA KASIH ***
        <br>Barang/jasa yang sudah dibeli
        <br>tidak dapat dikembalikan.
    </div>
    <div style="font-size:10px; text-align:center; margin-top:5px; color:#999;">
        (Print via browser: CTRL+P)
    </div>
    </div>
    """
    return struk_html

def input_pembelian():
    if 'keranjang_obj' not in st.session_state:
        st.session_state['keranjang_obj'] = Keranjang()
    if 'multi_pembelian' not in st.session_state:
        st.session_state['multi_pembelian'] = False

    st.markdown("""
        <div style="background:rgba(255,255,255,0.93);padding:1.3em 2em 1.3em 2em;border-radius:28px; margin-bottom:1em; margin-top:0; text-align:center; font-size:1.8em; font-weight:bold; color:#7d4f21; text-transform: uppercase;">
            Selamat Datang di Minimarketku
        </div>
    """, unsafe_allow_html=True)
    with st.container():
        st.header("Tambah Pembelian Baru")
        st.markdown("**Silakan masukkan data pembelian barang atau jasa di bawah ini.**")
        st.session_state['multi_pembelian'] = st.checkbox(
            "Pembelian dalam 1 ID/struk (multi barang/jasa)",
            value=st.session_state.get('multi_pembelian', False)
        )
        multi_mode = st.session_state['multi_pembelian']

        jenis = st.selectbox("Jenis", ["Barang", "Jasa"])
        if jenis == "Barang":
            col1, col2 = st.columns([2, 1])
            with col1:
                nama = st.text_input("Nama Barang", key="nama_barang", placeholder="Contoh: Oreo, Mizone, Spidol, dll")
            with col2:
                jumlah = st.number_input("Jumlah", min_value=1, step=1, format="%d", key="jumlah_barang")
            harga_str = st.text_input("Harga per Barang (Rp)", value="", placeholder="Masukkan harga...", key="harga_barang")
            try:
                harga = float(harga_str.replace(".", "").replace(",", "")) if harga_str else 0.0
            except:
                harga = -1
            tanggal = st.date_input("Tanggal", value=datetime.date.today(), key="tanggal_barang")
            if multi_mode:
                if st.button("Tambah ke Keranjang", key="tambah_keranjang_barang"):
                    if not nama.strip():
                        st.warning("Nama barang wajib diisi.")
                    elif harga_str.strip() == "":
                        st.warning("Harga harus diisi.")
                    elif harga <= 0:
                        st.warning("Harga harus lebih dari 0 dan berupa angka.")
                    else:
                        pembelian = Pembelian(jenis, nama, harga, jumlah, "", tanggal)
                        st.session_state['keranjang_obj'].tambah_item(pembelian)
                        st.success(f"{nama} ditambahkan ke keranjang.")
            else:
                if st.button("Simpan", key="simpan_barang"):
                    if not nama.strip():
                        st.warning("Nama barang wajib diisi.")
                    elif harga_str.strip() == "":
                        st.warning("Harga harus diisi.")
                    elif harga <= 0:
                        st.warning("Harga harus lebih dari 0 dan berupa angka.")
                    else:
                        id_nota = int(time.time()*1000)
                        with st.spinner("Menyimpan data..."):
                            database.execute_query(
                                "INSERT INTO pembelian (jenis, nama, harga, jumlah, tanggal, id_nota) VALUES (?, ?, ?, ?, ?, ?)",
                                (jenis, nama, harga, jumlah, tanggal.strftime("%Y-%m-%d"), id_nota)
                            )
                        st.success("Pembelian barang berhasil disimpan.")
                        struk_items = database.get_dataframe("SELECT * FROM pembelian WHERE id_nota = ?", (id_nota,))
                        st.markdown("### Struk Otomatis")
                        st.markdown(struk_html_func(struk_items), unsafe_allow_html=True)
                        st.markdown("""
                        <script>
                        function printDivStruk() {
                            var divContents = document.getElementById("strukku").innerHTML;
                            var a = window.open('', '', 'height=500, width=350');
                            a.document.write('<html><head><title>Print Struk</title></head>');
                            a.document.write('<body style="background:white;">');
                            a.document.write(divContents);
                            a.document.write('</body></html>');
                            a.document.close();
                            a.print();
                        }
                        </script>
                        <button onclick="printDivStruk()" style="margin-top:10px;background:#bc6c25;color:#fff;border:none;padding:10px 22px;border-radius:5px;font-size:15px;cursor:pointer;">🖨️ Print Struk</button>
                        """, unsafe_allow_html=True)

        else:
            NAMA_JASA_LIST = [
                "Pulsa", "Kuota Internet", "Top Up Game", "Top Up E-Wallet",
                "Bayar Listrik", "Token PLN", "Bayar PDAM"
            ]
            nama_jasa = st.selectbox("Nama Jasa", NAMA_JASA_LIST, key="nama_jasa")
            detail_jasa = ""
            if nama_jasa == "Top Up Game":
                game_list = [
                    "PUBG Mobile", "Mobile Legend", "Free Fire", "Valorant",
                    "Genshin Impact", "Honor of Kings", "LOL Wild Rift", "DOTA 2"
                ]
                game_selected = st.selectbox("Pilih Game", game_list, key="game_jasa")
                detail_jasa = game_selected
            elif nama_jasa == "Top Up E-Wallet":
                ewallet_list = ["DANA", "ShopeePay", "OVO", "GoPay"]
                ewallet_selected = st.selectbox("Pilih E-Wallet", ewallet_list, key="ewallet_jasa")
                detail_jasa = ewallet_selected

            nomor_tujuan = st.text_input("Nomor Tujuan (No HP/ID/No Meter)", placeholder="Opsional, sesuai kebutuhan", key="nomor_jasa")
            harga_jasa_str = st.text_input("Harga (Rp)", value="", placeholder="Masukkan harga jasa...", key="harga_jasa")
            try:
                harga_jasa = float(harga_jasa_str.replace(".", "").replace(",", "")) if harga_jasa_str else 0.0
            except:
                harga_jasa = -1
            tanggal = st.date_input("Tanggal", value=datetime.date.today(), key="tanggal_jasa")
            if multi_mode:
                if st.button("Tambah ke Keranjang", key="tambah_keranjang_jasa"):
                    if not nama_jasa.strip():
                        st.warning("Nama jasa wajib dipilih.")
                    elif nama_jasa == "Top Up Game" and not detail_jasa:
                        st.warning("Pilih nama game yang ingin di-top up.")
                    elif nama_jasa == "Top Up E-Wallet" and not detail_jasa:
                        st.warning("Pilih e-wallet yang ingin di-top up.")
                    elif harga_jasa_str.strip() == "":
                        st.warning("Harga harus diisi.")
                    elif harga_jasa <= 0:
                        st.warning("Harga harus lebih dari 0 dan berupa angka.")
                    else:
                        nama_db = nama_jasa
                        if detail_jasa:
                            nama_db += f" - {detail_jasa}"
                        pembelian = Pembelian("Jasa", nama_db, harga_jasa, 1, nomor_tujuan, tanggal)
                        st.session_state['keranjang_obj'].tambah_item(pembelian)
                        st.success(f"{nama_db} ditambahkan ke keranjang.")
            else:
                if st.button("Simpan", key="simpan_jasa"):
                    if not nama_jasa.strip():
                        st.warning("Nama jasa wajib dipilih.")
                    elif nama_jasa == "Top Up Game" and not detail_jasa:
                        st.warning("Pilih nama game yang ingin di-top up.")
                    elif nama_jasa == "Top Up E-Wallet" and not detail_jasa:
                        st.warning("Pilih e-wallet yang ingin di-top up.")
                    elif harga_jasa_str.strip() == "":
                        st.warning("Harga harus diisi.")
                    elif harga_jasa <= 0:
                        st.warning("Harga harus lebih dari 0 dan berupa angka.")
                    else:
                        nama_db = nama_jasa
                        if detail_jasa:
                            nama_db += f" - {detail_jasa}"
                        id_nota = int(time.time()*1000)
                        with st.spinner("Menyimpan data..."):
                            database.execute_query(
                                "INSERT INTO pembelian (jenis, nama, harga, jumlah, nomor_tujuan, tanggal, id_nota) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                ("Jasa", nama_db, harga_jasa, 1, nomor_tujuan, tanggal.strftime("%Y-%m-%d"), id_nota)
                            )
                        st.success("Pembelian jasa berhasil disimpan.")
                        struk_items = database.get_dataframe("SELECT * FROM pembelian WHERE id_nota = ?", (id_nota,))
                        st.markdown("### Struk Otomatis")
                        st.markdown(struk_html_func(struk_items), unsafe_allow_html=True)
                        st.markdown("""
                        <script>
                        function printDivStruk() {
                            var divContents = document.getElementById("strukku").innerHTML;
                            var a = window.open('', '', 'height=500, width=350');
                            a.document.write('<html><head><title>Print Struk</title></head>');
                            a.document.write('<body style="background:white;">');
                            a.document.write(divContents);
                            a.document.write('</body></html>');
                            a.document.close();
                            a.print();
                        }
                        </script>
                        <button onclick="printDivStruk()" style="margin-top:10px;background:#bc6c25;color:#fff;border:none;padding:10px 22px;border-radius:5px;font-size:15px;cursor:pointer;">🖨️ Print Struk</button>
                        """, unsafe_allow_html=True)

        if multi_mode:
            st.markdown("---")
            st.subheader("Keranjang Pembelian (Satu ID Struk)")
            keranjang_obj = st.session_state['keranjang_obj']
            if keranjang_obj.items:
                df_keranjang = pd.DataFrame(keranjang_obj.to_dict_list())
                df_keranjang_show = df_keranjang[["jenis","nama","jumlah","harga","nomor_tujuan","tanggal"]]
                st.dataframe(df_keranjang_show, use_container_width=True)
                if st.button("Simpan Semua ke Riwayat (Satu ID)", key="simpan_semua_keranjang"):
                    id_nota = int(time.time()*1000)
                    tanggal_now = datetime.date.today()
                    nota = Nota(id_nota, keranjang_obj, tanggal_now, kasir="Admin")
                    for item in nota.get_items():
                        database.execute_query(
                            "INSERT INTO pembelian (jenis, nama, harga, jumlah, nomor_tujuan, tanggal, id_nota) VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (
                                item.jenis, item.nama, item.harga, item.jumlah,
                                item.nomor_tujuan or "",
                                item.tanggal.strftime("%Y-%m-%d"), id_nota
                            )
                        )
                    st.success(f"Berhasil menyimpan {len(nota.get_items())} pembelian dalam 1 ID.")

                    # --- CETAK STRUK OTOMATIS (multi) ---
                    struk_items = database.get_dataframe("SELECT * FROM pembelian WHERE id_nota = ?", (id_nota,))
                    st.markdown("### Struk Otomatis")
                    st.markdown(struk_html_func(struk_items), unsafe_allow_html=True)
                    st.markdown("""
                    <script>
                    function printDivStruk() {
                        var divContents = document.getElementById("strukku").innerHTML;
                        var a = window.open('', '', 'height=500, width=350');
                        a.document.write('<html><head><title>Print Struk</title></head>');
                        a.document.write('<body style="background:white;">');
                        a.document.write(divContents);
                        a.document.write('</body></html>');
                        a.document.close();
                        a.print();
                    }
                    </script>
                    <button onclick="printDivStruk()" style="margin-top:10px;background:#bc6c25;color:#fff;border:none;padding:10px 22px;border-radius:5px;font-size:15px;cursor:pointer;">🖨️ Print Struk</button>
                    """, unsafe_allow_html=True)

                    keranjang_obj.clear()
            else:
                st.info("Keranjang masih kosong.")
        st.markdown("</div>", unsafe_allow_html=True)

def riwayat_pembelian():
    st.header("Riwayat Pembelian")

    if 'msg_sukses_hapus' in st.session_state:
        st.success(st.session_state['msg_sukses_hapus'])
        del st.session_state['msg_sukses_hapus']
    if 'msg_update' in st.session_state:
        st.success(st.session_state['msg_update'])
        del st.session_state['msg_update']

    df_all = database.get_dataframe("SELECT * FROM pembelian ORDER BY tanggal DESC, id_nota DESC, id DESC")
    with st.expander("🔍 Filter Riwayat", expanded=False):
        nama_filter = st.text_input("Cari nama barang/jasa:", placeholder="Masukkan nama barang/jasa...")
        jenis_filter = st.selectbox("Jenis", options=["Semua", "Barang", "Jasa"])
        idnota_filter = st.text_input("Cari ID Nota:", placeholder="Masukkan ID Nota...")
        colT1, colT2 = st.columns(2)
        with colT1:
            tgl_mulai = st.date_input("Tanggal Mulai", value=datetime.date.today() - datetime.timedelta(days=30))
        with colT2:
            tgl_sampai = st.date_input("Tanggal Sampai", value=datetime.date.today())

    df = df_all.copy()
    if 'nama_filter' in locals() and nama_filter:
        df = df[df['nama'].str.contains(nama_filter, case=False, na=False)]
    if 'jenis_filter' in locals() and jenis_filter != "Semua":
        df = df[df['jenis'] == jenis_filter]
    if 'idnota_filter' in locals() and idnota_filter:
        df = df[df['id_nota'].astype(str).str.contains(idnota_filter.strip())]
    if 'tgl_mulai' in locals() and 'tgl_sampai' in locals():
        df = df[
            (pd.to_datetime(df['tanggal']) >= pd.to_datetime(str(tgl_mulai))) &
            (pd.to_datetime(df['tanggal']) <= pd.to_datetime(str(tgl_sampai)))
        ]

    if df.empty:
        st.info("Belum ada data pembelian dengan filter di atas.")
    else:
        df['Total Harga (Rp)'] = df.apply(
            lambda row: format_rp(row['harga'] * row['jumlah']) if (row['jenis'] == 'Barang' and row['jumlah'] is not None) else format_rp(row['harga']),
            axis=1
        )
        st.dataframe(
            df[['id', 'id_nota', 'jenis', 'nama', 'jumlah', 'nomor_tujuan', 'Total Harga (Rp)', 'tanggal']],
            use_container_width=True,
            height=380
        )

        st.markdown("---")
        st.markdown("### Edit Transaksi (ID Terpilih)")
        edit_id = st.number_input("ID Pembelian untuk diedit", min_value=1, step=1, key="edit_id")
        row_edit = database.fetch_query("SELECT * FROM pembelian WHERE id = ?", (edit_id,), fetch_all=False)
        if row_edit:
            new_nama = st.text_input("Nama Baru", value=row_edit['nama'], key="edit_nama")
            new_jumlah = st.number_input("Jumlah Baru", min_value=1, value=row_edit['jumlah'] if row_edit['jumlah'] else 1, key="edit_jumlah")
            new_harga = st.number_input("Harga Baru", min_value=0.0, value=row_edit['harga'] if row_edit['harga'] else 0.0, key="edit_harga")
            if st.button("Update Transaksi", key="btn_update"):
                database.execute_query(
                    "UPDATE pembelian SET nama=?, jumlah=?, harga=? WHERE id=?",
                    (new_nama, new_jumlah, new_harga, edit_id)
                )
                st.session_state['msg_update'] = "Transaksi berhasil diupdate."
                st.rerun()
        else:
            st.info("Masukkan ID transaksi yang ingin diedit.")

        st.markdown("---")
        st.markdown("### Void/Hapus Semua Transaksi dalam Satu Struk (id_nota)")
        hapus_idnota = st.text_input("ID Nota yang ingin dihapus (hapus semua item dengan id_nota ini):")
        if st.button("Hapus Semua dalam Struk", key="btn_hapus_struk"):
            if not hapus_idnota.strip().isdigit():
                st.session_state['msg_sukses_hapus'] = "Masukkan ID Nota yang valid!"
                st.rerun()
            else:
                hapus_idnota_int = int(hapus_idnota)
                cek = database.get_dataframe("SELECT * FROM pembelian WHERE id_nota = ?", (hapus_idnota_int,))
                if cek.empty:
                    st.session_state['msg_sukses_hapus'] = "ID Nota tidak ditemukan."
                    st.rerun()
                else:
                    database.execute_query("DELETE FROM pembelian WHERE id_nota = ?", (hapus_idnota_int,))
                    st.session_state['msg_sukses_hapus'] = f"Berhasil menghapus seluruh isi struk dengan ID Nota {hapus_idnota_int}."
                    st.rerun()

        st.markdown("---")
        st.subheader("Hapus Riwayat Pembelian (Multi ID)")
        ids_hapus = st.text_input(
            "Masukkan ID Pembelian yang ingin dihapus (pisahkan dengan koma, misal: 5,7,8):",
            placeholder="Contoh: 2,5,10"
        )
        if st.button("Hapus", key="hapus_pembelian_multi"):
            if not ids_hapus.strip():
                st.session_state['msg_sukses_hapus'] = "Masukkan minimal satu ID!"
                st.rerun()
            else:
                try:
                    id_list = [int(x.strip()) for x in ids_hapus.split(",") if x.strip().isdigit()]
                except Exception:
                    id_list = []
                if not id_list:
                    st.session_state['msg_sukses_hapus'] = "Format ID tidak valid."
                    st.rerun()
                else:
                    deleted = []
                    not_found = []
                    for id_del in id_list:
                        cek = database.fetch_query("SELECT * FROM pembelian WHERE id = ?", (id_del,), fetch_all=False)
                        if cek:
                            database.execute_query("DELETE FROM pembelian WHERE id = ?", (id_del,))
                            deleted.append(str(id_del))
                        else:
                            not_found.append(str(id_del))
                    msg = ""
                    if deleted:
                        msg += f"Berhasil menghapus ID: {', '.join(deleted)}. "
                    if not_found:
                        msg += f"ID tidak ditemukan: {', '.join(not_found)}."
                    st.session_state['msg_sukses_hapus'] = msg.strip()
                    st.rerun()

def ringkasan_pembelian():
    st.header("Rekap Pembelian")
    st.markdown("### Atur Range Waktu")
    df = database.get_dataframe("SELECT * FROM pembelian")
    tgl1 = st.date_input("Dari tanggal", value=datetime.date.today() - datetime.timedelta(days=30), key="tgl_awal_rks")
    tgl2 = st.date_input("Sampai tanggal", value=datetime.date.today(), key="tgl_akhir_rks")

    df_range = df[
        (pd.to_datetime(df['tanggal']) >= pd.to_datetime(str(tgl1))) &
        (pd.to_datetime(df['tanggal']) <= pd.to_datetime(str(tgl2)))
    ]
    total_semua = df_range.apply(lambda row: row['harga'] * row['jumlah'] if (row['jenis'] == "Barang" and row['jumlah'] is not None) else row['harga'], axis=1).sum()
    df_barang = df_range[df_range['jenis'] == "Barang"]
    total_barang = (df_barang['harga'] * df_barang['jumlah']).sum() if not df_barang.empty else 0
    total_jasa = df_range[df_range['jenis']=="Jasa"]['harga'].sum()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
            <div style="background-color:#ead7c2;padding:20px;border-radius:15px;text-align:center;max-width:100%;min-width:0;">
                <div style="color:#7d4f21; font-weight:bold; font-size:1.3em; margin-bottom:10px;">Total Seluruh</div>
                <span style="color:#222; font-size:2em; font-weight:bold; word-break:break-all;display:block;">
                    {format_rp(total_semua)}
                </span>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div style="background-color:#f7e1c2;padding:20px;border-radius:15px;text-align:center;max-width:100%;min-width:0;">
                <div style="color:#7d4f21; font-weight:bold; font-size:1.3em; margin-bottom:10px;">Total Barang</div>
                <span style="color:#222; font-size:2em; font-weight:bold; word-break:break-all;display:block;">
                    {format_rp(total_barang)}
                </span>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
            <div style="background-color:#f7e7da;padding:20px;border-radius:15px;text-align:center;max-width:100%;min-width:0;">
                <div style="color:#7d4f21; font-weight:bold; font-size:1.3em; margin-bottom:10px;">Total Jasa</div>
                <span style="color:#222; font-size:2em; font-weight:bold; word-break:break-all;display:block;">
                    {format_rp(total_jasa)}
                </span>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Jumlah Transaksi per Jenis (Bar Chart)")
    st.bar_chart(df_range['jenis'].value_counts())

    st.markdown("#### Grafik Total Transaksi Harian")
    if not df_range.empty:
        df_range['tanggal'] = pd.to_datetime(df_range['tanggal'])
        df_range['total_row'] = df_range.apply(
            lambda row: row['harga'] * row['jumlah'] if (row['jenis'] == "Barang" and row['jumlah'] is not None) else row['harga'], axis=1
        )
        daily = df_range.groupby('tanggal')['total_row'].sum().reset_index()
        daily = daily.sort_values('tanggal')
        st.bar_chart(daily.set_index('tanggal')['total_row'])

def main():
    if menu == "🛒 Input Pembelian":
        input_pembelian()
    elif menu == "📑 Riwayat Pembelian":
        riwayat_pembelian()
    elif menu == "📊 Rekap Pembelian":
        ringkasan_pembelian()
    st.markdown("---")
    st.caption("Aplikasi Sederhana Pembelian Barang & Jasa Minimarket | Tugas Besar Pemrograman Berbasis Objek")

if __name__ == "__main__":
    main()