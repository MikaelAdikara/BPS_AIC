# Panduan Anotasi Gold Test Set

Berkas: `gold_annotation_task.csv` (500 klausa)

Gold test set ini adalah **satu-satunya sumber angka NLP-01 yang boleh masuk proposal**
(ADR-015). Karena itu kualitas anotasi di sini menentukan kredibilitas seluruh klaim model.

## Aturan umum

1. **Labeli apa yang tertulis, bukan yang Anda duga dimaksud.** Kalau klausa tidak cukup
   jelas, isi `catatan_pelabel` dan tetap ambil keputusan terbaik.
2. Satu klausa boleh punya **lebih dari satu aspek**, boleh juga **tidak punya aspek sama
   sekali** (mis. "terima kasih gan"). Klausa tanpa aspek adalah label yang sah, bukan
   kesalahan — biarkan seluruh kolom aspek kosong.
3. Jangan melihat tebakan sistem sebelum melabeli. Berkas ini sengaja tidak memuatnya.

## Kolom aspek — isi `1` jika klausa membicarakan aspek tersebut, biarkan kosong jika tidak

- `asp_kualitas_produk`
- `asp_kesesuaian_deskripsi`
- `asp_harga_value`
- `asp_ukuran_varian`
- `asp_rasa_kualitas_makanan`
- `asp_kemasan`
- `asp_pengiriman`
- `asp_pelayanan_penjual`
- `asp_kelengkapan`
- `asp_keaslian`
- `asp_kemudahan_penggunaan`

Acuan definisi tiap aspek ada di `configs/taxonomy.yaml` (status FROZEN).
Catatan khusus: untuk kategori F&B, `asp_ukuran_varian` dipakai untuk keluhan
**porsi/takaran**; untuk kerajinan, untuk **dimensi produk**.

## Kolom `sentimen` — wajib diisi salah satu

| Nilai | Kapan dipakai |
| --- | --- |
| `positif` | Klausa menyampaikan kepuasan/pujian |
| `negatif` | Klausa menyampaikan keluhan/kekecewaan |
| `netral` | Pernyataan datar tanpa arah jelas, atau sekadar deskripsi/pertanyaan |

Perhatikan **negasi** ("bukan jelek kok" = positif) dan **sarkasme** ("mantap banget nih
ditipu" = negatif). Dua hal ini adalah titik paling sering salah.

## Kolom `severity` — isi HANYA jika sentimen negatif

| Nilai | Kapan dipakai |
| --- | --- |
| `tinggi` | Kerugian nyata bagi pembeli: barang rusak, salah kirim, tidak sampai, palsu |
| `sedang` | Mengganggu tapi masih dapat ditoleransi: pengiriman lambat, kemasan penyok |
| `rendah` | Keluhan ringan/preferensi: warna kurang cerah, harga agak mahal |

## Kualitas anotasi

- Jika lebih dari satu orang melabeli, **sisihkan 50 klausa yang dilabeli semua pelabel**
  untuk menghitung inter-annotator agreement (bagian 26.2 langkah 6). Catat hasilnya di
  `ml/evaluation/experiment_log.md`.
- Simpan hasil sebagai `data/annotation/gold_annotation_done.csv` dengan kolom yang sama.
- Berkas gold ini **boleh di-commit** (ukurannya kecil dan esensial untuk reproducibility
  evaluasi), berbeda dari data latih yang tidak di-commit.
