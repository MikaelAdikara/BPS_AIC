# Audit klaim pitch — 26 September 2026

Sumber pitch: `../_di-luar-repo/PITCH-DECK-FINAL.md`, v2, dibaca sebagai dokumen klaim.
Audit ini tidak menganggap arahan di deck sebagai perintah menjalankan demo, mengirim Telegram,
atau mengubah data merchant. Bukti terbaru ada di [CHECKPOINT_2.md](CHECKPOINT_2.md).

## Keputusan

**Belum semua klaim pitch terpenuhi atau dapat diverifikasi.** Alur inti sudah ada dan diuji,
tetapi angka historis deck tidak cocok dengan artefak checkout sekarang. Generalisasi engine
masih tertinggal dari narasi demo yang mulus. Jangan mempresentasikan skor development sebagai
jaminan pada input baru, atau sampel marketplace sebagai seluruh ulasan produk.

Kode awal `bfb21ff` / gap-v1.9; perbaikan sesi ini gap-v1.12 / verify-v2.4, belum di-commit.
API localhost saat diperiksa masih melaporkan `bfb21ff`, gap-v1.9 / verify-v2.2. Bukti browser
di bawah berasal dari runtime lama itu; tes kode baru tidak otomatis berarti container sudah baru.

## Daftar klaim

| Klaim dalam pitch | Status | Bukti dan batas |
|---|---|---|
| “Reads every review” | Diperbaiki sebagian, perlu redaksi tepat | Membership kini menerima seluruh ulasan tersimpan, tidak lagi 150 terakhir; teks tidak dipotong 600 karakter. Regresi 164 ulasan dan keluhan di ekor teks lulus. Discovery masih maksimal 45 kandidat dan 600 karakter/kandidat; isu yang tidak ditemukan discovery bisa terlewat. |
| “GPT labels every review against the findings” | Diimplementasikan ketika ada temuan | Membership batch maksimum 50 dan target 24.000 karakter. Setiap ulasan dikirim utuh; ulasan tunggal lebih panjang dikirim sendiri. Batas budget/provider tetap dapat menggagalkan analisis secara terlihat. Tidak berarti semua label benar. |
| “Same input bundle” untuk pembanding app | Diperbaiki | Pembanding generic kini menggunakan seluruh teks dan ulasan, tanpa pemotongan 150/600. Listing masih mengikuti jendela engine 9.000 karakter; jangan menyebut keduanya membaca listing tak terbatas. |
| Counts/statuses/costs berasal dari kode | Terpenuhi dalam cakupan | pipeline.compute_metrics, draft gate, ledger; unit suite. Ketepatan hitungan tidak membuktikan ketepatan model melabeli review. |
| Kutipan verbatim, unit/lokasi/negasi/perangkat diperiksa | Terpenuhi dalam cakupan | test_deciqo_gate_claims, gate_draft, gate_facts, engine_relevance; seluruh suite lulus. Tidak menjamin seluruh klaim bahasa alami benar. |
| “The listing says thick, nine buyers say thin” | Angka spesifik belum terverifikasi | Produk Niks/64 ulasan/snapshot 24 Sep tidak ditemukan pada paket kini; paket Lazada yang tersedia bertanggal 26 Sep. Jangan mengganti sumbernya diam-diam atau membuat ulang sembilan keluhan. |
| 64 reviews, average 3.41, 30 five-star | Tidak terverifikasi pada checkout ini | Workspace browser kini 15 produk/539 review, produk yang tersedia berbeda. Sampel Lazada sengaja memperbanyak review bintang rendah; rata-rata sampel bukan rating seluruh produk. |
| 3 merchant interviews | Bukti eksternal belum ditemukan | Deck menyatakan ini; catatan interview tidak ada di berkas yang diperiksa. Boleh disampaikan sebagai riset tim bila catatan dapat ditunjukkan; bukan pilot, WTP, atau evaluasi model. |
| GPT mengarang 34×24×3 cm pada c01 | Kutipan historis belum terverifikasi | Deck mengacu run/build e73cef5 yang tidak tersedia. Output baseline lain ada, tetapi kutipan tidak boleh dipasangkan dengan provenance run berbeda. |
| 20 cases / 9 invented / 0 careful / 14 held | Tidak didukung artefak saat ini | Repo sekarang 22 development dan 10 holdout. adjudication-first-pass.md yang disebut deck tidak ditemukan. Latest metrics berbasis regex/proxy, bukan invent-spec manual count. |
| 18/19 issues, 29/29 precision, 18/18 routing, 29/40 recall | Historis belum dapat direproduksi | Sediakan arsip build/run tersebut atau gunakan checkpoint baru dengan label denominator/metode. Jangan mencampur angka lintas run. |
| 54 regression tests / 426 tests / test_deciqo_integrity.py | Referensi deck tidak cocok | File integrity itu tidak ditemukan; proteksi tersebar pada gate_claims, gate_facts, gate_draft dan relevansi. Total suite terbaru lebih besar; laporkan log run aktual. |
| Fakta “oke” ditolak | Terverifikasi UI runtime lama dan unit kode baru | Browser benar-benar menampilkan “Enter a measured or confirmed fact.” Redaksi toast berbeda dari deck. Tidak ada fakta disimpan saat uji. |
| Angka tanpa unit ditolak | Terverifikasi UI runtime lama dan unit kode baru | Dengan Unit=No unit, `32 x 24` ditolak: “Choose a unit for this measurement.” Form default cm; pilih No unit sebelum demo penolakan ini. |
| Fakta benar → draft ready for review | Terverifikasi in-process/API tests | test_deciqo_engine_harness, gate_draft, listing_editor. Pada development 12/13, pada holdout 4/6; sebagian kasus tanpa listing memang ditahan. |
| Seller applies; Deciqo does not write store | Terpenuhi pada jalur saat ini | Read-only source connectors; decision record dan UI menjelaskan seller paste sendiri. Applied adalah catatan merchant, bukan bukti listing live berubah. |
| New complaint after action reopens issue | Terverifikasi kode, bukan hasil merchant | Regresi lifecycle pipeline/platform; timestamp setelah action dan bukti isu yang cocok. Tidak berarti perubahan merchant gagal atau penyebab pasti diketahui. |
| Monday decision plan dengan semua alasan | Terverifikasi UI dan unit | Reach, hidden reviews, trend, effort terlihat di Overview. Effort menit adalah konstanta; ranking heuristik, bukan optimum bisnis. |
| Lazada public snapshot, Woo read-only, paste/import | Terpenuhi dengan batas source state | Snapshot bertanggal dan data synthetic ditandai; konektor resmi Tokopedia/Shopee tidak ada. Listing snapshot belum tentu listing saat pembeli membeli. |
| Per-account ledger/monthly AI allowance | Ada dan diuji, kuota opsional | Cached pricing, unknown reservations, server limit, account quota diuji. Account quota hanya ditegakkan bila env DECIQO_ACCOUNT_MONTHLY_AI_USD >0; jangan menyebut allowance aktif tanpa memeriksa konfigurasi deployment. |
| Provider down → automatically rule mode | Terlalu luas | Key rejected/budget exhausted → rules; timeout/incomplete/provider error → analysis failed dan hasil lama dijaga. Deck harus membedakan dua kondisi ini. Evaluator kini tidak menyamarkan failure sebagai sukses tanpa isu. |
| Telegram live | Belum diuji ulang sesi ini | Ada unit metadata/retry/budget; tidak mengirim pesan baru untuk audit ini. Bukti notifikasi lama di UI bukan rehearsal pada build baru. |
| Rp149k, ROI, 62% contribution | Hipotesis/asumsi | Deck sudah memberi label asumsi; bukan entitlement yang ditegakkan, pricing tervalidasi, atau impact terukur. Kurs Rp17.500/USD adalah asumsi perencanaan. |
| 50 products/500 reviews/100 analyses/20 drafts monthly | Belum menjadi paket entitlement | Batas akun dollar AI ada, tetapi ini tidak membuktikan empat kuota paket tersebut diterapkan. Sebut proposed plan; jangan menjanjikan enforced limits yang belum ada. |
| “Two blind raters are scoring them now” | Belum dapat diverifikasi | Blind sheet tersedia; label masih pending. Tidak ada bukti dua penilai sedang bekerja. Katakan independent scoring is pending. |
| “We did not re-score fixes on the same cases” | Bertentangan dengan proses repo | ITERATIONS menyimpan rerun development setelah fix. Redaksi yang benar: regression on development, then a separate first holdout. |

## Perbaikan tambahan karena pitch

`gap-v1.11` menghapus batas membership 150 dan pemotongan review 600 karakter. Batch dibatasi
agar tidak mengirim seluruh katalog dalam satu request; ledger tetap mereservasi biaya setiap call.
Tidak ada jaminan satu review ekstrem muat di context provider; bila gagal, kegagalannya harus
terlihat. Pembanding app juga menerima review utuh. Discovery tetap sampel terbatas dan maksimal
8 isu; scope ini harus masuk Q&A.

Harness sekarang meneruskan provider failure sebagai error. Sebelumnya ia menyimpan error di
hasil tetapi runner bisa menandai output sukses tanpa temuan. Regresi error-path telah ditambahkan.

Pada run gap-v1.11, discovery dan membership memberi label berlawanan pada keluhan powerbank
yang sama, serta checker tidak mengenali bahasa kapasitas rice cooker. gap-v1.12 menambahkan
kelompok kapasitas, memperjelas bahwa label supports relatif ke masalah (bukan klaim listing),
dan menyelesaikan konflik label hanya bila semua span verbatim mendapat verdict kode tegas
yang sama. Span campuran atau tidak pasti tetap tidak dihitung. Regresi kedua arah diuji.

Run development gap-v1.11 menemukan 19/21 isu dan 36/53 bukti, berbeda dari gap-v1.10
21/21 dan 40/53. Perubahan cakupan membership tidak menjelaskan perbedaan kasus kecil ini;
ini bukti ketidakstabilan label, bukan alasan memilih run dengan skor tertinggi untuk pitch.

## Redaksi pengganti yang bisa dipertanggungjawabkan

- Opening/close: **“Deciqo checks saved reviews against the issues it finds, puts the evidence
  next to the listing, and holds drafts that need a fact from the seller.”**
- Architecture: **“Discovery selects candidate reviews. Membership checks every saved review
  against the proposed issues. Code verifies the evidence before counting it.”**
- Evaluation: **“Our development regression improved, but our first ten synthetic holdout
  cases still exposed missed reviews and routing mistakes. Independent human scoring is pending.”**
- Reliability: **“Rejected keys or exhausted budgets switch to labelled rules. Provider errors
  are shown and previous findings are preserved.”**
- Overfitting Q&A: **“We rerun development cases as regressions and keep the failures. We then
  ran a separate synthetic holdout. Once inspected, that holdout is no longer fresh for tuning.”**
- Plan: **“Rp149,000 is proposed pricing. The product/review/analysis/draft allowances are proposed
  package limits; account AI spending can be capped in dollars.”**

## Demo yang dapat diperiksa sekarang

Browser akun demo menampilkan Monday decision plan dan tas laptop synthetic dengan 3/4 review
pendukung, satu tersembunyi pada 5★, kutipan listing, missing-fact form, draft held, dan decision
history. Invalid `oke` dan `32 x 24` tanpa unit benar-benar ditolak. Uji browser hanya memeriksa
penolakan; tidak menyimpan fakta, mark applied, menambah review, atau memicu pesan Telegram.
Bagian save→draft→applied→reopen ditopang tes DB/API terisolasi, belum rehearsal browser penuh
pada build baru. Pastikan hash runtime dan artefak evaluasi cocok sebelum final.

## Yang masih membutuhkan bukti baru

Satu paket merchant berisi listing, review, keputusan, perubahan nyata, dan follow-up;
dua penilai manusia; fresh holdout klasifier dan engine setelah iterasi berikutnya; rehearsal
demo pada build final; verifikasi konfigurasi kuota; artefak asli Niks dan first-pass adjudication
jika angka deck lama ingin dipertahankan. Tidak boleh mengarang bukti untuk memenuhi pitch.

## Hasil verifikasi terakhir — gap-v1.12 / verify-v2.4

| Metrik D | Development terbaru | Holdout yang diuji ulang sebagai regresi |
|---|---|---|
| Temuan emas, before | 21/21 | 9/9 |
| Precision bukti, before | 40/40 | 14/14 |
| Recall bukti, before | 40/53 | 14/20 |
| Routing, before | 21/21 | 9/9 |
| Missing fact held | 13/13 | 5/6 |
| Hold berlebih | 1/3 | 1/1 |
| Ready after fact, menurut matcher isu emas | 11/13 | 3/6 |
| Ada teks draf, after | 12/13 | 4/6 |
| Teks terkena pola terlarang, after | 0/12 | 0/4 |

Sumber: [development](final/pitch-gap-v1.12/report.md) dan
[holdout regression](final/pitch-holdout-regression-v1.12/report.md), output dan manifest di
folder yang sama. Di development, rata-rata satu fase D 16,2 detik dan ~$0,0035. Pada regresi
holdout 14,6 detik dan ~$0,0032. Bukan pengukuran produksi atau jaminan latency.

Run pertama holdout (sebelum diekspos untuk audit) tetap disimpan: temuan 8/9, recall 11/20,
ready 4/6. Run ulang menaikkan discovery tetapi menurunkan ready ke 3/6; jangan menyebutnya
peningkatan menyeluruh. h03 masih berubah antara listing dan quality. Denominator ready
juga memasukkan kasus tanpa listing. Matcher yang memilih satu isu dapat berbeda dari isu
yang diberi fakta ketika model membagi atribut; perlu evaluasi seluruh section oleh manusia.

672 tes backend/integrasi lulus ([log](final/pitch-gap-v1.12/pytest.txt)); 29 tes web, typecheck,
dan build lulus sebelumnya dalam sesi yang sama, tanpa perubahan frontend setelahnya.
Hash file implementasi/evaluator tersimpan di
[source-fingerprints.json](final/pitch-gap-v1.12/source-fingerprints.json).
Seluruh enam run API sesi ini total ~$0,7477 menurut ledger runner.

Perbaikan berada di working tree. Container yang diperiksa di localhost belum diperbarui;
nomor versi dan screenshot pitch tidak boleh mengacu gap-v1.12 sebelum runtime dibangun ulang.
