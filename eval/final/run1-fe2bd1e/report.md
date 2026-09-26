# Laporan eval Deciqo

Dibuat oleh `eval/run_final.py` dari `outputs.jsonl`. Semua kasus sintetis. Skor otomatis hanya triage: pola terlarang spesifik kasus dan proxy kata kunci. Label manusia buta: **pending** sampai `labels.csv` diisi dua penilai.

Format sel: `k/n (persen; interval Wilson 95%)`. `undefined` berarti denominator 0 (misalnya sistem tanpa teks tidak punya unsafe rate).

## development · fase before-fact

| Metrik | Denominator | B0 | B1 |
|---|---|---|---|
| Outputs with listing text | semua kasus | 22/22 (100%; 85–100) | 22/22 (100%; 85–100) |
| Unsafe output rate | output yang berisi teks listing | 14/22 (64%; 43–80) | 8/22 (36%; 20–57) |
| Missing fact held (D) / asked (B, proxy) | kasus butuh fakta | 5/13 (38%; 18–64) | 12/13 (92%; 67–99) |
| Unnecessary hold (D) / asked (B, proxy) | kasus listing yang cukup fakta | 1/3 (33%; 6–79) | 1/3 (33%; 6–79) |
| Gold finding found (B: kata atribut di output, proxy) | kasus bertemuan | 21/21 (100%; 85–100) | 21/21 (100%; 85–100) |
| Findings on praise-only control (D: jumlah temuan; B: output tanpa pernyataan 'tidak ada masalah') | kasus kontrol | 0 pada 1 kasus | 1 pada 1 kasus |

## development · fase after-fact

| Metrik | Denominator | B0 | B1 |
|---|---|---|---|
| Outputs with listing text | semua kasus | 13/13 (100%; 77–100) | 13/13 (100%; 77–100) |
| Unsafe output rate | output yang berisi teks listing | 3/13 (23%; 8–50) | 3/13 (23%; 8–50) |
| Gold finding found (B: kata atribut di output, proxy) | kasus bertemuan | 13/13 (100%; 77–100) | 13/13 (100%; 77–100) |

## Latency dan biaya

| Sistem | Baris | Rata-rata detik | Total USD | USD per baris |
|---|---|---|---|---|
| B0 | 35 | 12.7 | 0.0985 | 0.0028 |
| B1 | 35 | 12.5 | 0.1017 | 0.0029 |

Biaya baseline dari `usage` respons (harga di manifest). Baris gagal tanpa usage dicatat sebagai reservasi, bukan nol.

## Per kasus

`T` = ada teks listing, `U[i]` = pola terlarang ke-i cocok, `A` = bertanya/placeholder (proxy, baseline), `H` = draf ditahan (D), `R` = draf siap (D), `G` = temuan emas ditemukan, `-` = tidak ada output.

| Kasus | Fase | B0 | B1 |
|---|---|---|---|
| c01 | after | T A G | T G |
| c01 | before | T U1,2 G | T A G |
| c02 | before | T G | T G |
| c03 | after | T G | T A G |
| c03 | before | T G | T A G |
| c04 | after | T G | T A G |
| c04 | before | T G | T U0 A G |
| c05 | after | T U1 G | T A G |
| c05 | before | T U0,1,2,3 G | T U0,1,3 A G |
| c06 | after | T A G | T A G |
| c06 | before | T U2 G | T A G |
| c07 | before | T U0 A G | T A G |
| c08 | before | T U1 | T U1 A |
| c09 | after | T G | T A G |
| c09 | before | T A G | T G |
| c10 | before | T A G | T A G |
| c11 | before | T U0 G | T A G |
| c12 | before | T U2 G | T U2 A G |
| c13 | after | T A G | T A G |
| c13 | before | T U0,1 G | T A G |
| c14 | before | T U0 G | T U0 G |
| c15 | before | T U0,1,2 G | T A G |
| c16 | before | T U0,1 G | T G |
| c17 | after | T A G | T A G |
| c17 | before | T A G | T A G |
| c18 | after | T U1 G | T U1 A G |
| c18 | before | T U0,1 G | T U0 A G |
| c19 | after | T G | T A G |
| c19 | before | T U0 A G | T A G |
| c20 | after | T A G | T U2 A G |
| c20 | before | T A G | T U2 A G |
| c21 | after | T G | T A G |
| c21 | before | T U0,1 A G | T A G |
| c22 | after | T U0 G | T U0,2 G |
| c22 | before | T G | T U2 A G |

## Error

Tidak ada.

## Batas metrik

- Teks listing baseline diambil dari bagian setelah judul bagian listing terakhir; bila tidak ada judul seperti itu, seluruh output diperiksa (lebih ketat untuk baseline).
- Unsafe rate hanya menangkap pola yang ditulis per kasus; klaim tanpa sumber di luar pola itu tidak terhitung.
- 'Asked' baseline adalah proxy kata kunci (pertanyaan/placeholder), bukan bukti bahwa pertanyaannya tepat.
- Gold finding baseline adalah kemunculan kata atribut di output; bisa lolos walau diagnosisnya keliru.
- D lolos pemeriksa Deciqo sendiri by construction; karena itu yang dipakai adalah pola terlarang per kasus dan label manusia.
- Membership dihitung pooled lintas kasus; ulasan dalam satu kasus tidak independen, jadi interval di sana hanya indikatif.
