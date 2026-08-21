"""detect_category() - menebak kategori toko alih-alih menanyakannya.

Sebelumnya kategori adalah satu-satunya isian WAJIB di layar unggah. Menanyakannya aneh dari
sisi pengguna: berkas yang baru saja ia unggah sudah memuat nama produknya, dan sistem yang
bertanya "ini toko apa" tepat setelah membaca 66 baris berisi nama produk terbaca seperti
sistem yang tidak membaca apa-apa.

Kategori dipakai untuk SATU hal - memilih baseline pembanding di `compare_category_baseline()`.
Karena itu tebakan yang salah bukan kesalahan kecil: baseline muncul di layar sebagai selisih
persen, dan selisih persen terbaca seperti fakta. Jadi berlaku tiga aturan:

  1. Tebakan selalu ditampilkan, tidak pernah dipakai diam-diam.
  2. Tebakan selalu membawa dasarnya - dari nama produk, dari teks ulasan, atau tidak dari
     apa-apa (`bawaan`).
  3. Bukti yang tipis menghasilkan `ConfidenceLevel.RENDAH`, dan layar hasil meminta pengguna
     memastikannya sendiri alih-alih menyatakannya sebagai temuan.

Metodenya sengaja pencocokan kata, bukan model. Kategori adalah kelas taksonomi yang sudah
dikunci sejak Fase 0 dan jumlahnya lima; melatih pengklasifikasi untuk lima kelas yang
kosakatanya sedangkal ini menambah satu lagi hal yang bisa gagal dimuat saat startup, tanpa
menambah apa pun yang tidak dicapai daftar kata.
"""

from __future__ import annotations

import re
from collections import defaultdict

from ..schemas import Category, ConfidenceLevel, CategoryGuess, ProcessedReview

# Kata penanda per kategori. Diambil dari nama produk pada dataset contoh dan dari kosakata
# yang lazim di ekspor marketplace Indonesia - bukan daftar lengkap, dan tidak perlu lengkap:
# yang dibutuhkan hanya cukup untuk memisahkan lima kelas, dan sisanya jatuh ke `other` dengan
# keyakinan rendah, yang memang keadaan sebenarnya.
#
# Kata yang ambigu antar kategori sengaja TIDAK dimasukkan. "tali" ada di tas dan di jam;
# "kotak" ada di semua. Penanda yang menunjuk dua arah menaikkan jumlah kecocokan tanpa
# menaikkan ketepatan, dan jumlah kecocokan itulah yang menjadi keyakinan yang ditampilkan.
PENANDA: dict[Category, tuple[str, ...]] = {
    Category.FASHION: (
        "sepatu", "sandal", "sneakers", "baju", "kemeja", "kaos", "kaus", "celana", "jeans",
        "jaket", "hoodie", "sweater", "dress", "rok", "gamis", "hijab", "kerudung", "jilbab",
        "mukena", "koko", "batik", "tas", "ransel", "dompet", "ikat pinggang", "kacamata",
        "jam tangan", "topi", "kaus kaki", "legging", "blouse", "outer", "cardigan", "piyama",
        "seragam", "wearpack", "heels", "flatshoes", "boots", "sepatu sekolah",
    ),
    Category.ELECTRONICS: (
        "handphone", "smartphone", "laptop", "charger", "kabel data", "powerbank", "earphone",
        "headset", "headphone", "speaker", "mouse", "keyboard", "monitor", "flashdisk",
        "memori", "kamera", "webcam", "printer", "router", "adaptor", "baterai", "casing hp",
        "tempered glass", "smartwatch", "tws", "kipas angin", "rice cooker", "blender",
        "setrika", "dispenser", "mesin cuci", "kulkas", "televisi",
    ),
    Category.FOOD_BEVERAGE: (
        "kopi", "teh", "susu", "keripik", "kerupuk", "snack", "camilan", "biskuit", "roti",
        "kue", "cokelat", "permen", "sambal", "bumbu", "kecap", "saus", "mie", "beras",
        "tepung", "gula", "madu", "minuman", "sirup", "jus", "yogurt", "frozen food",
        "nugget", "sosis", "bakso", "rendang", "abon", "dendeng", "selai", "granola",
    ),
    Category.CRAFT: (
        "rajut", "rajutan", "anyaman", "anyam", "keramik", "gerabah", "ukiran", "pahat",
        "handmade", "kerajinan", "souvenir", "hampers", "bunga kering", "lilin aromaterapi",
        "macrame", "decoupage", "kayu jati", "rotan", "bambu", "tenun", "batik tulis",
        "sulam", "bordir tangan", "clay", "resin art",
    ),
}

# Berapa bagian dari ulasan yang harus tercocokkan sebelum tebakan disebut kuat.
AMBANG_TINGGI = 0.45
AMBANG_SEDANG = 0.20

# Selisih minimum antara juara dan runner-up. Toko yang produknya benar-benar campur akan
# menghasilkan dua kategori dengan skor hampir sama, dan menyebut salah satunya sebagai
# temuan berarti melempar koin lalu menampilkannya sebagai kesimpulan.
MARGIN_MIN = 1.25


# Klitik yang menempel langsung di belakang kata benda dalam Bahasa Indonesia. Tanpa ini
# "kopinya harum" tidak cocok dengan penanda "kopi", dan itu bukan kasus pinggiran: bentuk
# berklitik justru yang lazim dipakai orang saat menulis ulasan - "sepatunya", "bajunya",
# "tasnya", "rasanya". Membiarkannya tidak cocok berarti deteksi dari teks ulasan hampir
# selalu gagal tepat pada korpus yang paling membutuhkannya, yaitu berkas yang nama produknya
# sudah dianonimkan.
KLITIK = "(?:nya|ku|mu)?"


def _cocok(teks: str, penanda: tuple[str, ...]) -> bool:
    """Apakah `teks` memuat salah satu penanda sebagai kata utuh, boleh berklitik.

    Batas kata itu wajib. Tanpanya "tas" cocok di dalam "batas" dan "kue" di dalam
    "kuesioner" - kecocokan palsu yang menaikkan skor fesyen dan makanan pada teks apa pun
    yang cukup panjang.

    Awalan sengaja TIDAK ditangani. Memulihkannya menuntut menebak huruf yang luluh
    ("pengiriman" -> "irim", bukan "kirim"), masalah yang sama sudah tercatat pada penjaga
    domain di tools/qna.py. Penanda di sini kata benda, dan kata benda jarang berawalan.
    """
    return any(
        re.search(rf"(?<![a-z0-9]){re.escape(p)}{KLITIK}(?![a-z0-9])", teks) for p in penanda
    )


def detect_category(reviews: list[ProcessedReview]) -> CategoryGuess:
    """Tebak kategori toko dari nama produk, lalu dari teks ulasan.

    Nama produk didahulukan dan tidak digabung dengan teks ulasan. Nama produk menyebut BENDA
    yang dijual; teks ulasan menyebut apa saja, termasuk benda lain ("dikirim bareng kopi
    pesanan sebelah"). Menggabung keduanya dalam satu keranjang membuat sinyal yang bersih
    diencerkan oleh sinyal yang berisik.

    Teks ulasan dipakai hanya kalau nama produk tidak ada atau tidak memutuskan apa pun -
    keadaan yang nyata: ekspor Shopee yang sudah dianonimkan memuat nama seperti "Produk-1481",
    yang tidak menyebutkan apa pun tentang barangnya.

    Returns:
        CategoryGuess. Selalu terisi; kalau tidak ada yang cocok, `Category.OTHER` dengan
        `basis="bawaan"` dan keyakinan rendah - bukan kategori pertama pada daftar.
    """
    total = len(reviews)
    if not total:
        return CategoryGuess(
            category=Category.OTHER,
            confidence=ConfidenceLevel.RENDAH,
            matched_reviews=0,
            total_reviews=0,
            basis="bawaan",
        )

    nama_produk = [(r.product_name or "").lower() for r in reviews]
    teks_ulasan = [r.clean_text.lower() for r in reviews]

    for basis, korpus in (("nama produk", nama_produk), ("teks ulasan", teks_ulasan)):
        if not any(korpus):
            continue

        skor: dict[Category, int] = defaultdict(int)
        for dokumen in korpus:
            if not dokumen:
                continue
            for kategori, penanda in PENANDA.items():
                if _cocok(dokumen, penanda):
                    skor[kategori] += 1

        if not skor:
            continue

        peringkat = sorted(skor.items(), key=lambda kv: (kv[1], kv[0].value), reverse=True)
        juara, jumlah = peringkat[0]
        runner_up = peringkat[1][1] if len(peringkat) > 1 else 0

        # Juara yang tidak cukup unggul dari runner-up bukan tebakan, itu undian.
        if runner_up and jumlah < runner_up * MARGIN_MIN:
            continue

        bagian = jumlah / total
        if bagian >= AMBANG_TINGGI:
            keyakinan = ConfidenceLevel.TINGGI
        elif bagian >= AMBANG_SEDANG:
            keyakinan = ConfidenceLevel.SEDANG
        else:
            keyakinan = ConfidenceLevel.RENDAH

        return CategoryGuess(
            category=juara,
            confidence=keyakinan,
            matched_reviews=jumlah,
            total_reviews=total,
            basis=basis,
        )

    return CategoryGuess(
        category=Category.OTHER,
        confidence=ConfidenceLevel.RENDAH,
        matched_reviews=0,
        total_reviews=total,
        basis="bawaan",
    )
