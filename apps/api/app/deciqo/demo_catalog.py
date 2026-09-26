"""Isi toko demo SINTETIS: ditulis tim, bukan data pelanggan.

Dipakai dua pihak dengan id yang sama: toko Woo sintetis (`mock_woo`) menyajikannya lewat REST,
dan seed akun demo menyimpannya lewat `ingest`. Karena id produk dan ulasan identik, sinkron dari
toko demo setelah seed menghasilkan `unchanged`, bukan duplikat.

Tanggal ulasan relatif terhadap saat toko dibuat (beberapa minggu terakhir), sehingga tindak
lanjut setelah keputusan dan tren per hari bermakna di demo.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

# Tiap ulasan: (id, rating, hari yang lalu, varian, teks)
PRODUCTS: list[dict] = [
    {
        "id": 101,
        "sku": "TAS-KNV-14",
        "name": "Tas laptop kanvas 14 inci",
        "price": "189000",
        "description": (
            "Tas laptop bahan kanvas tebal, muat laptop hingga 14 inch. Warna hitam. Dilengkapi "
            "tali bahu yang bisa diatur dan satu kantong depan untuk charger dan mouse."
        ),
        "attributes": [{"name": "Bahan", "options": ["Kanvas"]}, {"name": "Warna", "options": ["Hitam"]}],
        "reviews": [
            (1011, 2, 20, "", "Laptop 14 inch saya tidak muat, resletingnya gak bisa ditutup rapat."),
            (1012, 3, 15, "", "Kantong dalamnya sempit, laptop 14 inci harus dipaksa masuk."),
            (1013, 5, 9, "", "Bahannya bagus dan jahitannya rapi, tapi agak sempit buat laptop 14 inch saya."),
            (1014, 5, 6, "", "Ukurannya pas untuk laptop 13 inch saya, masuk dengan mudah."),
        ],
    },
    {
        "id": 102,
        "sku": "KMJ-LINEN",
        "name": "Kemeja linen lengan panjang",
        "price": "249000",
        "description": (
            "Kemeja linen lengan panjang, bahan adem dan ringan untuk dipakai seharian. Tersedia "
            "ukuran S, M, L, XL. Warna putih, krem, dan biru muda."
        ),
        "attributes": [{"name": "Ukuran", "options": ["S", "M", "L", "XL"]},
                       {"name": "Bahan", "options": ["Linen"]}],
        "reviews": [
            (1021, 2, 24, "L", "Ukuran L kekecilan di dada, biasanya saya pakai L selalu pas."),
            (1022, 3, 19, "M", "Kecilan dari perkiraan, lingkar dadanya sempit."),
            (1023, 2, 13, "XL", "Kegedean banget XL nya, bahunya turun."),
            (1024, 1, 11, "L", "Pesan ukuran L yang datang malah M, kecewa."),
            (1025, 5, 8, "M", "Bahannya adem, enak dipakai seharian di kantor."),
            (1026, 4, 4, "S", "Jahitan rapi, warnanya sesuai foto."),
        ],
    },
    {
        "id": 103,
        "sku": "KRS-LIPAT",
        "name": "Kursi lipat camping",
        "price": "159000",
        "description": (
            "Kursi lipat camping rangka besi, beban maksimal 100 kg. Ukuran saat dibuka "
            "50 x 50 x 80 cm. Mudah dilipat dan dibawa ke mana saja."
        ),
        "attributes": [{"name": "Rangka", "options": ["Besi"]}],
        "reviews": [
            (1031, 3, 25, "", "Setelah dilipat ternyata masih panjang, tidak muat di bagasi motor saya."),
            (1032, 2, 18, "", "Ukuran lipatnya besar, susah masuk bagasi mobil kecil."),
            (1033, 2, 22, "", "Pengiriman lama sekali, hampir dua minggu baru sampai."),
            (1034, 3, 12, "", "Kurirnya lambat, paket telat seminggu dari estimasi."),
            (1035, 1, 28, "", "Penjual tidak membalas chat waktu saya tanya soal garansi."),
            (1036, 2, 26, "", "Chat ke penjual dicuekin, responnya lama sekali."),
            (1037, 5, 10, "", "Kursinya kokoh, enak buat mancing di pinggir danau."),
        ],
    },
    {
        # Kontrol: hanya pujian. Tidak boleh menghasilkan temuan, berapa pun bintangnya.
        "id": 104,
        "sku": "BTL-750",
        "name": "Botol minum stainless 750 ml",
        "price": "99000",
        "description": (
            "Botol minum stainless steel 750 ml, dinding ganda, menjaga minuman dingin hingga "
            "12 jam. Tutup ulir anti bocor."
        ),
        "attributes": [{"name": "Kapasitas", "options": ["750 ml"]}],
        "reviews": [
            (1041, 5, 21, "", "Ukuran sesuai, pas dibawa ke kantor tiap hari."),
            (1042, 3, 14, "", "Ukurannya pas di tas, airnya tetap dingin sampai sore."),
            (1043, 4, 7, "", "Tutupnya rapat, tidak bocor di dalam tas."),
            (1044, 5, 3, "", "Bagus, sesuai deskripsi."),
        ],
    },
]

# Fakta yang sudah dikonfirmasi merchant pada kursi lipat (ukuran lipat tidak ada di listing).
CONFIRMED_FACTS = [
    {"product_sku": "KRS-LIPAT", "attribute_hint": ("lipat", "fold", "size", "ukuran"),
     "value": "15 x 20 x 85", "unit": "cm", "location": "folded"},
]

# Keputusan contoh pada kursi lipat: pengiriman sedang ditangani, layanan penjual sudah
# diterapkan beberapa hari lalu (dipantau; ulasan baru dari demo tools membuka isunya lagi).
SEED_DECISIONS = [
    {"product_sku": "KRS-LIPAT", "attribute_hint": ("service", "seller", "layanan", "respon", "chat"),
     "decision": "acted", "days_ago": 5,
     "note": "Mengaktifkan balasan otomatis chat dan menambah jam respons 08.00-21.00."},
]

# Ulasan yang ditambahkan tombol "demo live" (±8 detik sekali), ditulis "sekarang".
LIVE_REVIEWS = [
    (103, 2, "Chat ke penjual tidak dibalas lagi, padahal mau tanya soal pengiriman."),
    (101, 2, "Laptop 14 inch tetap tidak muat, resleting tidak bisa ditutup."),
    (102, 3, "Ukuran M kekecilan di bagian dada."),
]


def review_time(days_ago: int, base: datetime | None = None) -> str:
    base = base or datetime.now(timezone.utc)
    moment = (base - timedelta(days=days_ago)).replace(hour=3, minute=0, second=0, microsecond=0)
    return moment.isoformat()


def as_catalog(base: datetime | None = None) -> list[dict]:
    """Bentuk katalog yang diterima `ingest.upsert_catalog`."""
    items = []
    for product in PRODUCTS:
        items.append({
            "source_item_id": str(product["id"]),
            "title": product["name"],
            "url": f"https://woo-demo.deciqo.app/product/{product['sku'].lower()}",
            "description": product["description"],
            "specs": {a["name"]: ", ".join(a["options"]) for a in product["attributes"]},
            "variants": next((a["options"] for a in product["attributes"] if a["name"] == "Ukuran"), []),
            "price": float(product["price"]),
            "reviews": [
                # Tanpa varian: REST Woo tidak membawa varian pada ulasan, dan seed harus identik
                # dengan hasil sinkron supaya tidak dihitung sebagai perubahan.
                {"id": str(rid), "rating": rating, "text": text, "review_time": review_time(days, base)}
                for rid, rating, days, _variant, text in product["reviews"]
            ],
        })
    return items
