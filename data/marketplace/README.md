# Data marketplace

Paket data yang dibaca aplikasi saat seed akun demo dan saat tombol "Load demo pack" ditekan.
Setiap berkas menyebut asal data (`data_origin`) dan tanggal ambil (`captured_at`); aplikasi
menampilkan keduanya di setiap produk. `sampling_kind` menyatakan cara ulasan diambil dan menentukan
angka pembeli terdampak di rencana keputusan (lihat bawah).

| Berkas | Channel | Asal (`data_origin`) | Tanggal ambil | `sampling_kind` | Isi | Yang dihapus |
|---|---|---|---|---|---|---|
| `tokopedia-2019.json` | Tokopedia | `public_dataset` | dataset 2019 | `unknown` | 6 produk, 271 ulasan dari *Tokopedia Product Reviews 2019* (HuggingFace `farhamu/tokopedia-product-reviews-2019`, Apache-2.0), plus jumlah terjual. Tanpa teks listing dan tanpa tanggal ulasan | Tidak ada identitas reviewer di dataset; teks diredaksi |
| `tokopedia-prdect.json` | Tokopedia | `public_dataset` | terbit 2022 | `skewed` | 23 produk, 355 ulasan dari *PRDECT-ID* (Sutoyo dkk., *Data in Brief*, 2022; HuggingFace `ZakyF/PRDECT-ID`, **CC-BY-4.0, atribusi wajib**), plus harga dan jumlah terjual. Tanpa teks listing dan tanpa tanggal ulasan | Tidak ada identitas reviewer di dataset; lokasi toko tidak disalin; teks diredaksi |
| `shopee-team.json` | Shopee | `team_collected` | Okt 2025 – Agu 2026 | `unknown` | 2 listing, 66 ulasan nyata yang dikumpulkan tim (`data/samples/demo_shopee_asli.csv`), tidak disaring | Nama akun, foto profil, dan ukuran tubuh pembeli tidak disimpan; nama produk dianonimkan |
| `tiktok-sintetis.json` | TikTok Shop | `synthetic` | tanggal build | `complete` | 2 produk + listing + jumlah terjual, 14 ulasan ditulis tim | – |
| `blibli-sintetis.json` | Blibli | `synthetic` | tanggal build | `complete` | 2 produk + listing + jumlah terjual, 13 ulasan ditulis tim | – |
| `lazada-snapshot-2026-09-26.json` | Lazada (lazada.co.id) | `public_snapshot` | 26 Sep 2026 | `skewed` | 10 produk publik (tas laptop, powerbank, kemeja pria, earphone TWS, sneakers, casing iPhone), 517 ulasan: listing, spesifikasi, varian, ulasan | Nama dan profil reviewer tidak diambil; nomor telepon, email, dan handle di teks ulasan diredaksi |

## Pembeli terdampak dan `sampling_kind`

Rencana keputusan hanya menyebut angka pasti: **"setidaknya N pembeli menulis ini, dari M unit
terjual"**, dengan N = ulasan yang menyebut isu. Proyeksi batas bawah Wilson 95% × unit terjual hanya
muncul bila isu dilaporkan minimal dua ulasan dan `sampling_kind` = `complete` (semua ulasan sumber, mis. sinkron penuh Woo atau toko
sintetis) atau `random`, dan diberi label asumsi "pengulas mewakili pembeli". `skewed` (bintang
rendah sengaja diperbanyak: Lazada, PRDECT-ID) dan `unknown` tidak pernah diproyeksikan.

PRDECT-ID memuat 1.832 ulasan bintang 1 dari 5.400, padahal rating listing-nya 4,7–4,9, jadi
datasetnya jelas memperbanyak ulasan negatif. Tanggal pengumpulannya tidak dipublikasikan; 2022 adalah
tahun terbit.

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

`python scripts/build_channel_packs.py` (butuh `data/raw/tokopedia_reviews_2019` dan
`data/raw/prdect_id`, diunduh `scripts/download_datasets.py`). Produk dipilih dengan aturan tetap:

- **Tokopedia 2019:** minimal 25 ulasan, porsi ulasan bintang 1–3 tertinggi, kategori
  elektronik/handphone/fashion; 60 ulasan pertama per produk menurut urutan dataset, tanpa menyaring
  bintang. Jumlah terjual memakai penghitung Tokopedia yang dibulatkan ke bawah ("2,9rb" → 2.900).
- **PRDECT-ID:** minimal 10 ulasan dan harga minimal Rp10.000 (di bawahnya item tambahan seperti dus
  atau bubble wrap), diurutkan menurut jumlah ulasan bintang 1–3, paling banyak 2 produk per kategori;
  semua ulasan produk itu di dataset.
