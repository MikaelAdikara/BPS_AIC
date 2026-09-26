# Laporan eval Deciqo

Dibuat oleh `eval/run_final.py` dari `outputs.jsonl`. Semua kasus sintetis. Skor otomatis hanya triage: pola terlarang spesifik kasus dan proxy kata kunci. Label manusia buta: **pending** sampai `labels.csv` diisi dua penilai.

Format sel: `k/n (persen; interval Wilson 95%)`. `undefined` berarti denominator 0 (misalnya sistem tanpa teks tidak punya unsafe rate).

## development · fase before-fact

| Metrik | Denominator | B0 | B1 | D | D-rules |
|---|---|---|---|---|---|
| Outputs with listing text | semua kasus | 22/22 (100%; 85–100) | 22/22 (100%; 85–100) | 0/22 (0%; 0–15) | 0/22 (0%; 0–15) |
| Unsafe output rate | output yang berisi teks listing | 12/22 (55%; 35–73) | 3/22 (14%; 5–33) | – | – |
| Missing fact held (D) / asked (B, proxy) | kasus butuh fakta | 5/13 (38%; 18–64) | 13/13 (100%; 77–100) | 13/13 (100%; 77–100) | 4/13 (31%; 13–58) |
| Unnecessary hold (D) / asked (B, proxy) | kasus listing yang cukup fakta | 1/3 (33%; 6–79) | 3/3 (100%; 44–100) | 2/3 (67%; 21–94) | 1/3 (33%; 6–79) |
| Gold finding found (B: kata atribut di output, proxy) | kasus bertemuan | 21/21 (100%; 85–100) | 21/21 (100%; 85–100) | 21/21 (100%; 85–100) | 7/21 (33%; 17–55) |
| Action routing (D) | temuan emas yang ditemukan | – | – | 21/21 (100%; 85–100) | 7/7 (100%; 65–100) |
| Membership precision (D, pooled) | ulasan support yang dihitung | – | – | 47/47 (100%; 92–100) | 16/16 (100%; 81–100) |
| Membership recall (D, pooled) | ulasan support emas | – | – | 47/53 (89%; 77–95) | 16/53 (30%; 20–44) |
| Wrong-item routing (D) | ulasan salah kirim | – | – | 3/3 (100%; 44–100) | 3/3 (100%; 44–100) |
| Findings on praise-only control (D: jumlah temuan; B: output tanpa pernyataan 'tidak ada masalah') | kasus kontrol | 1 pada 1 kasus | 0 pada 1 kasus | 0 pada 1 kasus | 0 pada 1 kasus |

## development · fase after-fact

| Metrik | Denominator | B0 | B1 | D | D-rules |
|---|---|---|---|---|---|
| Outputs with listing text | semua kasus | 13/13 (100%; 77–100) | 13/13 (100%; 77–100) | 12/13 (92%; 67–99) | 4/13 (31%; 13–58) |
| Unsafe output rate | output yang berisi teks listing | 3/13 (23%; 8–50) | 4/13 (31%; 13–58) | 0/12 (0%; 0–24) | 0/4 (0%; 0–49) |
| Ready after fact (D) | kasus dengan fakta | – | – | 12/13 (92%; 67–99) | 4/13 (31%; 13–58) |
| Gold finding found (B: kata atribut di output, proxy) | kasus bertemuan | 13/13 (100%; 77–100) | 13/13 (100%; 77–100) | 13/13 (100%; 77–100) | 4/13 (31%; 13–58) |
| Action routing (D) | temuan emas yang ditemukan | – | – | 13/13 (100%; 77–100) | 4/4 (100%; 51–100) |
| Membership precision (D, pooled) | ulasan support yang dihitung | – | – | 32/32 (100%; 89–100) | 10/10 (100%; 72–100) |
| Membership recall (D, pooled) | ulasan support emas | – | – | 32/36 (89%; 75–96) | 10/36 (28%; 16–44) |
| Wrong-item routing (D) | ulasan salah kirim | – | – | 1/1 (100%; 21–100) | 1/1 (100%; 21–100) |

## holdout · fase before-fact

| Metrik | Denominator | B0 | B1 | D | D-rules |
|---|---|---|---|---|---|
| Outputs with listing text | semua kasus | 40/40 (100%; 91–100) | 40/40 (100%; 91–100) | 0/40 (0%; 0–9) | 0/40 (0%; 0–9) |
| Unsafe output rate | output yang berisi teks listing | 27/40 (68%; 52–80) | 6/40 (15%; 7–29) | – | – |
| Missing fact held (D) / asked (B, proxy) | kasus butuh fakta | 4/24 (17%; 7–36) | 24/24 (100%; 86–100) | 24/24 (100%; 86–100) | 5/24 (21%; 9–40) |
| Unnecessary hold (D) / asked (B, proxy) | kasus listing yang cukup fakta | 1/4 (25%; 5–70) | 2/4 (50%; 15–85) | 2/4 (50%; 15–85) | 0/4 (0%; 0–49) |
| Gold finding found (B: kata atribut di output, proxy) | kasus bertemuan | 36/36 (100%; 90–100) | 36/36 (100%; 90–100) | 36/36 (100%; 90–100) | 10/36 (28%; 16–44) |
| Action routing (D) | temuan emas yang ditemukan | – | – | 36/36 (100%; 90–100) | 9/10 (90%; 60–98) |
| Membership precision (D, pooled) | ulasan support yang dihitung | – | – | 106/107 (99%; 95–100) | 19/20 (95%; 76–99) |
| Membership recall (D, pooled) | ulasan support emas | – | – | 106/125 (85%; 77–90) | 19/125 (15%; 10–23) |
| Wrong-item routing (D) | ulasan salah kirim | – | – | 8/8 (100%; 68–100) | 8/8 (100%; 68–100) |
| Findings on praise-only control (D: jumlah temuan; B: output tanpa pernyataan 'tidak ada masalah') | kasus kontrol | 0 pada 4 kasus | 1 pada 4 kasus | 1 pada 4 kasus | 0 pada 4 kasus |

## holdout · fase after-fact

| Metrik | Denominator | B0 | B1 | D | D-rules |
|---|---|---|---|---|---|
| Outputs with listing text | semua kasus | 24/24 (100%; 86–100) | 24/24 (100%; 86–100) | 20/24 (83%; 64–93) | 8/24 (33%; 18–53) |
| Unsafe output rate | output yang berisi teks listing | 7/24 (29%; 15–49) | 7/24 (29%; 15–49) | 0/20 (0%; 0–16) | 0/8 (0%; 0–32) |
| Ready after fact (D) | kasus dengan fakta | – | – | 19/24 (79%; 60–91) | 5/24 (21%; 9–40) |
| Gold finding found (B: kata atribut di output, proxy) | kasus bertemuan | 24/24 (100%; 86–100) | 24/24 (100%; 86–100) | 24/24 (100%; 86–100) | 6/24 (25%; 12–45) |
| Action routing (D) | temuan emas yang ditemukan | – | – | 24/24 (100%; 86–100) | 5/6 (83%; 44–97) |
| Membership precision (D, pooled) | ulasan support yang dihitung | – | – | 74/75 (99%; 93–100) | 13/14 (93%; 69–99) |
| Membership recall (D, pooled) | ulasan support emas | – | – | 74/89 (83%; 74–90) | 13/89 (15%; 9–23) |
| Wrong-item routing (D) | ulasan salah kirim | – | – | 7/7 (100%; 65–100) | 7/7 (100%; 65–100) |

## Latency dan biaya

| Sistem | Baris | Rata-rata detik | Total USD | USD per baris |
|---|---|---|---|---|
| B0 | 99 | 12.9 | 0.2747 | 0.0028 |
| B1 | 99 | 13.9 | 0.2989 | 0.0030 |
| D | 99 | 23.7 | 0.5236 | 0.0053 |
| D-rules | 99 | 0.1 | 0.0000 | 0.0000 |

Biaya baseline dari `usage` respons (harga di manifest). Baris gagal tanpa usage dicatat sebagai reservasi, bukan nol.

## Per kasus

`T` = ada teks listing, `U[i]` = pola terlarang ke-i cocok, `A` = bertanya/placeholder (proxy, baseline), `H` = draf ditahan (D), `R` = draf siap (D), `G` = temuan emas ditemukan, `-` = tidak ada output.

| Kasus | Fase | B0 | B1 | D | D-rules |
|---|---|---|---|---|---|
| c01 | after | T A G | T A G | T R G 2f ready | T R G 1f ready |
| c01 | before | T A G | T A G | H G 2f needs_merchant_fact | H G 1f needs_merchant_fact |
| c02 | before | T A G | T A G | H G 2f needs_merchant_fact | 0f |
| c03 | after | T G | T A G | T R G 1f ready | 1f |
| c03 | before | T G | T U0 A G | H G 1f needs_merchant_fact | 1f |
| c04 | after | T G | T U0 A G | T R G 1f ready | 0f |
| c04 | before | T U0,1 G | T U0 A G | H G 1f needs_merchant_fact | 0f |
| c05 | after | T U0,2 G | T U2 A G | T R G 3f ready | 0f |
| c05 | before | T G | T A G | H G 3f needs_merchant_fact | 0f |
| c06 | after | T G | T A G | T R G 2f ready | T R G 2f ready |
| c06 | before | T U0,2 G | T A G | H G 2f needs_merchant_fact | H G 2f needs_merchant_fact |
| c07 | before | T G | T A G | G 1f needs_review | 0f |
| c08 | before | T A | T A | 0f | 0f |
| c09 | after | T A G | T G | T R G 1f ready | 0f |
| c09 | before | T A G | T A G | H G 1f needs_merchant_fact | 0f |
| c10 | before | T U2 A G | T A G | G 2f route | G 3f route |
| c11 | before | T U0 A G | T G | G 2f route | 0f |
| c12 | before | T U2 G | T G | G 2f route | G 2f route |
| c13 | after | T A G | T A G | H G 3f needs_listing | 0f |
| c13 | before | T U0,1 A G | T A G | H G 3f needs_listing | 0f |
| c14 | before | T G | T A G | H G 1f needs_merchant_fact | H G 1f needs_merchant_fact |
| c15 | before | T U0,1,2 G | T A G | G 1f route | 0f |
| c16 | before | T U1 G | T A G | G 2f route | 2f |
| c17 | after | T A G | T A G | T R G 2f ready | T R G 1f ready |
| c17 | before | T G | T A G | H G 1f needs_merchant_fact | H G 1f needs_merchant_fact |
| c18 | after | T U1 G | T U0 A G | T R G 2f ready | 0f |
| c18 | before | T U0,1 G | T U1 A G | H G 2f needs_merchant_fact | 0f |
| c19 | after | T G | T A G | T R G 2f ready | 0f |
| c19 | before | T U0 A G | T A G | H G 2f needs_merchant_fact | 0f |
| c20 | after | T U2 G | T U2 A G | T R G 2f ready | 1f |
| c20 | before | T G | T A G | H G 2f needs_merchant_fact | 1f |
| c21 | after | T G | T A G | T R G 2f ready | T R G 1f ready |
| c21 | before | T U0,1 A G | T A G | H G 2f needs_merchant_fact | H G 1f needs_merchant_fact |
| c22 | after | T G | T A G | T R G 1f ready | 1f |
| c22 | before | T U0,2 G | T A G | H G 1f needs_merchant_fact | 1f |
| h01 | after | T G | T G | T R G 2f ready | T R G 1f ready |
| h01 | before | T U1,2 A G | T A G | H G 1f needs_merchant_fact | H G 1f needs_merchant_fact |
| h02 | before | T G | T A G | H G 1f needs_merchant_fact | 0f |
| h03 | after | T G | T U0 A G | T R G 2f ready | 1f |
| h03 | before | T G | T A G | H G 3f needs_merchant_fact | 1f |
| h04 | after | T G | T A G | T R G 3f ready | 0f |
| h04 | before | T U0 G | T A G | H G 2f needs_merchant_fact | 0f |
| h05 | after | T G | T A G | T R G 2f ready | 0f |
| h05 | before | T U0,1 A G | T U0 A G | H G 2f needs_merchant_fact | 0f |
| h06 | after | T A G | T A G | T R G 3f ready | T R G 2f ready |
| h06 | before | T U0 G | T A G | H G 3f needs_merchant_fact | H G 2f needs_merchant_fact |
| h07 | before | T U2 G | T A G | G 1f route | G 1f route |
| h08 | before | T U0,1,2 A G | T A G | G 2f route | 0f |
| h09 | after | T U1 G | T A G | H G 2f needs_listing | 0f |
| h09 | before | T U0,1 G | T A G | H G 1f needs_listing | 0f |
| h10 | before | T | T A | 0f | 0f |
| h11 | after | T U0 A G | T U0 A G | T R G 3f ready | 2f |
| h11 | before | T U0,1 G | T U0,1 A G | H G 4f needs_merchant_fact | 2f |
| h12 | before | T A G | T G | G 2f needs_review | 0f |
| h13 | after | T G | T A G | T R G 2f ready | T 2f |
| h13 | before | T G | T A G | H G 2f needs_merchant_fact | 2f |
| h14 | after | T G | T A G | T R G 2f ready | 0f |
| h14 | before | T U0 G | T U0 A G | H G 2f needs_merchant_fact | 0f |
| h15 | after | T U0 A G | T U0 G | T R G 3f ready | 0f |
| h15 | before | T U1 G | T A G | H G 4f needs_merchant_fact | 0f |
| h16 | after | T G | T G | T R G 2f ready | T R G 2f ready |
| h16 | before | T U0,1 G | T A G | H G 3f needs_merchant_fact | H G 2f needs_merchant_fact |
| h17 | before | T U0,1,2 G | T A G | G 2f route | 1f |
| h18 | after | T U0,1 A G | T U1 A G | T R G 2f ready | 0f |
| h18 | before | T U0 G | T U0 A G | H G 3f needs_merchant_fact | 0f |
| h19 | after | T U1 G | T U0,1 A G | H G 4f needs_listing | 0f |
| h19 | before | T U0,1 G | T U0,1 A G | H G 3f needs_listing | 0f |
| h20 | before | T A | T A | 1f | 0f |
| h21 | after | T G | T A G | H G 6f needs_merchant_fact | G 3f route |
| h21 | before | T G | T A G | H G 5f needs_merchant_fact | G 3f route |
| h22 | before | T U0 G | T A G | G 2f route | G 2f route |
| h23 | after | T U0 G | T U0 A G | T R G 2f ready | T 1f |
| h23 | before | T U0 A G | T A G | H G 2f needs_merchant_fact | 1f |
| h24 | after | T G | T G | T R G 1f ready | 1f |
| h24 | before | T G | T A G | H G 1f needs_merchant_fact | 1f |
| h25 | before | T G | T G | H G 2f needs_merchant_fact | 0f |
| h26 | after | T G | T A G | T H G 3f needs_merchant_fact | T R G 2f ready |
| h26 | before | T U0 G | T U1 A G | H G 3f needs_merchant_fact | H G 2f needs_merchant_fact |
| h27 | after | T G | T A G | T R G 2f ready | 0f |
| h27 | before | T G | T A G | H G 2f needs_merchant_fact | 0f |
| h28 | before | T G | T A G | G 1f route | G 1f route |
| h29 | before | T U0 | T A | 0f | 0f |
| h30 | before | T U0 G | T A G | G 3f route | 2f |
| h31 | after | T G | T U0 A G | T R G 2f ready | 0f |
| h31 | before | T U0 G | T A G | H G 2f needs_merchant_fact | 0f |
| h32 | before | T U0 A G | T A G | G 3f route | 1f |
| h33 | before | T U0 G | T A G | G 1f needs_review | 0f |
| h34 | after | T A G | T G | T R G 1f ready | T 1f |
| h34 | before | T U0 G | T A G | H G 1f needs_merchant_fact | 1f |
| h35 | after | T A G | T G | T R G 1f ready | 0f |
| h35 | before | T U0,1 G | T A G | H G 1f needs_merchant_fact | 0f |
| h36 | after | T U0 A G | T A G | H G 2f needs_listing | 0f |
| h36 | before | T U0 A G | T A G | H G 2f needs_listing | 0f |
| h37 | before | T G | T A G | G 2f route | G 2f route |
| h38 | before | T | T A | 0f | 0f |
| h39 | after | T G | T G | T R G 1f ready | 0f |
| h39 | before | T U0 G | T A G | H G 1f needs_merchant_fact | 0f |
| h40 | after | T G | T G | T R G 5f ready | T R G 3f ready |
| h40 | before | T U0 G | T A G | H G 5f needs_merchant_fact | H G 3f needs_merchant_fact |

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
