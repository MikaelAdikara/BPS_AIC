# Laporan eval Deciqo

Dibuat oleh `eval/run_final.py` dari `outputs.jsonl`. Semua kasus sintetis. Skor otomatis hanya triage: pola terlarang spesifik kasus dan proxy kata kunci. Label manusia buta: **pending** sampai `labels.csv` diisi dua penilai.

Format sel: `k/n (persen; interval Wilson 95%)`. `undefined` berarti denominator 0 (misalnya sistem tanpa teks tidak punya unsafe rate).

## holdout · fase before-fact

| Metrik | Denominator | B1 | D | D-rules |
|---|---|---|---|---|
| Outputs with listing text | semua kasus | 10/10 (100%; 72–100) | 0/10 (0%; 0–28) | 0/10 (0%; 0–28) |
| Unsafe output rate | output yang berisi teks listing | 2/10 (20%; 6–51) | – | – |
| Missing fact held (D) / asked (B, proxy) | kasus butuh fakta | 6/6 (100%; 61–100) | 4/6 (67%; 30–90) | 2/6 (33%; 10–70) |
| Unnecessary hold (D) / asked (B, proxy) | kasus listing yang cukup fakta | 1/1 (100%; 21–100) | 1/1 (100%; 21–100) | 0/1 (0%; 0–79) |
| Gold finding found (B: kata atribut di output, proxy) | kasus bertemuan | 9/9 (100%; 70–100) | 8/9 (89%; 56–98) | 3/9 (33%; 12–65) |
| Action routing (D) | temuan emas yang ditemukan | – | 7/8 (88%; 53–98) | 3/3 (100%; 44–100) |
| Membership precision (D, pooled) | ulasan support yang dihitung | – | 11/11 (100%; 74–100) | 5/5 (100%; 57–100) |
| Membership recall (D, pooled) | ulasan support emas | – | 11/20 (55%; 34–74) | 5/20 (25%; 11–47) |
| Wrong-item routing (D) | ulasan salah kirim | – | 1/1 (100%; 21–100) | 1/1 (100%; 21–100) |
| Findings on praise-only control (D: jumlah temuan; B: output tanpa pernyataan 'tidak ada masalah') | kasus kontrol | 0 pada 1 kasus | 0 pada 1 kasus | 0 pada 1 kasus |

## holdout · fase after-fact

| Metrik | Denominator | B1 | D | D-rules |
|---|---|---|---|---|
| Outputs with listing text | semua kasus | 6/6 (100%; 61–100) | 4/6 (67%; 30–90) | 2/6 (33%; 10–70) |
| Unsafe output rate | output yang berisi teks listing | 0/6 (0%; 0–39) | 0/4 (0%; 0–49) | 0/2 (0%; 0–66) |
| Ready after fact (D) | kasus dengan fakta | – | 4/6 (67%; 30–90) | 2/6 (33%; 10–70) |
| Gold finding found (B: kata atribut di output, proxy) | kasus bertemuan | 6/6 (100%; 61–100) | 5/6 (83%; 44–97) | 2/6 (33%; 10–70) |
| Action routing (D) | temuan emas yang ditemukan | – | 5/5 (100%; 57–100) | 2/2 (100%; 34–100) |
| Membership precision (D, pooled) | ulasan support yang dihitung | – | 6/6 (100%; 61–100) | 4/4 (100%; 51–100) |
| Membership recall (D, pooled) | ulasan support emas | – | 6/15 (40%; 20–64) | 4/15 (27%; 11–52) |
| Wrong-item routing (D) | ulasan salah kirim | – | 1/1 (100%; 21–100) | 1/1 (100%; 21–100) |

## Latency dan biaya

| Sistem | Baris | Rata-rata detik | Total USD | USD per baris |
|---|---|---|---|---|
| B1 | 16 | 13.1 | 0.0484 | 0.0030 |
| D | 16 | 16.0 | 0.0542 | 0.0034 |
| D-rules | 16 | 0.1 | 0.0000 | 0.0000 |

Biaya baseline dari `usage` respons (harga di manifest). Baris gagal tanpa usage dicatat sebagai reservasi, bukan nol.

## Per kasus

`T` = ada teks listing, `U[i]` = pola terlarang ke-i cocok, `A` = bertanya/placeholder (proxy, baseline), `H` = draf ditahan (D), `R` = draf siap (D), `G` = temuan emas ditemukan, `-` = tidak ada output.

| Kasus | Fase | B1 | D | D-rules |
|---|---|---|---|---|
| h01 | after | T G | T R G 2f ready | T R G 1f ready |
| h01 | before | T A G | H G 2f needs_merchant_fact | H G 1f needs_merchant_fact |
| h02 | before | T A G | H G 1f needs_merchant_fact | 0f |
| h03 | after | T A G | 0f | 1f |
| h03 | before | T A G | G 2f route | 1f |
| h04 | after | T A G | T R G 2f ready | 0f |
| h04 | before | T U0,1 A G | H G 3f needs_merchant_fact | 0f |
| h05 | after | T A G | T R G 1f ready | 0f |
| h05 | before | T A G | H G 1f needs_merchant_fact | 0f |
| h06 | after | T A G | T R G 3f ready | T R G 2f ready |
| h06 | before | T A G | G 3f needs_review | H G 2f needs_merchant_fact |
| h07 | before | T G | 0f | G 1f route |
| h08 | before | T U0,1 A G | G 1f route | 0f |
| h09 | after | T A G | H G 2f needs_listing | 0f |
| h09 | before | T A G | H G 1f needs_listing | 0f |
| h10 | before | T A | 0f | 0f |

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
