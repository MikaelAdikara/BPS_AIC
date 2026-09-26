# Data marketplace

Paket data yang dibaca aplikasi saat seed akun demo dan saat tombol "Load demo pack" ditekan.
Setiap berkas menyebut asal data (`data_origin`) dan tanggal ambil (`captured_at`); aplikasi
menampilkan keduanya di setiap produk.

| Berkas | Channel | Asal (`data_origin`) | Tanggal ambil | Isi | Yang dihapus |
|---|---|---|---|---|---|
| `tokopedia-2019.json` | Tokopedia | `public_dataset` | dataset 2019 | 6 produk, 271 ulasan dari *Tokopedia Product Reviews 2019* (HuggingFace `farhamu/tokopedia-product-reviews-2019`, Apache-2.0). Tanpa teks listing dan tanpa tanggal ulasan | Tidak ada identitas reviewer di dataset; teks diredaksi |
| `shopee-team.json` | Shopee | `team_collected` | Okt 2025 – Agu 2026 | 2 listing, 66 ulasan nyata yang dikumpulkan tim (`data/samples/demo_shopee_asli.csv`), tidak disaring | Nama akun, foto profil, dan ukuran tubuh pembeli tidak disimpan; nama produk dianonimkan |
| `tiktok-sintetis.json` | TikTok Shop | `synthetic` | tanggal build | 1 produk + listing, 6 ulasan ditulis tim | – |
| `blibli-sintetis.json` | Blibli | `synthetic` | tanggal build | 1 produk + listing, 6 ulasan ditulis tim | – |
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

## Cara membangun ulang paket channel

`python scripts/build_channel_packs.py` (butuh `data/raw/tokopedia_reviews_2019`, diunduh
`scripts/download_datasets.py`). Produk Tokopedia dipilih dengan aturan tetap: minimal 25 ulasan,
porsi ulasan bintang 1–3 tertinggi, kategori elektronik/handphone/fashion; 60 ulasan pertama per
produk menurut urutan dataset, tanpa menyaring bintang.
