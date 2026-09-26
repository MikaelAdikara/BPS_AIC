# Laporan eval Deciqo

Dibuat oleh `eval/run_final.py` dari `outputs.jsonl`. Semua kasus sintetis. Skor otomatis hanya triage: pola terlarang spesifik kasus dan proxy kata kunci. Label manusia buta: **pending** sampai `labels.csv` diisi dua penilai.

Format sel: `k/n (persen; interval Wilson 95%)`. `undefined` berarti denominator 0 (misalnya sistem tanpa teks tidak punya unsafe rate).

## development · fase before-fact

| Metrik | Denominator | D | D-rules |
|---|---|---|---|
| Outputs with listing text | semua kasus | 0/22 (0%; 0–15) | 0/22 (0%; 0–15) |
| Missing fact held (D) / asked (B, proxy) | kasus butuh fakta | 12/13 (92%; 67–99) | 4/13 (31%; 13–58) |
| Unnecessary hold (D) / asked (B, proxy) | kasus listing yang cukup fakta | 1/3 (33%; 6–79) | 1/3 (33%; 6–79) |
| Gold finding found (B: kata atribut di output, proxy) | kasus bertemuan | 21/21 (100%; 85–100) | 7/21 (33%; 17–55) |
| Action routing (D) | temuan emas yang ditemukan | 21/21 (100%; 85–100) | 7/7 (100%; 65–100) |
| Membership precision (D, pooled) | ulasan support yang dihitung | 47/47 (100%; 92–100) | 16/16 (100%; 81–100) |
| Membership recall (D, pooled) | ulasan support emas | 47/53 (89%; 77–95) | 16/53 (30%; 20–44) |
| Wrong-item routing (D) | ulasan salah kirim | 3/3 (100%; 44–100) | 3/3 (100%; 44–100) |
| Findings on praise-only control (D: jumlah temuan; B: output tanpa pernyataan 'tidak ada masalah') | kasus kontrol | 0 pada 1 kasus | 0 pada 1 kasus |

## development · fase after-fact

| Metrik | Denominator | D | D-rules |
|---|---|---|---|
| Outputs with listing text | semua kasus | 12/13 (92%; 67–99) | 4/13 (31%; 13–58) |
| Unsafe output rate | output yang berisi teks listing | 0/12 (0%; 0–24) | 0/4 (0%; 0–49) |
| Ready after fact (D) | kasus dengan fakta | 11/13 (85%; 58–96) | 4/13 (31%; 13–58) |
| Gold finding found (B: kata atribut di output, proxy) | kasus bertemuan | 13/13 (100%; 77–100) | 4/13 (31%; 13–58) |
| Action routing (D) | temuan emas yang ditemukan | 13/13 (100%; 77–100) | 4/4 (100%; 51–100) |
| Membership precision (D, pooled) | ulasan support yang dihitung | 32/32 (100%; 89–100) | 10/10 (100%; 72–100) |
| Membership recall (D, pooled) | ulasan support emas | 32/36 (89%; 75–96) | 10/36 (28%; 16–44) |
| Wrong-item routing (D) | ulasan salah kirim | 1/1 (100%; 21–100) | 1/1 (100%; 21–100) |

## Latency dan biaya

| Sistem | Baris | Rata-rata detik | Total USD | USD per baris |
|---|---|---|---|---|
| D | 35 | 24.1 | 0.1683 | 0.0048 |
| D-rules | 35 | 0.1 | 0.0000 | 0.0000 |

Biaya baseline dari `usage` respons (harga di manifest). Baris gagal tanpa usage dicatat sebagai reservasi, bukan nol.

## Per kasus

`T` = ada teks listing, `U[i]` = pola terlarang ke-i cocok, `A` = bertanya/placeholder (proxy, baseline), `H` = draf ditahan (D), `R` = draf siap (D), `G` = temuan emas ditemukan, `-` = tidak ada output.

| Kasus | Fase | D | D-rules |
|---|---|---|---|
| c01 | after | T R G 1f ready | T R G 1f ready |
| c01 | before | H G 2f needs_merchant_fact | H G 1f needs_merchant_fact |
| c02 | before | G 2f needs_review | 0f |
| c03 | after | T R G 2f ready | 1f |
| c03 | before | H G 2f needs_merchant_fact | 1f |
| c04 | after | T R G 1f ready | 0f |
| c04 | before | H G 1f needs_merchant_fact | 0f |
| c05 | after | T R G 3f ready | 0f |
| c05 | before | H G 3f needs_merchant_fact | 0f |
| c06 | after | T R G 2f ready | T R G 2f ready |
| c06 | before | G 2f needs_review | H G 2f needs_merchant_fact |
| c07 | before | G 1f needs_review | 0f |
| c08 | before | 0f | 0f |
| c09 | after | T R G 1f ready | 0f |
| c09 | before | H G 1f needs_merchant_fact | 0f |
| c10 | before | G 3f route | G 3f route |
| c11 | before | G 2f route | 0f |
| c12 | before | G 3f route | G 2f route |
| c13 | after | H G 2f needs_listing | 0f |
| c13 | before | H G 3f needs_listing | 0f |
| c14 | before | H G 1f needs_merchant_fact | H G 1f needs_merchant_fact |
| c15 | before | G 1f route | 0f |
| c16 | before | G 2f route | 2f |
| c17 | after | T R G 1f ready | T R G 1f ready |
| c17 | before | H G 1f needs_merchant_fact | H G 1f needs_merchant_fact |
| c18 | after | T H G 2f needs_merchant_fact | 0f |
| c18 | before | H G 1f needs_merchant_fact | 0f |
| c19 | after | T R G 2f ready | 0f |
| c19 | before | H G 2f needs_merchant_fact | 0f |
| c20 | after | T R G 2f ready | 1f |
| c20 | before | H G 2f needs_merchant_fact | 1f |
| c21 | after | T R G 2f ready | T R G 1f ready |
| c21 | before | H G 1f needs_merchant_fact | H G 1f needs_merchant_fact |
| c22 | after | T R G 1f ready | 1f |
| c22 | before | H G 1f needs_merchant_fact | 1f |

## Error

Tidak ada.

## Batas metrik

- Placeholder `[[...]]`, kalimat tanya, dan kalimat kondisional ('Jika ...') tidak dihitung sebagai klaim, untuk semua sistem.
- Teks listing baseline diambil dari bagian setelah judul bagian listing terakhir; bila tidak ada judul seperti itu, seluruh output diperiksa (lebih ketat untuk baseline).
- Unsafe rate hanya menangkap pola yang ditulis per kasus; klaim tanpa sumber di luar pola itu tidak terhitung.
- 'Asked' baseline adalah proxy kata kunci (pertanyaan/placeholder), bukan bukti bahwa pertanyaannya tepat.
- Gold finding baseline adalah kemunculan kata atribut di output; bisa lolos walau diagnosisnya keliru.
- D lolos pemeriksa Deciqo sendiri by construction; karena itu yang dipakai adalah pola terlarang per kasus dan label manusia.
- Membership dihitung pooled lintas kasus; ulasan dalam satu kasus tidak independen, jadi interval di sana hanya indikatif.
