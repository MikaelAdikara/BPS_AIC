"""Potong `Logo.png` menjadi aset web: lambang, lockup, favicon, kartu pratinjau.

Berkas sumbernya sudah PNG bertransparansi 1000x478 - lambang di kiri, kata "Ulasin" di
kanan - jadi tidak ada lagi latar yang perlu dikupas. Versi sebelumnya berangkat dari dua
render JPEG di atas latar putih bergradien dan menghabiskan seratus baris untuk memisahkan
logo dari latarnya lewat rona; seluruh tahap itu hilang bersama sumbernya.

Yang tersisa tinggal tiga keputusan:

    1. **Bayangan jatuhnya dibuang.** Bayangannya asli - gelap dan semi-transparan di kanal
       alpha, bukan putih yang dipanggang seperti sumber lama - jadi sebenarnya ia menumpuk
       benar di atas latar apa pun. Tetap dibuang karena dua hal: pada ikon 30px, halo
       selebar 30px memakan sepertiga bitmapnya sehingga lambangnya mengecil di dalam
       kotaknya sendiri, dan `.brand__mark` sudah memasang `drop-shadow` sendiri yang ikut
       terangkat saat disentuh - bayangan panggang tidak bisa ikut bergerak.
    2. **Pemotongannya per komponen terhubung, bukan per koordinat.** Lambang selalu pulau
       terbesar; huruf-hurufnya pulau-pulau kecil di sebelahnya. Memotong pada koordinat x
       akan salah begitu jarak lambang ke kata digeser sedikit saja di berkas sumbernya.
    3. **Tidak ada varian gelap.** Kata "Ulasin" pada logo baru bergradien biru terang
       (#2F5AC7 sampai #81B0FD); piksel paling gelapnya 3,1:1 di atas kanvas #101218 - di
       atas ambang 3:1 untuk elemen grafis - dan rata-ratanya 5,5:1. Logo lama biru tua
       pekat dan hanya 2,6:1 di sana, karena itu dulu ada `lockup-dark.png` yang mewarnai
       ulang hurufnya. Sumber baru tidak membutuhkannya.

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
SUMBER = ROOT / "Logo.png"

# Piksel dengan alpha di atas ini dianggap badan logo, bukan bayangan maupun tepi lembut.
# Bayangannya tidak pernah melewati 60; badan logonya 255 hampir di mana-mana.
PEKAT = 200

# Lebar cincin tepi yang ikut disimpan di sekeliling badan logo. Dua piksel itu anti-aliasing
# aslinya - dibuang juga, siluetnya jadi bergerigi; disisakan lebih lebar, bayangannya mulai
# ikut terbawa.
TEPI = 2.0


def _tanpa_bayangan(a: np.ndarray) -> np.ndarray:
    """Kosongkan alpha di luar cincin `TEPI` piksel dari badan logo."""
    jarak = ndimage.distance_transform_edt(a[..., 3] <= PEKAT)
    a = a.copy()
    a[..., 3] = np.where(jarak <= TEPI, a[..., 3], 0)
    return a


def _pulau(a: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Pisahkan lambang (pulau terbesar) dari kata (sisanya)."""
    label, jumlah = ndimage.label(a[..., 3] > 8)
    luas = ndimage.sum(a[..., 3] > 8, label, range(1, jumlah + 1))
    lambang = int(np.argmax(luas)) + 1
    return label == lambang, (label != lambang) & (label != 0)


def _potong(a: np.ndarray, topeng: np.ndarray | None = None) -> Image.Image:
    """Ambil bagian bertopeng saja, lalu pangkas ke kotak isinya."""
    if topeng is not None:
        a = a.copy()
        a[..., 3] *= topeng
    gambar = Image.fromarray(a.astype(np.uint8), "RGBA")
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


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    a = _tanpa_bayangan(np.asarray(Image.open(SUMBER).convert("RGBA"), dtype=float))
    topeng_lambang, _ = _pulau(a)

    # Lambangnya di berkas sumber berukuran 260x211. Ukuran terbesar yang benar-benar dipakai
    # di layar adalah 32px, jadi 160px sudah melayani sampai kerapatan piksel 5x. Versi
    # sebelumnya menyimpan 512px seberat 300 KB untuk ikon 30px - itu dibuang, bukan dikecilkan.
    lambang = _kotakkan(_potong(a, topeng_lambang))
    for nama, ukuran in [("mark.png", 160), ("favicon-180.png", 180), ("favicon-32.png", 32)]:
        lambang.resize((ukuran, ukuran), Image.LANCZOS).save(OUT / nama, optimize=True)

    lockup = _potong(a)
    _skala_tinggi(lockup, 180).save(OUT / "lockup.png", optimize=True)

    # Kartu pratinjau tautan. 1200x630 adalah rasio yang dipotong paling sedikit oleh
    # WhatsApp, LinkedIn, maupun X; krem #F1F0E9 diambil dari token --bg supaya kartunya
    # sewarna dengan halaman yang dibukanya.
    kartu = Image.new("RGBA", (1200, 630), (241, 240, 233, 255))
    isi = _skala_tinggi(lockup, 190)
    kartu.alpha_composite(isi, ((1200 - isi.width) // 2, (630 - isi.height) // 2))
    kartu.convert("RGB").save(OUT / "og.png", optimize=True)

    for berkas in sorted(OUT.iterdir()):
        print(f"{berkas.relative_to(ROOT)}  {berkas.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
