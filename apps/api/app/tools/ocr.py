"""ING-10 - membaca teks ulasan dari tangkapan layar halaman marketplace.

**Kenapa jalur ini ada.** Ekspor CSV tidak tersedia di setiap lapak, dan pelaku usaha mikro
kerap hanya memegang tangkapan layar dari HP-nya. Menolak masukan itu berarti menolak justru
pengguna yang paling tidak punya jalan lain.

**Kenapa hasilnya tidak pernah langsung dianalisis.** Pembacaan teks dari gambar tidak pernah
sempurna, dan satu huruf yang salah baca merambat ke seluruh hasil: aspek salah dikenali,
kutipan bukti berbunyi janggal, angka ikut bergeser. Karena itu keluaran modul ini berstatus
DRAF - frontend menampilkannya untuk diperiksa dan disunting lebih dulu. Pemilik toko adalah
satu-satunya pihak yang tahu bunyi ulasan aslinya.

**Yang sengaja tidak dilakukan.** Modul ini tidak menyimpulkan apa pun dari isi GAMBAR - tidak
menilai kondisi barang, tidak membaca bintang yang digambar sebagai ikon. Ia hanya mengubah
piksel huruf menjadi huruf. Kemampuan menyimpulkan kondisi produk dari foto belum lolos
gerbang go/no-go (lihat docs/LIMITATIONS.md), dan tidak diam-diam diselundupkan lewat sini.

Tesseract dipilih, bukan mesin berbasis neural, karena masukannya berupa tangkapan layar:
huruf hasil render, kontras tinggi, tanpa distorsi perspektif. Pada bahan seperti itu Tesseract
akurat, muat dalam beberapa puluh megabyte, dan tidak menambah unduhan model saat startup -
tiga hal yang penting pada target CPU-only (blueprint bagian 30.3).
"""

from __future__ import annotations

import io
import logging
import os
import re
from dataclasses import dataclass, field
from functools import lru_cache
from statistics import median

from app.tools.privacy import redact_personal_data

log = logging.getLogger("insightulasan.ocr")

# Bahasa yang diminta ke Tesseract. Indonesia lebih dulu, Inggris sebagai pendamping karena
# ulasan Indonesia rutin menyelipkan kata Inggris ("packing", "seller", "fast respon").
OCR_LANG = os.getenv("OCR_LANG", "ind+eng")

# Ambang keyakinan per kata. Di bawah ini kata dianggap sampah OCR dan dibuang sebelum
# tergabung menjadi kalimat - lebih baik kalimatnya terpotong daripada memuat kata yang
# tidak pernah ada di layar.
MIN_WORD_CONF = 40.0

# Rata-rata keyakinan satu blok. Di atas ini blok ditandai "terbaca jelas", di bawahnya
# "perlu diperiksa". Dua tingkat saja, dan keduanya ditulis sebagai kata di antarmuka -
# angka keyakinan mentah tidak berarti apa pun bagi pemilik toko (BRAND_GUIDELINES bagian 7).
CONF_TINGGI = 78.0

MIN_REVIEW_CHARS = 12
MAX_REVIEWS_PER_IMAGE = 60

# Batas ukuran per gambar. Tangkapan layar HP yang wajar berada jauh di bawah ini; berkas yang
# jauh lebih besar hampir pasti foto kamera resolusi penuh, yang bukan bahan modul ini.
MAX_IMAGE_BYTES = 8 * 1024 * 1024

# Pembesaran sebelum OCR. Tangkapan layar HP kerap memuat teks setinggi 11-13 piksel,
# sedangkan Tesseract bekerja paling baik di sekitar 30 piksel per huruf kapital.
UPSCALE_TARGET_WIDTH = 1600


class OcrUnavailable(RuntimeError):
    """Tesseract tidak terpasang atau gagal dipanggil."""


class OcrRejected(ValueError):
    """Berkas ditolak sebelum sempat dibaca - ukuran, format, atau isinya."""


@dataclass
class OcrLine:
    """Satu baris teks beserta posisi dan keyakinannya."""

    text: str
    top: int
    height: int
    conf: float


@dataclass
class OcrDraft:
    """Satu calon ulasan hasil pembacaan. Selalu berstatus draf."""

    text: str
    rating: int | None = None
    confidence: float = 0.0
    lines: int = 1

    @property
    def confidence_level(self) -> str:
        return "tinggi" if self.confidence >= CONF_TINGGI else "rendah"


@dataclass
class OcrImageResult:
    image: str
    drafts: list[OcrDraft] = field(default_factory=list)


# --------------------------------------------------------------------------------------
# Penyaring perabot antarmuka
# --------------------------------------------------------------------------------------

# Tangkapan layar memuat jauh lebih banyak tombol daripada kalimat. Semua pola di bawah adalah
# teks ANTARMUKA marketplace, bukan tulisan pembeli, dan ikut terbaca kalau tidak disingkirkan.
CHROME_EXACT = {
    "balas", "bermanfaat", "membantu", "laporkan", "lapor", "ulasan", "ulasan produk",
    "semua", "terbaru", "terlama", "dengan media", "dengan foto", "dengan komentar",
    "lihat balasan", "lihat semua", "lihat selengkapnya", "selengkapnya", "sembunyikan",
    "penilaian produk", "penilaian", "rating produk", "beli lagi", "chat", "keranjang",
    "bagikan", "suka", "komentar", "tanya penjual", "diskusi produk", "spesifikasi",
    "deskripsi produk", "produk terkait", "kembali", "cari", "beranda", "profil",
    "reply", "helpful", "report", "see more", "show more", "all", "latest",
}

CHROME_PREFIX = (
    "varian:", "variasi:", "warna:", "ukuran:", "tipe:", "model:", "jumlah:",
    "kualitas produk:", "kondisi:", "harga:", "pengiriman:", "dikirim dari",
    "balasan penjual", "respons penjual", "dari penjual", "penjual:",
    "rp", "total:", "subtotal", "diskon", "gratis ongkir", "voucher",
)

# Baris yang hanya berisi tanggal atau penanda waktu relatif.
RE_TANGGAL = re.compile(
    r"^\s*(?:"
    r"\d{1,2}[-/ ]\w{2,9}[-/ ]\d{2,4}"          # 12 Mei 2024, 12/05/2024
    r"|\d{4}-\d{2}-\d{2}"                        # 2024-05-12
    r"|\d+\s*(?:detik|menit|jam|hari|minggu|bulan|tahun)\s*(?:yang\s*)?lalu"
    r"|kemarin|hari ini|baru saja"
    r")\s*[\d:.\s]*$",
    re.I,
)

# Nama akun Shopee/Tokopedia disamarkan penjualnya sendiri: "b*****a", "ri***na".
RE_NAMA_TERSAMAR = re.compile(r"^[\w.]{0,12}\*{2,}[\w.]{0,12}$")

# Bintang yang dirender sebagai teks, bukan sebagai ikon.
RE_BINTANG_TEKS = re.compile(r"^[\s★☆*]{3,}$")

RE_RATING = re.compile(
    r"(?:^|\s)(?:(\d)\s*/\s*5|bintang\s*(\d)|(\d)\s*bintang|rating\s*(\d))(?:\s|$)", re.I
)

# Chip penyaring di kepala halaman: "5 Bintang", "Bintang 4", "5/5". Bentuknya identik dengan
# rating yang ditulis pembeli, dan yang membedakan hanyalah bahwa chip BERDIRI SENDIRI tanpa
# kalimat di sekitarnya.
RE_CHIP_RATING = re.compile(r"^\s*(?:\d\s*bintang|bintang\s*\d|\d\s*/\s*5|\d\s*★+)\s*$", re.I)

# Baris tanpa satu pun huruf - biasanya sisa ikon, angka jumlah suka, atau garis pemisah.
RE_ADA_HURUF = re.compile(r"[A-Za-zÀ-ɏ]")

# Pemisah yang dipakai antarmuka untuk menempelkan dua keterangan berbeda pada satu baris:
# "12 Mei 2024 | Varian: Hitam, L". Keduanya perabot, tetapi baris utuhnya tidak cocok dengan
# pola perabot mana pun - jadi ia harus dipecah lebih dulu.
RE_PEMISAH = re.compile(r"\s*[|·•‧⋅»›]\s*|\s{3,}")


# Tombol antarmuka kerap membawa jumlahnya: "Bermanfaat (3)", "Lihat Balasan (2)", "Suka 12".
# Angkanya dilepas sebelum dicocokkan supaya daftar CHROME_EXACT tidak perlu memuat setiap
# kemungkinan hitungan.
RE_HITUNGAN_EKOR = re.compile(r"[\s(\[]*\d+[\s)\]]*$")


def _is_chrome(line: str) -> bool:
    low = line.strip().lower().rstrip(":·.-")
    if not low:
        return True
    if low in CHROME_EXACT:
        return True
    if RE_HITUNGAN_EKOR.sub("", low).strip() in CHROME_EXACT:
        return True
    if low.startswith(CHROME_PREFIX):
        return True
    if RE_TANGGAL.match(low) or RE_NAMA_TERSAMAR.match(low) or RE_BINTANG_TEKS.match(line):
        return True
    if RE_CHIP_RATING.match(line):
        return True
    # Baris tanpa huruf sama sekali tidak mungkin kalimat ulasan.
    if not RE_ADA_HURUF.search(line):
        return True
    return False


def bersihkan_baris(line: str) -> str:
    """Buang potongan perabot dari dalam satu baris, sisakan yang benar-benar tulisan pembeli.

    Penyaringan per BARIS UTUH tidak cukup. Tesseract menggabungkan apa pun yang sebaris,
    sehingga tanggal, varian, dan tombol kerap menempel pada kalimat ulasan - dan baris
    gabungan itu tidak cocok dengan pola perabot mana pun, jadi ia lolos utuh ke hasil.

    Yang dikembalikan adalah string kosong bila seluruh potongannya perabot.
    """
    sisa = [p for p in RE_PEMISAH.split(line) if p.strip() and not _is_chrome(p)]
    return " ".join(sisa).strip()


def _rating_dari(line: str) -> int | None:
    """Bintang hanya terbaca bila DITULIS sebagai teks di dalam kalimat.

    Sebagian besar marketplace menggambar bintang sebagai ikon, dan ikon tidak punya huruf
    untuk dibaca. Karena itu rating lebih sering None daripada terisi - itu perilaku yang
    benar. Menebak bintang dari nada kalimat akan mengarang angka yang lalu ikut terhitung
    ke dalam severity, dan severity memang sudah diturunkan dari rating.

    Chip penyaring "5 Bintang" di kepala halaman sengaja TIDAK dihitung. Ia menyebut penyaring
    yang sedang aktif, bukan penilaian ulasan mana pun, dan mengambilnya berarti memberi setiap
    ulasan di layar itu rating yang sama.
    """
    if RE_CHIP_RATING.match(line):
        return None
    match = RE_RATING.search(line)
    if not match:
        return None
    nilai = next((int(g) for g in match.groups() if g), None)
    return nilai if nilai and 1 <= nilai <= 5 else None


# --------------------------------------------------------------------------------------
# Pengelompokan baris menjadi ulasan
# --------------------------------------------------------------------------------------


def group_lines_into_drafts(lines: list[OcrLine]) -> list[OcrDraft]:
    """Kelompokkan baris berurutan menjadi calon ulasan.

    Pemisahnya JARAK VERTIKAL, bukan tanda baca. Di halaman ulasan, dua ulasan berbeda selalu
    dipisahkan ruang yang lebih besar daripada jarak antar-baris di dalam satu ulasan, sedangkan
    tanda baca sama sekali tidak dapat diandalkan - pembeli menulis tanpa titik, dan satu ulasan
    kerap memuat beberapa kalimat.

    Ambangnya relatif terhadap tinggi baris pada gambar itu sendiri, bukan angka piksel tetap,
    supaya tangkapan layar HP 720p dan tangkapan layar desktop 4K diperlakukan sama.
    """
    dipakai = []
    for ln in sorted(lines, key=lambda x: x.top):
        bersih = bersihkan_baris(ln.text)
        if bersih:
            dipakai.append(OcrLine(text=bersih, top=ln.top, height=ln.height, conf=ln.conf))
    if not dipakai:
        return []

    tinggi_khas = median([ln.height for ln in dipakai]) or 1
    ambang_pisah = tinggi_khas * 1.9

    kelompok: list[list[OcrLine]] = [[dipakai[0]]]
    for sebelum, sekarang in zip(dipakai, dipakai[1:]):
        jarak = sekarang.top - (sebelum.top + sebelum.height)
        if jarak > ambang_pisah:
            kelompok.append([sekarang])
        else:
            kelompok[-1].append(sekarang)

    drafts: list[OcrDraft] = []
    for grup in kelompok:
        teks = _sambung(ln.text for ln in grup)
        if len(teks) < MIN_REVIEW_CHARS:
            continue
        rating = next((r for ln in grup if (r := _rating_dari(ln.text))), None)
        drafts.append(
            OcrDraft(
                text=teks,
                rating=rating,
                confidence=sum(ln.conf for ln in grup) / len(grup),
                lines=len(grup),
            )
        )
    return drafts[:MAX_REVIEWS_PER_IMAGE]


def _sambung(potongan) -> str:
    """Gabungkan baris menjadi satu paragraf.

    Baris yang terpotong karena lebar kolom disambung dengan spasi; baris yang memang berakhir
    dengan tanda baca tetap dipisahkan spasi juga - hasilnya satu paragraf yang terbaca wajar
    tanpa menebak-nebak di mana kalimat aslinya berakhir.
    """
    teks = " ".join(p.strip() for p in potongan if p.strip())
    teks = re.sub(r"\s+", " ", teks)
    teks = re.sub(r"\s+([,.!?;:])", r"\1", teks)
    return teks.strip()


# --------------------------------------------------------------------------------------
# Pembacaan gambar
# --------------------------------------------------------------------------------------


def _siapkan_gambar(data: bytes):
    """Grayscale + perbesar. Dua langkah ini yang paling menentukan akurasi pada tangkapan
    layar HP, jauh melebihi pengaturan Tesseract mana pun."""
    from PIL import Image, ImageOps  # noqa: PLC0415

    try:
        gambar = Image.open(io.BytesIO(data))
        gambar.load()
    except Exception as exc:  # format tidak dikenal, berkas rusak
        raise OcrRejected("Berkas gambar tidak dapat dibaca.") from exc

    gambar = ImageOps.exif_transpose(gambar).convert("L")
    if gambar.width < UPSCALE_TARGET_WIDTH:
        skala = min(3.0, UPSCALE_TARGET_WIDTH / max(gambar.width, 1))
        gambar = gambar.resize(
            (int(gambar.width * skala), int(gambar.height * skala)), Image.LANCZOS
        )
    return ImageOps.autocontrast(gambar)


@lru_cache(maxsize=1)
def bahasa_terpakai() -> str:
    """Pilih bahasa yang BENAR-BENAR terpasang.

    Tesseract menolak seluruh permintaan bila salah satu bahasa yang diminta tidak ada - jadi
    meminta "ind+eng" pada mesin tanpa paket Indonesia bukan berarti hasilnya lebih buruk,
    melainkan tidak ada hasil sama sekali. Turun ke bahasa yang tersedia jauh lebih baik
    daripada endpoint yang mati total, dan penurunannya dicatat supaya tidak diam-diam.

    Docker image sudah memasang `tesseract-ocr-ind`; jalur cadangan ini untuk mesin
    pengembang dan pemasangan yang tidak lengkap.
    """
    import pytesseract  # noqa: PLC0415

    diminta = OCR_LANG.split("+")
    try:
        tersedia = set(pytesseract.get_languages(config=""))
    except Exception:  # daftar bahasa tidak dapat dibaca - biarkan Tesseract yang memutuskan
        return OCR_LANG

    dipakai = [b for b in diminta if b in tersedia]
    if not dipakai:
        dipakai = ["eng"] if "eng" in tersedia else sorted(tersedia)[:1]
    if set(dipakai) != set(diminta):
        hilang = sorted(set(diminta) - tersedia)
        log.warning(
            "paket bahasa Tesseract %s tidak terpasang; memakai %s. Kata Indonesia akan lebih "
            "sering salah baca - pasang tesseract-ocr-ind untuk hasil yang benar.",
            "+".join(hilang),
            "+".join(dipakai),
        )
    if not dipakai:
        raise OcrUnavailable("tidak ada paket bahasa Tesseract yang terpasang")
    return "+".join(dipakai)


def _baris_dari_tesseract(gambar) -> list[OcrLine]:
    try:
        import pytesseract  # noqa: PLC0415
        from pytesseract import Output  # noqa: PLC0415
    except ImportError as exc:
        raise OcrUnavailable("pytesseract belum terpasang") from exc

    # Di dalam container biner-nya ada di PATH dan variabel ini tidak perlu diisi. Ia ada untuk
    # mesin pengembang Windows, tempat pemasang menaruh tesseract.exe di Program Files dan
    # PATH-nya baru berlaku setelah sesi dimulai ulang.
    if perintah := os.getenv("TESSERACT_CMD"):
        pytesseract.pytesseract.tesseract_cmd = perintah

    try:
        # `--psm 6` memperlakukan gambar sebagai satu blok teks seragam. Mode bawaan (3)
        # mencoba mendeteksi kolom dan pada tangkapan layar kerap memecah satu ulasan menjadi
        # beberapa kolom semu karena avatar dan ikon di sebelah kiri teks.
        data = pytesseract.image_to_data(
            gambar, lang=bahasa_terpakai(), config="--psm 6", output_type=Output.DICT
        )
    except Exception as exc:
        # pytesseract melempar TesseractNotFoundError maupun galat pemanggilan lain sebagai
        # kelas yang berbeda-beda; semuanya berarti hal yang sama bagi pemanggil.
        raise OcrUnavailable(str(exc)) from exc

    ember: dict[tuple[int, int, int], list[dict]] = {}
    for i, teks in enumerate(data["text"]):
        teks = (teks or "").strip()
        if not teks:
            continue
        try:
            conf = float(data["conf"][i])
        except (TypeError, ValueError):
            conf = -1.0
        if conf < MIN_WORD_CONF:
            continue
        kunci = (data["block_num"][i], data["par_num"][i], data["line_num"][i])
        ember.setdefault(kunci, []).append(
            {
                "text": teks,
                "left": data["left"][i],
                "right": data["left"][i] + data["width"][i],
                "top": data["top"][i],
                "height": data["height"][i],
                "conf": conf,
            }
        )

    baris: list[OcrLine] = []
    for kata in ember.values():
        kata.sort(key=lambda k: k["left"])
        for potongan in _pecah_pada_jurang(kata):
            baris.append(
                OcrLine(
                    text=" ".join(k["text"] for k in potongan),
                    top=min(k["top"] for k in potongan),
                    height=max(k["height"] for k in potongan),
                    conf=sum(k["conf"] for k in potongan) / len(potongan),
                )
            )
    return baris


def _pecah_pada_jurang(kata: list[dict]) -> list[list[dict]]:
    """Pecah satu baris menjadi beberapa potongan pada jarak mendatar yang lebar.

    Tesseract menganggap apa pun yang sebaris sebagai satu baris, sehingga dua tombol yang
    terpisah setengah layar - "Balas" di kiri, "Bermanfaat" di tengah - keluar sebagai satu
    string. Jarak antar-kata di dalam kalimat hanya beberapa piksel; jarak antar-elemen
    antarmuka jauh lebih lebar dari tinggi hurufnya sendiri.
    """
    if len(kata) < 2:
        return [kata]

    tinggi = max(k["height"] for k in kata)
    ambang = tinggi * 1.5

    potongan, sekarang = [], [kata[0]]
    for sebelum, k in zip(kata, kata[1:]):
        if k["left"] - sebelum["right"] > ambang:
            potongan.append(sekarang)
            sekarang = [k]
        else:
            sekarang.append(k)
    potongan.append(sekarang)
    return potongan


def read_screenshot(data: bytes, nama: str = "gambar") -> OcrImageResult:
    """Baca satu tangkapan layar menjadi daftar draf ulasan.

    PII diredaksi DI SINI, bukan nanti saat analisis: begitu teks dikembalikan ke frontend ia
    sudah keluar dari backend, dan nomor telepon yang sempat tampil di layar sudah terlanjur
    ikut (bagian 27.3 - redaksi wajib sebelum data bergerak ke mana pun).
    """
    if not data:
        raise OcrRejected("Berkas gambar kosong.")
    if len(data) > MAX_IMAGE_BYTES:
        raise OcrRejected(
            f"Gambar melebihi {MAX_IMAGE_BYTES // (1024 * 1024)} MB. "
            "Tangkapan layar biasanya jauh di bawah itu."
        )

    gambar = _siapkan_gambar(data)
    baris = _baris_dari_tesseract(gambar)
    drafts = group_lines_into_drafts(baris)

    for d in drafts:
        d.text = redact_personal_data(d.text).text

    return OcrImageResult(image=nama, drafts=drafts)
