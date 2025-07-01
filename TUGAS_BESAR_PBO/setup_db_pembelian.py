import sqlite3

DB_NAME = "pembelian.db"

def create_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pembelian (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            jenis TEXT,
            nama TEXT,
            harga REAL,
            jumlah INTEGER,
            nomor_tujuan TEXT,
            tanggal TEXT,
            id_nota INTEGER
        )
    """)
    conn.commit()
    conn.close()
    print("Tabel pembelian siap dipakai! (sudah ada id_nota)")

if __name__ == "__main__":
    create_table()