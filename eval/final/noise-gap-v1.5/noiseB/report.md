# Laporan eval Deciqo

Dibuat oleh `eval/run_final.py` dari `outputs.jsonl`. Semua kasus sintetis. Skor otomatis hanya triage: pola terlarang spesifik kasus dan proxy kata kunci. Label manusia buta: **pending** sampai `labels.csv` diisi dua penilai.

Format sel: `k/n (persen; interval Wilson 95%)`. `undefined` berarti denominator 0 (misalnya sistem tanpa teks tidak punya unsafe rate).

## development · fase before-fact

| Metrik | Denominator | D |
|---|---|---|
| Outputs with listing text | semua kasus | 0/22 (0%; 0–15) |
| Missing fact held (D) / asked (B, proxy) | kasus butuh fakta | 10/13 (77%; 50–92) |
| Unnecessary hold (D) / asked (B, proxy) | kasus listing yang cukup fakta | 3/3 (100%; 44–100) |
| Gold finding found (B: kata atribut di output, proxy) | kasus bertemuan | 17/21 (81%; 60–92) |
| Action routing (D) | temuan emas yang ditemukan | 17/17 (100%; 82–100) |
| Membership precision (D, pooled) | ulasan support yang dihitung | 25/25 (100%; 87–100) |
| Membership recall (D, pooled) | ulasan support emas | 25/53 (47%; 34–60) |
| Wrong-item routing (D) | ulasan salah kirim | 1/3 (33%; 6–79) |
| Findings on praise-only control (D: jumlah temuan; B: output tanpa pernyataan 'tidak ada masalah') | kasus kontrol | 0 pada 1 kasus |

## development · fase after-fact

| Metrik | Denominator | D |
|---|---|---|
| Outputs with listing text | semua kasus | 9/13 (69%; 42–87) |
| Unsafe output rate | output yang berisi teks listing | 1/9 (11%; 2–44) |
| Ready after fact (D) | kasus dengan fakta | 9/13 (69%; 42–87) |
| Gold finding found (B: kata atribut di output, proxy) | kasus bertemuan | 10/13 (77%; 50–92) |
| Action routing (D) | temuan emas yang ditemukan | 10/10 (100%; 72–100) |
| Membership precision (D, pooled) | ulasan support yang dihitung | 16/16 (100%; 81–100) |
| Membership recall (D, pooled) | ulasan support emas | 16/36 (44%; 30–60) |
| Wrong-item routing (D) | ulasan salah kirim | 0/1 (0%; 0–79) |

## Latency dan biaya

| Sistem | Baris | Rata-rata detik | Total USD | USD per baris |
|---|---|---|---|---|
| D | 35 | 13.9 | 0.0969 | 0.0028 |

Biaya baseline dari `usage` respons (harga di manifest). Baris gagal tanpa usage dicatat sebagai reservasi, bukan nol.

## Per kasus

`T` = ada teks listing, `U[i]` = pola terlarang ke-i cocok, `A` = bertanya/placeholder (proxy, baseline), `H` = draf ditahan (D), `R` = draf siap (D), `G` = temuan emas ditemukan, `-` = tidak ada output.

| Kasus | Fase | D |
|---|---|---|
| c01 | after | T R G 2f ready |
| c01 | before | H G 2f needs_merchant_fact |
| c02 | before | H G 1f needs_merchant_fact |
| c03 | after | T R G 2f ready |
| c03 | before | H G 2f needs_merchant_fact |
| c04 | after | 0f |
| c04 | before | 0f |
| c05 | after | T R G 2f ready |
| c05 | before | H G 1f needs_merchant_fact |
| c06 | after | T U3 R G 1f ready |
| c06 | before | H G 2f needs_merchant_fact |
| c07 | before | H G 1f needs_merchant_fact |
| c08 | before | 0f |
| c09 | after | T R G 1f ready |
| c09 | before | H G 1f needs_merchant_fact |
| c10 | before | G 3f route |
| c11 | before | G 1f route |
| c12 | before | G 2f route |
| c13 | after | 0f |
| c13 | before | 0f |
| c14 | before | H G 1f needs_merchant_fact |
| c15 | before | 0f |
| c16 | before | G 2f route |
| c17 | after | T R G 1f ready |
| c17 | before | H G 1f needs_merchant_fact |
| c18 | after | T R G 1f ready |
| c18 | before | H G 1f needs_merchant_fact |
| c19 | after | G 2f blocked |
| c19 | before | H G 1f needs_merchant_fact |
| c20 | after | 0f |
| c20 | before | 0f |
| c21 | after | T R G 2f ready |
| c21 | before | H G 1f needs_merchant_fact |
| c22 | after | T R G 1f ready |
| c22 | before | H G 1f needs_merchant_fact |

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
