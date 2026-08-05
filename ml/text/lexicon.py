"""Leksikon untuk labeling function weak supervision (ADR-015).

Prinsip desain penting: **istilah TOPIK dipisah tegas dari istilah POLARITAS.**

Aspek ditentukan HANYA dari istilah topik (kata benda/tema), sedangkan sentimen ditentukan
dari istilah polaritas (kata sifat). Tanpa pemisahan ini, klausa "pengirimannya bagus" akan
salah dilabeli sebagai aspek `kualitas_produk` hanya karena memuat kata "bagus".

Leksikon ini adalah SUMBER LABEL SILVER, bukan komponen runtime. Kualitasnya diukur terhadap
gold test set berlabel manusia (lihat `make_gold_task.py`), dan hasilnya menentukan apakah
labeling function perlu direvisi sebelum fine-tuning final.
"""

from __future__ import annotations

import re

# --------------------------------------------------------------------------------------
# Normalisasi slang/singkatan (NLP-02 versi dasar, blueprint bagian 18.3)
# Hanya bentuk yang tidak ambigu. Penanda negasi ("ga", "gak", "nggak") sengaja dipetakan
# ke "tidak" supaya deteksi negasi di bawah bekerja seragam.
# --------------------------------------------------------------------------------------
SLANG_MAP: dict[str, str] = {
    "gk": "tidak", "ga": "tidak", "gak": "tidak", "nggak": "tidak", "enggak": "tidak",
    "ngga": "tidak", "tdk": "tidak", "tak": "tidak", "kagak": "tidak",
    "bgt": "banget", "bngt": "banget", "banget2": "banget",
    "udh": "sudah", "udah": "sudah", "sdh": "sudah", "dah": "sudah",
    "blm": "belum", "blom": "belum", "lom": "belum",
    "sy": "saya", "gw": "saya", "gue": "saya", "aq": "saya", "aku": "saya",
    "yg": "yang", "dgn": "dengan", "dg": "dengan",
    "tp": "tapi", "tpi": "tapi", "tetapi": "tapi",
    "krn": "karena", "krna": "karena", "karna": "karena",
    "jd": "jadi", "bs": "bisa", "dr": "dari", "utk": "untuk", "untk": "untuk",
    "dpt": "dapat", "trs": "terus", "sm": "sama", "sma": "sama",
    "klo": "kalau", "kalo": "kalau", "klu": "kalau",
    "msh": "masih", "jg": "juga", "aja": "saja", "aj": "saja", "doang": "saja",
    "bgs": "bagus", "baguss": "bagus", "mantul": "mantap", "mantab": "mantap",
    "recomended": "recommended", "rekomended": "recommended", "rekomen": "recommended",
    "brg": "barang", "brgnya": "barangnya", "cpt": "cepat", "cepet": "cepat",
    "lgsg": "langsung", "lngsg": "langsung", "pengiriman2": "pengiriman",
    "mksh": "terima kasih", "makasih": "terima kasih", "thx": "terima kasih",
    "thanks": "terima kasih", "tq": "terima kasih",
    "okey": "oke", "ok": "oke", "okeh": "oke", "good": "bagus", "nice": "bagus",
    "fast": "cepat", "seler": "seller", "sellernya": "seller",
    "pengirimanya": "pengiriman", "kualitasnya": "kualitas", "barangnya": "barang",
    "ukurannya": "ukuran", "harganya": "harga", "kemasanya": "kemasan",
    "packingnya": "packing", "respon": "respon", "fastrespon": "cepat respon",
}

# --------------------------------------------------------------------------------------
# ISTILAH TOPIK per aspek -> menentukan aspek mana yang disebut sebuah klausa.
# Kunci = id aspek pada configs/taxonomy.yaml (FROZEN, Fase 0).
# --------------------------------------------------------------------------------------
ASPECT_TERMS: dict[str, list[str]] = {
    "kualitas_produk": [
        "kualitas", "mutu", "bahan", "material", "jahitan", "kondisi barang", "kondisinya",
        "rusak", "cacat", "sobek", "robek", "pecah", "patah", "penyok", "lecet", "retak",
        "bocor", "luntur", "berkarat", "awet", "tahan lama", "rapuh", "gampang rusak",
        "kualitasnya", "barangnya bagus", "barangnya jelek",
    ],
    "kesesuaian_deskripsi": [
        "sesuai", "kesesuaian", "deskripsi", "keterangan", "sesuai gambar", "sesuai foto",
        "sesuai pesanan", "sesuai iklan", "beda dengan gambar", "tidak seperti gambar",
        "sesuai ekspektasi", "sesuai harapan", "sesuai deskripsi",
    ],
    "harga_value": [
        "harga", "harganya", "murah", "mahal", "worth", "worth it", "sepadan", "sebanding",
        "terjangkau", "kemahalan", "kemurahan", "value", "diskon", "promo", "budget",
    ],
    "ukuran_varian": [
        "ukuran", "size", "ukurannya", "kekecilan", "kebesaran", "kepanjangan", "kependekan",
        "muat", "sempit", "longgar", "pas di badan", "varian", "warna", "warnanya",
        "model", "tipe", "salah warna", "salah ukuran", "porsi", "takaran", "dimensi",
        "gramasi", "isi bersih",
    ],
    "rasa_kualitas_makanan": [
        "rasa", "rasanya", "enak", "manis", "asin", "gurih", "hambar", "pahit", "asem",
        "basi", "kadaluarsa", "kadaluwarsa", "expired", "renyah", "aroma", "wangi",
    ],
    "kemasan": [
        "kemasan", "kemasannya", "packing", "packaging", "bungkus", "dus", "kardus", "box",
        "segel", "bubble", "bubble wrap", "plastik", "amplop", "dibungkus", "dikemas",
    ],
    "pengiriman": [
        "kirim", "dikirim", "pengiriman", "pengirimannya", "sampai", "nyampe", "kurir",
        "ekspedisi", "ongkir", "ongkos kirim", "resi", "paket", "telat", "terlambat",
        "jne", "j&t", "jnt", "sicepat", "anteraja", "gosend", "grab", "ninja", "pos",
        "estimasi", "proses kirim",
    ],
    "pelayanan_penjual": [
        "seller", "penjual", "pelayanan", "pelayanannya", "respon", "responnya", "ramah",
        "admin", "cs", "customer service", "balas", "dibalas", "chat", "komunikasi",
        "tokonya", "pemilik toko", "fast respon", "slow respon", "dilayani",
    ],
    "kelengkapan": [
        "lengkap", "komplit", "kurang lengkap", "tidak lengkap", "isinya", "isi paket",
        "jumlahnya", "hilang", "kurang satu", "bonus", "aksesoris", "kelengkapan",
        "tidak ada bonus", "item kurang", "kelengkapannya", "jumlah barang", "kurang 1",
        "isi kurang", "tidak sesuai jumlah",
    ],
    "keaslian": [
        "asli", "ori", "original", "palsu", "kw", "tiruan", "abal", "abal-abal", "bajakan",
        "keaslian", "authentic", "replika",
    ],
    "kemudahan_penggunaan": [
        "mudah dipakai", "gampang dipakai", "mudah digunakan", "susah dipakai", "ribet",
        "praktis", "simpel", "rumit", "instalasi", "dipasang", "pemasangan", "cara pakai",
        "mudah dipasang", "user friendly", "gampang digunakan", "penggunaan", "pemakaian",
        "dioperasikan", "digunakan", "dipakai", "settingnya", "pengoperasian",
    ],
}

# Istilah rujukan produk yang terlalu umum untuk dipakai sebagai pemicu utama: "barang bagus"
# memang berbicara tentang kualitas produk, tetapi "barang cepat sampai" berbicara tentang
# pengiriman. Karena itu istilah ini hanya memicu `kualitas_produk` sebagai FALLBACK - dipakai
# hanya jika tidak ada aspek lain yang terdeteksi pada klausa yang sama.
FALLBACK_ASPECT = "kualitas_produk"
FALLBACK_TERMS: list[str] = [
    "barang", "barangnya", "produk", "produknya", "itemnya", "bendanya",
]

# --------------------------------------------------------------------------------------
# ISTILAH POLARITAS -> menentukan sentimen klausa. Sengaja TIDAK dipakai untuk aspek.
# --------------------------------------------------------------------------------------
POSITIVE_TERMS: list[str] = [
    "bagus", "baik", "mantap", "memuaskan", "puas", "suka", "recommended", "oke", "keren",
    "cepat", "ramah", "aman", "rapi", "mulus", "sesuai", "murah", "worth", "enak", "awet",
    "lengkap", "asli", "original", "mudah", "gampang", "praktis", "top", "sip", "cocok",
    "nyaman", "berkualitas", "terjangkau", "memuaskan", "sempurna", "istimewa", "bermanfaat",
    "terbaik", "terima kasih", "amanah", "terpercaya", "sesuai harapan", "sesuai ekspektasi",
]

NEGATIVE_TERMS: list[str] = [
    "jelek", "buruk", "rusak", "cacat", "kecewa", "mengecewakan", "lambat", "lama", "telat",
    "terlambat", "mahal", "kemahalan", "palsu", "tiruan", "sobek", "robek", "pecah", "patah",
    "penyok", "lecet", "retak", "bau", "basi", "hilang", "susah", "ribet", "rumit", "salah",
    "komplain", "retur", "zonk", "parah", "nyesel", "menyesal", "bocor", "luntur", "gagal",
    "kotor", "murahan", "rapuh", "kadaluarsa", "expired", "kurang", "mengecewakan",
    "kekecilan", "kebesaran", "sempit", "hambar", "berkarat", "abal", "nipu", "tipu",
]

# Penanda negasi — membalik polaritas kata sesudahnya dalam jendela terbatas.
NEGATION_MARKERS: list[str] = ["tidak", "bukan", "belum", "jangan", "tanpa", "kurang"]
NEGATION_WINDOW = 3  # jumlah kata sesudah penanda yang terkena pembalikan

# Konjungsi kontras — pemisah klausa. "bagus tapi lama" harus jadi dua klausa,
# kalau tidak sentimennya saling menghapus.
CONTRAST_MARKERS: list[str] = [
    "tapi", "namun", "sayangnya", "sayang", "cuma", "hanya saja", "meskipun", "walaupun",
    "kecuali", "padahal",
]


def _compile_terms(terms: list[str]) -> re.Pattern[str]:
    """Susun satu regex ber-word-boundary dari daftar istilah, terpanjang didahulukan."""
    ordered = sorted(terms, key=len, reverse=True)
    joined = "|".join(re.escape(t) for t in ordered)
    return re.compile(rf"(?<!\w)(?:{joined})(?!\w)", re.IGNORECASE)


ASPECT_PATTERNS: dict[str, re.Pattern[str]] = {
    aspect: _compile_terms(terms) for aspect, terms in ASPECT_TERMS.items()
}
POSITIVE_PATTERN = _compile_terms(POSITIVE_TERMS)
NEGATIVE_PATTERN = _compile_terms(NEGATIVE_TERMS)
NEGATION_PATTERN = _compile_terms(NEGATION_MARKERS)
FALLBACK_PATTERN = _compile_terms(FALLBACK_TERMS)

ALL_ASPECTS: tuple[str, ...] = tuple(ASPECT_TERMS.keys())
