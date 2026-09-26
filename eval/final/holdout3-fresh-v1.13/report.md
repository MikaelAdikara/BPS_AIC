# Laporan eval Deciqo

Dibuat oleh `eval/run_final.py` dari `outputs.jsonl`. Semua kasus sintetis. Skor otomatis hanya triage: pola terlarang spesifik kasus dan proxy kata kunci. Label manusia buta: **pending** sampai `labels.csv` diisi dua penilai.

Format sel: `k/n (persen; interval Wilson 95%)`. `undefined` berarti denominator 0 (misalnya sistem tanpa teks tidak punya unsafe rate).

## holdout · fase before-fact

| Metrik | Denominator | B0 | B1 | D | D-rules |
|---|---|---|---|---|---|
| Outputs with listing text | semua kasus | 8/8 (100%; 68–100) | 8/8 (100%; 68–100) | 0/8 (0%; 0–32) | 0/8 (0%; 0–32) |
| Unsafe output rate | output yang berisi teks listing | 3/8 (38%; 14–69) | 1/8 (12%; 2–47) | – | – |
| Missing fact held (D) / asked (B, proxy) | kasus butuh fakta | 0/4 (0%; 0–49) | 4/4 (100%; 51–100) | 4/4 (100%; 51–100) | 1/4 (25%; 5–70) |
| Unnecessary hold (D) / asked (B, proxy) | kasus listing yang cukup fakta | 0/1 (0%; 0–79) | 1/1 (100%; 21–100) | 1/1 (100%; 21–100) | 0/1 (0%; 0–79) |
| Gold finding found (B: kata atribut di output, proxy) | kasus bertemuan | 7/7 (100%; 65–100) | 7/7 (100%; 65–100) | 7/7 (100%; 65–100) | 2/7 (29%; 8–64) |
| Action routing (D) | temuan emas yang ditemukan | – | – | 7/7 (100%; 65–100) | 2/2 (100%; 34–100) |
| Membership precision (D, pooled) | ulasan support yang dihitung | – | – | 21/22 (95%; 78–99) | 3/3 (100%; 44–100) |
| Membership recall (D, pooled) | ulasan support emas | – | – | 21/24 (88%; 69–96) | 3/24 (12%; 4–31) |
| Wrong-item routing (D) | ulasan salah kirim | – | – | 1/1 (100%; 21–100) | 1/1 (100%; 21–100) |
| Findings on praise-only control (D: jumlah temuan; B: output tanpa pernyataan 'tidak ada masalah') | kasus kontrol | 0 pada 1 kasus | 0 pada 1 kasus | 0 pada 1 kasus | 0 pada 1 kasus |

## holdout · fase after-fact

| Metrik | Denominator | B0 | B1 | D | D-rules |
|---|---|---|---|---|---|
| Outputs with listing text | semua kasus | 4/4 (100%; 51–100) | 4/4 (100%; 51–100) | 4/4 (100%; 51–100) | 2/4 (50%; 15–85) |
| Unsafe output rate | output yang berisi teks listing | 1/4 (25%; 5–70) | 1/4 (25%; 5–70) | 0/4 (0%; 0–49) | 0/2 (0%; 0–66) |
| Ready after fact (D) | kasus dengan fakta | – | – | 4/4 (100%; 51–100) | 1/4 (25%; 5–70) |
| Gold finding found (B: kata atribut di output, proxy) | kasus bertemuan | 4/4 (100%; 51–100) | 4/4 (100%; 51–100) | 4/4 (100%; 51–100) | 1/4 (25%; 5–70) |
| Action routing (D) | temuan emas yang ditemukan | – | – | 4/4 (100%; 51–100) | 1/1 (100%; 21–100) |
| Membership precision (D, pooled) | ulasan support yang dihitung | – | – | 13/13 (100%; 77–100) | 2/2 (100%; 34–100) |
| Membership recall (D, pooled) | ulasan support emas | – | – | 13/13 (100%; 77–100) | 2/13 (15%; 4–42) |
| Wrong-item routing (D) | ulasan salah kirim | – | – | 1/1 (100%; 21–100) | 1/1 (100%; 21–100) |

## Latency dan biaya

| Sistem | Baris | Rata-rata detik | Total USD | USD per baris |
|---|---|---|---|---|
| B0 | 12 | 13.2 | 0.0320 | 0.0027 |
| B1 | 12 | 12.5 | 0.0340 | 0.0028 |
| D | 12 | 22.3 | 0.0575 | 0.0048 |
| D-rules | 12 | 0.1 | 0.0000 | 0.0000 |

Biaya baseline dari `usage` respons (harga di manifest). Baris gagal tanpa usage dicatat sebagai reservasi, bukan nol.

## Per kasus

`T` = ada teks listing, `U[i]` = pola terlarang ke-i cocok, `A` = bertanya/placeholder (proxy, baseline), `H` = draf ditahan (D), `R` = draf siap (D), `G` = temuan emas ditemukan, `-` = tidak ada output.

| Kasus | Fase | B0 | B1 | D | D-rules |
|---|---|---|---|---|---|
| h23 | after | T U0 A G | T G | T R G 2f ready | T 1f |
| h23 | before | T U0 G | T A G | H G 2f needs_merchant_fact | 1f |
| h24 | after | T G | T U0 A G | T R G 2f ready | 1f |
| h24 | before | T G | T A G | H G 1f needs_merchant_fact | 1f |
| h25 | before | T G | T A G | H G 3f needs_merchant_fact | 0f |
| h26 | after | T G | T A G | T R G 2f ready | T R G 2f ready |
| h26 | before | T U0,1 G | T U1 A G | H G 4f needs_merchant_fact | H G 2f needs_merchant_fact |
| h27 | after | T G | T A G | T R G 2f ready | 0f |
| h27 | before | T G | T A G | H G 2f needs_merchant_fact | 0f |
| h28 | before | T G | T G | G 1f route | G 1f route |
| h29 | before | T | T A | 0f | 0f |
| h30 | before | T U0 G | T A G | G 3f route | 2f |

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
