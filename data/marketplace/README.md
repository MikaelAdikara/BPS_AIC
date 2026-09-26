# Data marketplace

Paket data yang dibaca aplikasi saat seed akun demo dan saat tombol "Load demo pack" ditekan.
Setiap berkas menyebut asal data (`data_origin`) dan tanggal ambil (`captured_at`); aplikasi
menampilkan keduanya di setiap produk.

| Berkas | Channel | Asal (`data_origin`) | Tanggal ambil | Isi | Yang dihapus |
|---|---|---|---|---|---|
| `lazada-snapshot-2026-09-26.json` | Lazada (lazada.co.id) | `public_snapshot` | 26 Sep 2026 | 11 produk publik (tas laptop, powerbank, kemeja pria, earphone TWS, sneakers, casing iPhone): listing, spesifikasi, varian, ulasan | Nama dan profil reviewer tidak diambil; nomor telepon, email, dan handle di teks ulasan diredaksi |

## Cara pengambilan Lazada

Halaman produk publik diambil lewat actor Apify `lergassy/lazada-scraper` (bayar per hasil, batas
biaya per run) dengan `scripts/lazada_snapshot.py`. Pemilihan produk: hasil pencarian per kata kunci,
diurutkan menurut jumlah ulasan.

**Sampel ulasan tidak mewakili distribusi bintang produk.** Per produk berisi 30 ulasan terbaru
ditambah hingga 10 ulasan masing-masing untuk bintang 1, 2, dan 3. Ulasan terbaru hampir seluruhnya
bintang 5, sehingga tanpa tambahan itu keluhan nyata hampir tidak terlihat. Hitungan di aplikasi
("N dari M ulasan tersimpan") selalu merujuk pada ulasan yang tersimpan ini, bukan seluruh pembeli.

Listing di snapshot adalah listing pada tanggal ambil, belum tentu listing saat pembeli membeli.
