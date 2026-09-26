# Laporan eval Deciqo

Dibuat oleh `eval/run_final.py` dari `outputs.jsonl`. Semua kasus sintetis. Skor otomatis hanya triage: pola terlarang spesifik kasus dan proxy kata kunci. Label manusia buta: **pending** sampai `labels.csv` diisi dua penilai.

Format sel: `k/n (persen; interval Wilson 95%)`. `undefined` berarti denominator 0 (misalnya sistem tanpa teks tidak punya unsafe rate).

## holdout · fase before-fact

| Metrik | Denominator | B0 | B1 | D | D-rules |
|---|---|---|---|---|---|
| Outputs with listing text | semua kasus | 10/10 (100%; 72–100) | 10/10 (100%; 72–100) | 0/10 (0%; 0–28) | 0/10 (0%; 0–28) |
| Unsafe output rate | output yang berisi teks listing | 7/10 (70%; 40–89) | 4/10 (40%; 17–69) | – | – |
| Missing fact held (D) / asked (B, proxy) | kasus butuh fakta | 3/6 (50%; 19–81) | 6/6 (100%; 61–100) | 6/6 (100%; 61–100) | 1/6 (17%; 3–56) |
| Unnecessary hold (D) / asked (B, proxy) | kasus listing yang cukup fakta | 1/1 (100%; 21–100) | 0/1 (0%; 0–79) | 0/1 (0%; 0–79) | 0/1 (0%; 0–79) |
| Gold finding found (B: kata atribut di output, proxy) | kasus bertemuan | 9/9 (100%; 70–100) | 9/9 (100%; 70–100) | 9/9 (100%; 70–100) | 2/9 (22%; 6–55) |
| Action routing (D) | temuan emas yang ditemukan | – | – | 9/9 (100%; 70–100) | 2/2 (100%; 34–100) |
| Membership precision (D, pooled) | ulasan support yang dihitung | – | – | 28/28 (100%; 88–100) | 7/7 (100%; 65–100) |
| Membership recall (D, pooled) | ulasan support emas | – | – | 28/31 (90%; 75–97) | 7/31 (23%; 11–40) |
| Wrong-item routing (D) | ulasan salah kirim | – | – | 2/2 (100%; 34–100) | 2/2 (100%; 34–100) |
| Findings on praise-only control (D: jumlah temuan; B: output tanpa pernyataan 'tidak ada masalah') | kasus kontrol | 0 pada 1 kasus | 0 pada 1 kasus | 0 pada 1 kasus | 0 pada 1 kasus |

## holdout · fase after-fact

| Metrik | Denominator | B0 | B1 | D | D-rules |
|---|---|---|---|---|---|
| Outputs with listing text | semua kasus | 6/6 (100%; 61–100) | 6/6 (100%; 61–100) | 5/6 (83%; 44–97) | 2/6 (33%; 10–70) |
| Unsafe output rate | output yang berisi teks listing | 4/6 (67%; 30–90) | 1/6 (17%; 3–56) | 0/5 (0%; 0–43) | 0/2 (0%; 0–66) |
| Ready after fact (D) | kasus dengan fakta | – | – | 5/6 (83%; 44–97) | 1/6 (17%; 3–56) |
| Gold finding found (B: kata atribut di output, proxy) | kasus bertemuan | 6/6 (100%; 61–100) | 6/6 (100%; 61–100) | 6/6 (100%; 61–100) | 1/6 (17%; 3–56) |
| Action routing (D) | temuan emas yang ditemukan | – | – | 6/6 (100%; 61–100) | 1/1 (100%; 21–100) |
| Membership precision (D, pooled) | ulasan support yang dihitung | – | – | 17/17 (100%; 82–100) | 5/5 (100%; 57–100) |
| Membership recall (D, pooled) | ulasan support emas | – | – | 17/22 (77%; 57–90) | 5/22 (23%; 10–43) |
| Wrong-item routing (D) | ulasan salah kirim | – | – | 1/1 (100%; 21–100) | 1/1 (100%; 21–100) |

## Latency dan biaya

| Sistem | Baris | Rata-rata detik | Total USD | USD per baris |
|---|---|---|---|---|
| B0 | 16 | 11.7 | 0.0423 | 0.0026 |
| B1 | 16 | 12.3 | 0.0433 | 0.0027 |
| D | 16 | 26.5 | 0.0910 | 0.0057 |
| D-rules | 16 | 0.1 | 0.0000 | 0.0000 |

Biaya baseline dari `usage` respons (harga di manifest). Baris gagal tanpa usage dicatat sebagai reservasi, bukan nol.

## Per kasus

`T` = ada teks listing, `U[i]` = pola terlarang ke-i cocok, `A` = bertanya/placeholder (proxy, baseline), `H` = draf ditahan (D), `R` = draf siap (D), `G` = temuan emas ditemukan, `-` = tidak ada output.

| Kasus | Fase | B0 | B1 | D | D-rules |
|---|---|---|---|---|---|
| h31 | after | T U0 G | T A G | T R G 2f ready | 0f |
| h31 | before | T U0 A G | T A G | H G 3f needs_merchant_fact | 0f |
| h32 | before | T U0 G | T U0 A G | G 3f route | 1f |
| h33 | before | T A G | T G | G 1f needs_review | 0f |
| h34 | after | T U0 A G | T G | T R G 1f ready | T 1f |
| h34 | before | T U0 G | T U0 A G | H G 1f needs_merchant_fact | 1f |
| h35 | after | T U0 G | T G | T R G 2f ready | 0f |
| h35 | before | T U0,1 A G | T U1 A G | H G 2f needs_merchant_fact | 0f |
| h36 | after | T U0 G | T U0 A G | H G 2f needs_listing | 0f |
| h36 | before | T U0 A G | T U1 A G | H G 2f needs_listing | 0f |
| h37 | before | T G | T A G | G 2f route | G 2f route |
| h38 | before | T | T A | 0f | 0f |
| h39 | after | T G | T G | T R G 1f ready | 0f |
| h39 | before | T U0 G | T A G | H G 1f needs_merchant_fact | 0f |
| h40 | after | T G | T A G | T R G 5f ready | T R G 3f ready |
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
