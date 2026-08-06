# Panduan Adjudikasi Gold Test Set

Berkas: `gold_adjudication_task.csv` — **302 baris**, bukan 500.

Tiga sumber label sudah disiapkan. Tugas Anda memutuskan yang benar, bukan melabeli dari nol.

| Sumber | Cara dibuat | Status |
| --- | --- | --- |
| `silver_*` | Labeling function leksikon otomatis | sudah ada |
| `llm_*` | Pembacaan semantik per klausa oleh LLM | sudah ada |
| `final_*` | **Keputusan Anda** | perlu diisi |

Hanya baris yang kedua sumbernya **berbeda** (262 baris) plus **40 baris kontrol** yang keduanya
sepakat. Baris kontrol itu bukan basa-basi: kalau kedua sumber kebetulan salah dengan cara yang
sama, hanya pemeriksaan acak yang bisa menangkapnya.

## Cara mengisi

Isi tiga kolom di setiap baris:

- **`final_aspek`** — daftar aspek dipisah koma, atau `-` bila tidak ada aspek sama sekali.
  Klausa tanpa aspek adalah jawaban yang sah ("terima kasih gan").
- **`final_sentimen`** — `positif` / `negatif` / `netral`
- **`final_severity`** — `rendah` / `sedang` / `tinggi`, **hanya** bila sentimennya negatif

Sering kali salah satu kolom `silver_` atau `llm_` sudah benar — cukup salin nilainya. Kolom
`catatan` untuk kasus yang benar-benar meragukan.

Acuan definisi aspek ada di `configs/taxonomy.yaml`.

## Yang sudah diketahui salah — periksa ekstra pada kasus ini

Perbandingan menemukan tiga pola kekeliruan berulang. Mengetahuinya lebih dulu mempercepat kerja:

**1. Kata "enak" memicu aspek rasa, padahal bukan soal makanan.**
Leksikon memasukkan "enak" sebagai penanda `rasa_kualitas_makanan`, sehingga "enak dipakai",
"enak dimainin", dan "enak buat ngegame" ikut terlabeli rasa. Hampir selalu keliru — biasanya
yang dimaksud `kemudahan_penggunaan` atau `kualitas_produk`.

**2. Kata "barang" memicu kualitas produk, padahal kalimatnya soal pengiriman.**
Aturan cadangan leksikon melabeli `kualitas_produk` untuk klausa berisi "barang" bila tidak ada
aspek lain terdeteksi. Akibatnya "barang sudah di terima" terlabeli kualitas produk, padahal itu
`pengiriman` dan sentimennya `netral`, bukan positif.

**3. Variasi kata membuat leksikon meleset.**
"lama banget sampenya" tidak terdeteksi karena leksikon hanya memuat "sampai", bukan "sampenya".
Kasus semacam ini terlabeli tanpa aspek sama sekali.

Pola-pola ini menjelaskan mengapa `kualitas_produk` paling banyak berselisih (98 kasus LLM
menyebut sementara leksikon melewatkannya) dan `rasa_kualitas_makanan` paling banyak dilabeli
berlebihan oleh leksikon (22 kasus).

## Kalau ada dua pelabel

Sisihkan **50 baris yang sama** untuk dikerjakan keduanya, lalu hitung persentase kesepakatan
dan catat di `ml/evaluation/experiment_log.md` (blueprint bagian 26.2 langkah 6).

## Setelah selesai

Simpan sebagai `data/annotation/gold_adjudication_done.csv` dengan kolom yang sama. Baris yang
tidak masuk berkas ini (198 baris yang kedua sumbernya sepakat dan tidak terpilih sebagai
kontrol) memakai label yang disepakati keduanya.

Setelah itu barulah tersedia angka NLP-01 yang layak masuk proposal.

## Catatan kejujuran

Angka kesepakatan antara leksikon dan LLM — aspek 56,4%, sentimen 80,4% — **bukan ukuran
kebenaran**. Keduanya bisa sama-sama keliru. Angka itu hanya menunjukkan berapa banyak baris
yang memerlukan keputusan manusia, dan hasil akhirnya nanti dilaporkan sebagai
**human-adjudicated**, bukan sebagai anotasi manusia dari nol.
