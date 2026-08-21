"""Ubah dua berkas logo JPEG menjadi aset web bertransparansi.

Logonya dikirim sebagai render JPEG 2048x2048 di atas latar putih bergradien - bentuk yang
tidak bisa dipakai langsung. Latar putihnya akan terbaca sebagai kotak terang begitu tema
gelap dinyalakan, dan berkas 1,4 MB terlalu besar untuk ikon 30px di bilah navigasi.

Cara memisahkan logo dari latarnya:

    1. Latar JPEG-nya bukan satu warna rata melainkan gradien halus, jadi ambang global
       tidak bisa dipakai. Gradiennya diperkirakan lebih dulu dengan mencocokkan polinomial
       kuadratik pada piksel tepi gambar - daerah yang dijamin latar.
    2. Piksel dipisahkan dari latar berdasarkan RONA, bukan kecerahan. Kecerahan sempat
       dipakai dan membawa serta bayangan jatuhnya: bayangan di dekat logo sama gelapnya
       dengan bagian logo yang paling pucat (keduanya sekitar 20-30 tingkat di bawah latar),
       jadi tidak ada satu ambang kecerahan pun yang memisahkan keduanya. Rona memisahkannya
       telak - bayangan itu kelabu netral (terukur 3-6), seluruh bagian logo kebiruan (17-29).
    3. Lubang di dalam siluet ditutup (`binary_fill_holes`), sehingga bagian dalam lensa yang
       memang berwarna terang tetap ikut terbawa alih-alih menjadi lubang tembus pandang.
    4. Hanya komponen terbesar yang disimpan; sisanya bintik derau JPEG.

Bayangan jatuhnya sengaja DIBUANG - lihat langkah 2. Bayangan yang ikut terbawa akan menjadi
halo kelabu yang terlihat kotor di atas permukaan gelap.

Tepinya diperlakukan khusus. Piksel paling luar siluet adalah campuran JPEG antara logo dan
latar putihnya; dipotong tegak lurus, campuran itu menjadi pinggiran putih bergerigi yang baru
kelihatan setelah tema gelap menyala. Karena itu siluetnya dikikis dua piksel lebih dulu, lalu
alpha di sisa tepinya dibuat mengikuti seberapa jauh piksel itu dari latar - bukan 0 atau 255.
Bagian dalam tetap dipaksa pekat lewat siluet yang sudah dikikis lebih dalam, supaya isi lensa
yang memang berwarna terang tidak ikut memudar.

Varian gelap dibuat dengan mewarnai ulang HANYA kata "Ulasin" - biru tuanya 2,6:1 di atas
kanvas gelap, di bawah ambang WCAG AA. Lambangnya tidak disentuh: bentuknya sudah terbaca
di kedua tema. Pemisahan lambang dari huruf memakai komponen terhubung, bukan koordinat
potong: huruf adalah pulau-pulau tersendiri, dan lambang selalu pulau terbesar.

Pemakaian:
    python scripts/build_brand_assets.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "apps" / "web" / "public" / "brand"

SUMBER_LAMBANG = ROOT / "Logo only.jpeg"
SUMBER_LOCKUP = ROOT / "Logo with Name.jpeg"

# Ambang rona. Latar dan bayangan terukur di bawah 6, bagian logo yang paling pucat di atas
# 17, jadi 10 berada di tengah jurangnya.
AMBANG = 10.0


def _perkiraan_latar(a: np.ndarray) -> np.ndarray:
    """Perkirakan gradien latar dengan polinomial kuadratik yang dicocokkan pada tepi gambar."""
    h, w, _ = a.shape
    ys, xs = np.mgrid[0:h, 0:w]
    yn, xn = ys / h, xs / w
    basis = np.stack([np.ones_like(yn), yn, xn, yn * xn, yn**2, xn**2], axis=-1)

    tebal = int(min(h, w) * 0.04)
    tepi = np.zeros((h, w), dtype=bool)
    tepi[:tebal, :] = tepi[-tebal:, :] = True
    tepi[:, :tebal] = tepi[:, -tebal:] = True

    latar = np.empty_like(a)
    for c in range(3):
        koef, *_ = np.linalg.lstsq(basis[tepi], a[..., c][tepi], rcond=None)
        latar[..., c] = basis @ koef
    return latar


def _alpha(path: Path) -> Image.Image:
    """Baca JPEG, buang latarnya, kembalikan RGBA yang sudah dipangkas ke kotak isi."""
    a = np.asarray(Image.open(path).convert("RGB"), dtype=float)
    latar = _perkiraan_latar(a)

    # Rona diukur setelah kecerahan masing-masing piksel dinetralkan, supaya yang tersisa murni
    # perbedaan warna - itulah yang membedakan biru pucat dari abu-abu pucat. Sedikit blur
    # dipasang sebelum pengambangan: tanpanya derau blok JPEG membuat garis tepinya bergerigi,
    # dan gerigi itu baru kelihatan setelah temanya gelap.
    rona = np.abs(
        (a - a.mean(axis=2, keepdims=True)) - (latar - latar.mean(axis=2, keepdims=True))
    ).mean(axis=2)
    selisih = ndimage.gaussian_filter(rona, sigma=1.5)

    siluet = ndimage.binary_fill_holes(selisih > AMBANG)
    label, jumlah = ndimage.label(siluet)
    if jumlah > 1:
        # Lockup punya dua komponen sah - lambang dan tiap huruf. Ambang luasnya dipatok
        # relatif terhadap komponen terbesar supaya huruf "i" bertahan dan bintik tidak.
        luas = ndimage.sum(siluet, label, range(1, jumlah + 1))
        siluet = np.isin(label, np.nonzero(luas > luas.max() * 0.001)[0] + 1)

    siluet = ndimage.binary_erosion(siluet, iterations=2)
    inti = ndimage.binary_erosion(siluet, iterations=4)
    tepi = np.clip((selisih - 7.0) / 6.0, 0.0, 1.0)
    alpha = np.where(siluet, np.maximum(tepi, inti.astype(float)), 0.0)

    rgba = np.dstack([a, alpha * 255]).astype(np.uint8)
    gambar = Image.fromarray(rgba, "RGBA")
    return gambar.crop(gambar.getbbox())


def _kotakkan(im: Image.Image) -> Image.Image:
    """Taruh gambar di tengah kanvas persegi, supaya `width == height` di CSS selalu benar."""
    sisi = max(im.size)
    kanvas = Image.new("RGBA", (sisi, sisi), (0, 0, 0, 0))
    kanvas.paste(im, ((sisi - im.width) // 2, (sisi - im.height) // 2))
    return kanvas


def _skala_tinggi(im: Image.Image, tinggi: int) -> Image.Image:
    lebar = round(im.width * tinggi / im.height)
    return im.resize((lebar, tinggi), Image.LANCZOS)


def _wordmark_terang(im: Image.Image) -> Image.Image:
    """Cerahkan kata "Ulasin" untuk dipakai di atas permukaan gelap.

    Lambang dipisahkan dari huruf lewat komponen terhubung. Memotong pada koordinat x sempat
    dicoba dan salah sasaran: celah kolom terlebar ternyata jatuh di antara dua huruf, bukan
    di antara lambang dan kata, sehingga sebagian kata ikut tertinggal gelap.
    """
    a = np.asarray(im).astype(float)

    label, jumlah = ndimage.label(a[..., 3] > 8)
    luas = ndimage.sum(a[..., 3] > 8, label, range(1, jumlah + 1))
    lambang = int(np.argmax(luas)) + 1
    sisi_kata = (label != lambang) & (label != 0)

    # #A8C1FF - biru terang yang sama dipakai token --blue-dark pada tema gelap, jadi kata
    # ini sewarna dengan tautan dan angka di sekitarnya, bukan biru keempat yang berdiri
    # sendiri. Rasio kontrasnya 8,7:1 di atas kanvas #101218.
    target = np.array([168.0, 193.0, 255.0])
    lum = a[..., :3].mean(axis=2)
    # Semakin gelap piksel aslinya, semakin penuh warna barunya. Piksel tepi yang setengah
    # pudar ikut memudar juga, sehingga anti-aliasing hurufnya tidak menjadi pinggiran kasar.
    bobot = np.clip((200.0 - lum) / 150.0, 0.0, 1.0)[..., None] * sisi_kata[..., None]
    a[..., :3] = a[..., :3] * (1 - bobot) + target * bobot
    return Image.fromarray(a.astype(np.uint8), "RGBA")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    lambang = _kotakkan(_alpha(SUMBER_LAMBANG))
    for nama, ukuran in [("mark-512.png", 512), ("mark.png", 256), ("favicon-180.png", 180), ("favicon-32.png", 32)]:
        lambang.resize((ukuran, ukuran), Image.LANCZOS).save(OUT / nama, optimize=True)

    lockup = _alpha(SUMBER_LOCKUP)
    _skala_tinggi(lockup, 180).save(OUT / "lockup.png", optimize=True)
    _skala_tinggi(_wordmark_terang(lockup), 180).save(OUT / "lockup-dark.png", optimize=True)

    # Kartu pratinjau tautan. 1200x630 adalah rasio yang dipotong paling sedikit oleh
    # WhatsApp, LinkedIn, maupun X; krem #F1F0E9 diambil dari token --bg supaya kartunya
    # sewarna dengan halaman yang dibukanya.
    kartu = Image.new("RGBA", (1200, 630), (241, 240, 233, 255))
    isi = _skala_tinggi(lockup, 200)
    kartu.alpha_composite(isi, ((1200 - isi.width) // 2, (630 - isi.height) // 2))
    kartu.convert("RGB").save(OUT / "og.png", optimize=True)

    for berkas in sorted(OUT.iterdir()):
        print(f"{berkas.relative_to(ROOT)}  {berkas.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
