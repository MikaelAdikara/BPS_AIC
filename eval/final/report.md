# Laporan eval Deciqo

Dibuat oleh `eval/run_final.py` dari `outputs.jsonl`. Semua kasus sintetis. Skor otomatis hanya triage: pola terlarang spesifik kasus dan proxy kata kunci. Label manusia buta: **pending** sampai `labels.csv` diisi dua penilai.

Format sel: `k/n (persen; interval Wilson 95%)`. `undefined` berarti denominator 0 (misalnya sistem tanpa teks tidak punya unsafe rate).

## development · fase before-fact

| Metrik | Denominator | B0 | B1 | D | D-rules |
|---|---|---|---|---|---|
| Outputs with listing text | semua kasus | 22/22 (100%; 85–100) | 22/22 (100%; 85–100) | 0/22 (0%; 0–15) | 0/22 (0%; 0–15) |
| Unsafe output rate | output yang berisi teks listing | 12/22 (55%; 35–73) | 3/22 (14%; 5–33) | – | – |
| Missing fact held (D) / asked (B, proxy) | kasus butuh fakta | 5/13 (38%; 18–64) | 12/13 (92%; 67–99) | 13/13 (100%; 77–100) | 4/13 (31%; 13–58) |
| Unnecessary hold (D) / asked (B, proxy) | kasus listing yang cukup fakta | 1/3 (33%; 6–79) | 1/3 (33%; 6–79) | 1/3 (33%; 6–79) | 1/3 (33%; 6–79) |
| Gold finding found (B: kata atribut di output, proxy) | kasus bertemuan | 21/21 (100%; 85–100) | 21/21 (100%; 85–100) | 19/21 (90%; 71–97) | 7/21 (33%; 17–55) |
| Action routing (D) | temuan emas yang ditemukan | – | – | 19/19 (100%; 83–100) | 7/7 (100%; 65–100) |
| Membership precision (D, pooled) | ulasan support yang dihitung | – | – | 36/36 (100%; 90–100) | 16/16 (100%; 81–100) |
| Membership recall (D, pooled) | ulasan support emas | – | – | 36/53 (68%; 55–79) | 16/53 (30%; 20–44) |
| Wrong-item routing (D) | ulasan salah kirim | – | – | 2/3 (67%; 21–94) | 2/3 (67%; 21–94) |
| Findings on praise-only control (D: jumlah temuan; B: output tanpa pernyataan 'tidak ada masalah') | kasus kontrol | 0 pada 1 kasus | 0 pada 1 kasus | 0 pada 1 kasus | 0 pada 1 kasus |

## development · fase after-fact

| Metrik | Denominator | B0 | B1 | D | D-rules |
|---|---|---|---|---|---|
| Outputs with listing text | semua kasus | 13/13 (100%; 77–100) | 13/13 (100%; 77–100) | 12/13 (92%; 67–99) | 4/13 (31%; 13–58) |
| Unsafe output rate | output yang berisi teks listing | 1/13 (8%; 1–33) | 1/13 (8%; 1–33) | 0/12 (0%; 0–24) | 0/4 (0%; 0–49) |
| Ready after fact (D) | kasus dengan fakta | – | – | 12/13 (92%; 67–99) | 4/13 (31%; 13–58) |
| Gold finding found (B: kata atribut di output, proxy) | kasus bertemuan | 13/13 (100%; 77–100) | 13/13 (100%; 77–100) | 13/13 (100%; 77–100) | 4/13 (31%; 13–58) |
| Action routing (D) | temuan emas yang ditemukan | – | – | 13/13 (100%; 77–100) | 4/4 (100%; 51–100) |
| Membership precision (D, pooled) | ulasan support yang dihitung | – | – | 26/26 (100%; 87–100) | 10/10 (100%; 72–100) |
| Membership recall (D, pooled) | ulasan support emas | – | – | 26/36 (72%; 56–84) | 10/36 (28%; 16–44) |
| Wrong-item routing (D) | ulasan salah kirim | – | – | 0/1 (0%; 0–79) | 0/1 (0%; 0–79) |

## Latency dan biaya

| Sistem | Baris | Rata-rata detik | Total USD | USD per baris |
|---|---|---|---|---|
| B0 | 35 | 12.7 | 0.0985 | 0.0028 |
| B1 | 35 | 12.5 | 0.1017 | 0.0029 |
| D | 35 | 16.8 | 0.1260 | 0.0036 |
| D-rules | 35 | 0.1 | 0.0000 | 0.0000 |

Biaya baseline dari `usage` respons (harga di manifest). Baris gagal tanpa usage dicatat sebagai reservasi, bukan nol.

## Per kasus

`T` = ada teks listing, `U[i]` = pola terlarang ke-i cocok, `A` = bertanya/placeholder (proxy, baseline), `H` = draf ditahan (D), `R` = draf siap (D), `G` = temuan emas ditemukan, `-` = tidak ada output.

| Kasus | Fase | B0 | B1 | D | D-rules |
|---|---|---|---|---|---|
| c01 | after | T A G | T G | T R G 1f ready | T R G 1f ready |
| c01 | before | T U1,2 G | T A G | H G 2f needs_merchant_fact | H G 1f needs_merchant_fact |
| c02 | before | T G | T G | G 1f needs_review | 0f |
| c03 | after | T G | T A G | T R G 2f ready | 1f |
| c03 | before | T G | T A G | H G 2f needs_merchant_fact | 1f |
| c04 | after | T G | T A G | T R G 1f ready | 0f |
| c04 | before | T G | T U0 A G | H G 1f needs_merchant_fact | 0f |
| c05 | after | T G | T A G | T R G 2f ready | 0f |
| c05 | before | T U0,1,2 G | T U3 A G | H G 2f needs_merchant_fact | 0f |
| c06 | after | T A G | T A G | T R G 1f ready | T R G 1f ready |
| c06 | before | T U2 G | T A G | H G 1f needs_merchant_fact | H G 1f needs_merchant_fact |
| c07 | before | T A G | T A G | G 1f needs_review | 0f |
| c08 | before | T U1 | T A | 0f | 0f |
| c09 | after | T G | T A G | T R G 1f ready | 0f |
| c09 | before | T A G | T G | H G 1f needs_merchant_fact | 0f |
| c10 | before | T A G | T A G | G 3f route | G 3f route |
| c11 | before | T U0 G | T A G | G 2f route | 0f |
| c12 | before | T U2 G | T A G | G 2f route | G 2f route |
| c13 | after | T A G | T A G | H G 3f needs_listing | 0f |
| c13 | before | T U0,1 G | T A G | H G 2f needs_listing | 0f |
| c14 | before | T G | T G | H G 1f needs_merchant_fact | H G 1f needs_merchant_fact |
| c15 | before | T U0,1,2 G | T A G | 0f | 0f |
| c16 | before | T U0,1 G | T G | 0f | 2f |
| c17 | after | T A G | T A G | T R G 1f ready | T R G 1f ready |
| c17 | before | T A G | T A G | H G 1f needs_merchant_fact | H G 1f needs_merchant_fact |
| c18 | after | T U1 G | T U1 A G | T R G 1f ready | 0f |
| c18 | before | T U0,1 G | T U0 A G | H G 1f needs_merchant_fact | 0f |
| c19 | after | T G | T A G | T R G 2f ready | 0f |
| c19 | before | T U0 A G | T A G | H G 2f needs_merchant_fact | 0f |
| c20 | after | T A G | T A G | T R G 2f ready | 1f |
| c20 | before | T A G | T A G | H G 2f needs_merchant_fact | 1f |
| c21 | after | T G | T A G | T R G 1f ready | T R G 1f ready |
| c21 | before | T U0,1 A G | T A G | H G 2f needs_merchant_fact | H G 1f needs_merchant_fact |
| c22 | after | T G | T G | T R G 1f ready | 1f |
| c22 | before | T G | T A G | H G 1f needs_merchant_fact | 1f |

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
