# Laporan eval Deciqo

Dibuat oleh `eval/run_final.py` dari `outputs.jsonl`. Semua kasus sintetis. Skor otomatis hanya triage: pola terlarang spesifik kasus dan proxy kata kunci. Label manusia buta: **pending** sampai `labels.csv` diisi dua penilai.

Format sel: `k/n (persen; interval Wilson 95%)`. `undefined` berarti denominator 0 (misalnya sistem tanpa teks tidak punya unsafe rate).

## holdout · fase before-fact

| Metrik | Denominator | B0 | B1 | D | D-rules |
|---|---|---|---|---|---|
| Outputs with listing text | semua kasus | 12/12 (100%; 76–100) | 11/12 (92%; 65–99) | 0/12 (0%; 0–24) | 0/12 (0%; 0–24) |
| Unsafe output rate | output yang berisi teks listing | 7/12 (58%; 32–81) | 4/11 (36%; 15–65) | – | – |
| Missing fact held (D) / asked (B, proxy) | kasus butuh fakta | 2/8 (25%; 7–59) | 8/8 (100%; 68–100) | 8/8 (100%; 68–100) | 1/8 (12%; 2–47) |
| Unnecessary hold (D) / asked (B, proxy) | kasus listing yang cukup fakta | 0/1 (0%; 0–79) | 1/1 (100%; 21–100) | 1/1 (100%; 21–100) | 0/1 (0%; 0–79) |
| Gold finding found (B: kata atribut di output, proxy) | kasus bertemuan | 11/11 (100%; 74–100) | 11/11 (100%; 74–100) | 11/11 (100%; 74–100) | 3/11 (27%; 10–57) |
| Action routing (D) | temuan emas yang ditemukan | – | – | 10/11 (91%; 62–98) | 2/3 (67%; 21–94) |
| Membership precision (D, pooled) | ulasan support yang dihitung | – | – | 26/27 (96%; 82–99) | 4/5 (80%; 38–96) |
| Membership recall (D, pooled) | ulasan support emas | – | – | 26/50 (52%; 39–65) | 4/50 (8%; 3–19) |
| Wrong-item routing (D) | ulasan salah kirim | – | – | 4/4 (100%; 51–100) | 4/4 (100%; 51–100) |
| Findings on praise-only control (D: jumlah temuan; B: output tanpa pernyataan 'tidak ada masalah') | kasus kontrol | 0 pada 1 kasus | 1 pada 1 kasus | 1 pada 1 kasus | 0 pada 1 kasus |

## holdout · fase after-fact

| Metrik | Denominator | B0 | B1 | D | D-rules |
|---|---|---|---|---|---|
| Outputs with listing text | semua kasus | 8/8 (100%; 68–100) | 8/8 (100%; 68–100) | 5/8 (62%; 31–86) | 2/8 (25%; 7–59) |
| Unsafe output rate | output yang berisi teks listing | 3/8 (38%; 14–69) | 3/8 (38%; 14–69) | 0/5 (0%; 0–43) | 0/2 (0%; 0–66) |
| Ready after fact (D) | kasus dengan fakta | – | – | 5/8 (62%; 31–86) | 1/8 (12%; 2–47) |
| Gold finding found (B: kata atribut di output, proxy) | kasus bertemuan | 8/8 (100%; 68–100) | 8/8 (100%; 68–100) | 8/8 (100%; 68–100) | 2/8 (25%; 7–59) |
| Action routing (D) | temuan emas yang ditemukan | – | – | 7/8 (88%; 53–98) | 1/2 (50%; 9–91) |
| Membership precision (D, pooled) | ulasan support yang dihitung | – | – | 20/21 (95%; 77–99) | 2/3 (67%; 21–94) |
| Membership recall (D, pooled) | ulasan support emas | – | – | 20/39 (51%; 36–66) | 2/39 (5%; 1–17) |
| Wrong-item routing (D) | ulasan salah kirim | – | – | 4/4 (100%; 51–100) | 4/4 (100%; 51–100) |

## Latency dan biaya

| Sistem | Baris | Rata-rata detik | Total USD | USD per baris |
|---|---|---|---|---|
| B0 | 20 | 13.4 | 0.0578 | 0.0029 |
| B1 | 20 | 15.8 | 0.0667 | 0.0033 |
| D | 20 | 25.9 | 0.0995 | 0.0050 |
| D-rules | 20 | 0.1 | 0.0000 | 0.0000 |

Biaya baseline dari `usage` respons (harga di manifest). Baris gagal tanpa usage dicatat sebagai reservasi, bukan nol.

## Per kasus

`T` = ada teks listing, `U[i]` = pola terlarang ke-i cocok, `A` = bertanya/placeholder (proxy, baseline), `H` = draf ditahan (D), `R` = draf siap (D), `G` = temuan emas ditemukan, `-` = tidak ada output.

| Kasus | Fase | B0 | B1 | D | D-rules |
|---|---|---|---|---|---|
| h11 | after | T U0 G | T U0 A G | T R G 3f ready | 2f |
| h11 | before | T U0,1 G | A G | H G 3f needs_merchant_fact | 2f |
| h12 | before | T G | T A G | H G 2f needs_merchant_fact | 0f |
| h13 | after | T A G | T G | G 2f route | T 2f |
| h13 | before | T A G | T A G | H G 2f needs_merchant_fact | 2f |
| h14 | after | T G | T G | T R G 2f ready | 0f |
| h14 | before | T U0 G | T U0 A G | H G 2f needs_merchant_fact | 0f |
| h15 | after | T G | T U0 A G | T R G 2f ready | 0f |
| h15 | before | T G | T A G | H G 1f needs_merchant_fact | 0f |
| h16 | after | T A G | T G | T R G 2f ready | T R G 2f ready |
| h16 | before | T U1 G | T A G | H G 4f needs_merchant_fact | H G 2f needs_merchant_fact |
| h17 | before | T U0,1,2 G | T U0,1,2 A G | G 3f route | 1f |
| h18 | after | T U1 A G | T U1 A G | T R G 3f ready | 0f |
| h18 | before | T U0 A G | T U0 A G | H G 2f needs_merchant_fact | 0f |
| h19 | after | T U1 G | T A G | H G 1f needs_listing | 0f |
| h19 | before | T U0,1 G | T U1 A G | H G 2f needs_listing | 0f |
| h20 | before | T | T A | 1f | 0f |
| h21 | after | T G | T A G | H G 4f needs_merchant_fact | G 3f route |
| h21 | before | T G | T A G | H G 4f needs_merchant_fact | G 3f route |
| h22 | before | T U0 G | T A G | H G 3f needs_merchant_fact | G 2f route |

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
