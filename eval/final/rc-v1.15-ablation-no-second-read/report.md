# Laporan eval Deciqo

Dibuat oleh `eval/run_final.py` dari `outputs.jsonl`. Semua kasus sintetis. Skor otomatis hanya triage: pola terlarang spesifik kasus dan proxy kata kunci. Label manusia buta: **pending** sampai `labels.csv` diisi dua penilai.

Format sel: `k/n (persen; interval Wilson 95%)`. `undefined` berarti denominator 0 (misalnya sistem tanpa teks tidak punya unsafe rate).

## development · fase before-fact

| Metrik | Denominator | D |
|---|---|---|
| Outputs with listing text | semua kasus | 0/22 (0%; 0–15) |
| Missing fact held (D) / asked (B, proxy) | kasus butuh fakta | 13/13 (100%; 77–100) |
| Unnecessary hold (D) / asked (B, proxy) | kasus listing yang cukup fakta | 1/3 (33%; 6–79) |
| Gold finding found (B: kata atribut di output, proxy) | kasus bertemuan | 21/21 (100%; 85–100) |
| Action routing (D) | temuan emas yang ditemukan | 21/21 (100%; 85–100) |
| Membership precision (D, pooled) | ulasan support yang dihitung | 40/40 (100%; 91–100) |
| Membership recall (D, pooled) | ulasan support emas | 40/53 (75%; 62–85) |
| Wrong-item routing (D) | ulasan salah kirim | 3/3 (100%; 44–100) |
| Findings on praise-only control (D: jumlah temuan; B: output tanpa pernyataan 'tidak ada masalah') | kasus kontrol | 0 pada 1 kasus |

## development · fase after-fact

| Metrik | Denominator | D |
|---|---|---|
| Outputs with listing text | semua kasus | 11/13 (85%; 58–96) |
| Unsafe output rate | output yang berisi teks listing | 0/11 (0%; 0–26) |
| Ready after fact (D) | kasus dengan fakta | 10/13 (77%; 50–92) |
| Gold finding found (B: kata atribut di output, proxy) | kasus bertemuan | 13/13 (100%; 77–100) |
| Action routing (D) | temuan emas yang ditemukan | 12/13 (92%; 67–99) |
| Membership precision (D, pooled) | ulasan support yang dihitung | 24/25 (96%; 80–99) |
| Membership recall (D, pooled) | ulasan support emas | 24/36 (67%; 50–80) |
| Wrong-item routing (D) | ulasan salah kirim | 1/1 (100%; 21–100) |

## holdout · fase before-fact

| Metrik | Denominator | D |
|---|---|---|
| Outputs with listing text | semua kasus | 0/40 (0%; 0–9) |
| Missing fact held (D) / asked (B, proxy) | kasus butuh fakta | 21/24 (88%; 69–96) |
| Unnecessary hold (D) / asked (B, proxy) | kasus listing yang cukup fakta | 3/4 (75%; 30–95) |
| Gold finding found (B: kata atribut di output, proxy) | kasus bertemuan | 35/36 (97%; 86–100) |
| Action routing (D) | temuan emas yang ditemukan | 33/35 (94%; 81–98) |
| Membership precision (D, pooled) | ulasan support yang dihitung | 70/70 (100%; 95–100) |
| Membership recall (D, pooled) | ulasan support emas | 70/125 (56%; 47–64) |
| Wrong-item routing (D) | ulasan salah kirim | 8/8 (100%; 68–100) |
| Findings on praise-only control (D: jumlah temuan; B: output tanpa pernyataan 'tidak ada masalah') | kasus kontrol | 1 pada 4 kasus |

## holdout · fase after-fact

| Metrik | Denominator | D |
|---|---|---|
| Outputs with listing text | semua kasus | 18/24 (75%; 55–88) |
| Unsafe output rate | output yang berisi teks listing | 0/18 (0%; 0–18) |
| Ready after fact (D) | kasus dengan fakta | 17/24 (71%; 51–85) |
| Gold finding found (B: kata atribut di output, proxy) | kasus bertemuan | 22/24 (92%; 74–98) |
| Action routing (D) | temuan emas yang ditemukan | 20/22 (91%; 72–97) |
| Membership precision (D, pooled) | ulasan support yang dihitung | 48/49 (98%; 89–100) |
| Membership recall (D, pooled) | ulasan support emas | 48/89 (54%; 44–64) |
| Wrong-item routing (D) | ulasan salah kirim | 7/7 (100%; 65–100) |

## Latency dan biaya

| Sistem | Baris | Rata-rata detik | Total USD | USD per baris |
|---|---|---|---|---|
| D | 99 | 18.0 | 0.3863 | 0.0039 |

Biaya baseline dari `usage` respons (harga di manifest). Baris gagal tanpa usage dicatat sebagai reservasi, bukan nol.

## Per kasus

`T` = ada teks listing, `U[i]` = pola terlarang ke-i cocok, `A` = bertanya/placeholder (proxy, baseline), `H` = draf ditahan (D), `R` = draf siap (D), `G` = temuan emas ditemukan, `-` = tidak ada output.

| Kasus | Fase | D |
|---|---|---|
| c01 | after | G 2f blocked |
| c01 | before | H G 2f needs_merchant_fact |
| c02 | before | G 1f needs_review |
| c03 | after | T R G 2f ready |
| c03 | before | H G 2f needs_merchant_fact |
| c04 | after | T R G 1f ready |
| c04 | before | H G 1f needs_merchant_fact |
| c05 | after | T R G 3f ready |
| c05 | before | H G 2f needs_merchant_fact |
| c06 | after | T G 2f route |
| c06 | before | H G 2f needs_merchant_fact |
| c07 | before | G 1f needs_review |
| c08 | before | 0f |
| c09 | after | T R G 1f ready |
| c09 | before | H G 1f needs_merchant_fact |
| c10 | before | G 3f route |
| c11 | before | G 2f route |
| c12 | before | G 3f route |
| c13 | after | H G 2f needs_listing |
| c13 | before | H G 3f needs_listing |
| c14 | before | H G 1f needs_merchant_fact |
| c15 | before | G 1f route |
| c16 | before | G 2f route |
| c17 | after | T R G 1f ready |
| c17 | before | H G 1f needs_merchant_fact |
| c18 | after | T R G 1f ready |
| c18 | before | H G 1f needs_merchant_fact |
| c19 | after | T R G 2f ready |
| c19 | before | H G 2f needs_merchant_fact |
| c20 | after | T R G 1f ready |
| c20 | before | H G 2f needs_merchant_fact |
| c21 | after | T R G 1f ready |
| c21 | before | H G 1f needs_merchant_fact |
| c22 | after | T R G 1f ready |
| c22 | before | H G 1f needs_merchant_fact |
| h01 | after | T R G 2f ready |
| h01 | before | H G 2f needs_merchant_fact |
| h02 | before | H G 1f needs_merchant_fact |
| h03 | after | G 1f route |
| h03 | before | G 1f route |
| h04 | after | T R G 2f ready |
| h04 | before | H G 2f needs_merchant_fact |
| h05 | after | 0f |
| h05 | before | H G 2f needs_merchant_fact |
| h06 | after | T R G 2f ready |
| h06 | before | H G 3f needs_merchant_fact |
| h07 | before | G 1f route |
| h08 | before | G 1f route |
| h09 | after | G 2f route |
| h09 | before | H G 2f needs_listing |
| h10 | before | 0f |
| h11 | after | T R G 3f ready |
| h11 | before | H G 3f needs_merchant_fact |
| h12 | before | G 2f needs_review |
| h13 | after | 1f |
| h13 | before | 1f |
| h14 | after | T R G 2f ready |
| h14 | before | H G 2f needs_merchant_fact |
| h15 | after | T R G 1f ready |
| h15 | before | H G 2f needs_merchant_fact |
| h16 | after | T R G 2f ready |
| h16 | before | G 4f route |
| h17 | before | G 2f route |
| h18 | after | T R G 3f ready |
| h18 | before | H G 2f needs_merchant_fact |
| h19 | after | H G 2f needs_listing |
| h19 | before | H G 2f needs_listing |
| h20 | before | 1f |
| h21 | after | T R G 5f ready |
| h21 | before | H G 6f needs_merchant_fact |
| h22 | before | G 2f route |
| h23 | after | T R G 2f ready |
| h23 | before | H G 2f needs_merchant_fact |
| h24 | after | T R G 1f ready |
| h24 | before | H G 1f needs_merchant_fact |
| h25 | before | H G 2f needs_merchant_fact |
| h26 | after | T H G 3f needs_merchant_fact |
| h26 | before | H G 3f needs_merchant_fact |
| h27 | after | T R G 1f ready |
| h27 | before | H G 2f needs_merchant_fact |
| h28 | before | G 1f route |
| h29 | before | 0f |
| h30 | before | G 3f route |
| h31 | after | T R G 2f ready |
| h31 | before | H G 3f needs_merchant_fact |
| h32 | before | G 3f route |
| h33 | before | H G 1f needs_merchant_fact |
| h34 | after | T R G 1f ready |
| h34 | before | H G 1f needs_merchant_fact |
| h35 | after | T R G 2f ready |
| h35 | before | H G 1f needs_merchant_fact |
| h36 | after | H G 1f needs_listing |
| h36 | before | H G 1f needs_listing |
| h37 | before | G 2f route |
| h38 | before | 0f |
| h39 | after | T R G 1f ready |
| h39 | before | H G 1f needs_merchant_fact |
| h40 | after | T R G 5f ready |
| h40 | before | H G 6f needs_merchant_fact |

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
