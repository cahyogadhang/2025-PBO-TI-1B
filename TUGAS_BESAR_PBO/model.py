import datetime

class Pembelian:
    def __init__(self, jenis, nama, harga, jumlah=None, nomor_tujuan=None, tanggal=None, id_pembelian=None):
        self.id = id_pembelian
        self.jenis = jenis
        self.nama = nama
        self.harga = float(harga)
        self.jumlah = int(jumlah) if jumlah else None
        self.nomor_tujuan = nomor_tujuan
        if isinstance(tanggal, datetime.date):
            self.tanggal = tanggal
        elif isinstance(tanggal, str):
            self.tanggal = datetime.datetime.strptime(tanggal, "%Y-%m-%d").date()
        else:
            self.tanggal = datetime.date.today()

    def to_dict(self):
        return {
            "jenis": self.jenis,
            "nama": self.nama,
            "harga": self.harga,
            "jumlah": self.jumlah,
            "nomor_tujuan": self.nomor_tujuan,
            "tanggal": self.tanggal.strftime("%Y-%m-%d")
        }

class Keranjang:
    def __init__(self):
        self.items = []

    def tambah_item(self, pembelian):
        self.items.append(pembelian)

    def hapus_item(self, idx):
        if 0 <= idx < len(self.items):
            del self.items[idx]

    def total_harga(self):
        return sum(item.harga * (item.jumlah or 1) for item in self.items)

    def clear(self):
        self.items = []

    def to_dict_list(self):
        return [item.to_dict() for item in self.items]

class Nota:
    def __init__(self, id_nota, keranjang, tanggal, kasir="Admin"):
        self.id_nota = id_nota
        self.keranjang = keranjang
        self.tanggal = tanggal
        self.kasir = kasir

    def total(self):
        return self.keranjang.total_harga()

    def get_items(self):
        return self.keranjang.items