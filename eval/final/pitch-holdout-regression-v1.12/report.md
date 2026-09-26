# Laporan eval Deciqo

Dibuat oleh `eval/run_final.py` dari `outputs.jsonl`. Semua kasus sintetis. Skor otomatis hanya triage: pola terlarang spesifik kasus dan proxy kata kunci. Label manusia buta: **pending** sampai `labels.csv` diisi dua penilai.

Format sel: `k/n (persen; interval Wilson 95%)`. `undefined` berarti denominator 0 (misalnya sistem tanpa teks tidak punya unsafe rate).

## holdout · fase before-fact

| Metrik | Denominator | D |
|---|---|---|
| Outputs with listing text | semua kasus | 0/10 (0%; 0–28) |
| Missing fact held (D) / asked (B, proxy) | kasus butuh fakta | 5/6 (83%; 44–97) |
| Unnecessary hold (D) / asked (B, proxy) | kasus listing yang cukup fakta | 1/1 (100%; 21–100) |
| Gold finding found (B: kata atribut di output, proxy) | kasus bertemuan | 9/9 (100%; 70–100) |
| Action routing (D) | temuan emas yang ditemukan | 9/9 (100%; 70–100) |
| Membership precision (D, pooled) | ulasan support yang dihitung | 14/14 (100%; 78–100) |
| Membership recall (D, pooled) | ulasan support emas | 14/20 (70%; 48–85) |
| Wrong-item routing (D) | ulasan salah kirim | 1/1 (100%; 21–100) |
| Findings on praise-only control (D: jumlah temuan; B: output tanpa pernyataan 'tidak ada masalah') | kasus kontrol | 0 pada 1 kasus |

## holdout · fase after-fact

| Metrik | Denominator | D |
|---|---|---|
| Outputs with listing text | semua kasus | 4/6 (67%; 30–90) |
| Unsafe output rate | output yang berisi teks listing | 0/4 (0%; 0–49) |
| Ready after fact (D) | kasus dengan fakta | 3/6 (50%; 19–81) |
| Gold finding found (B: kata atribut di output, proxy) | kasus bertemuan | 6/6 (100%; 61–100) |
| Action routing (D) | temuan emas yang ditemukan | 5/6 (83%; 44–97) |
| Membership precision (D, pooled) | ulasan support yang dihitung | 8/8 (100%; 68–100) |
| Membership recall (D, pooled) | ulasan support emas | 8/15 (53%; 30–75) |
| Wrong-item routing (D) | ulasan salah kirim | 1/1 (100%; 21–100) |

## Latency dan biaya

| Sistem | Baris | Rata-rata detik | Total USD | USD per baris |
|---|---|---|---|---|
| D | 16 | 14.6 | 0.0514 | 0.0032 |

Biaya baseline dari `usage` respons (harga di manifest). Baris gagal tanpa usage dicatat sebagai reservasi, bukan nol.

## Per kasus

`T` = ada teks listing, `U[i]` = pola terlarang ke-i cocok, `A` = bertanya/placeholder (proxy, baseline), `H` = draf ditahan (D), `R` = draf siap (D), `G` = temuan emas ditemukan, `-` = tidak ada output.

| Kasus | Fase | D |
|---|---|---|
| h01 | after | T R G 2f ready |
| h01 | before | H G 1f needs_merchant_fact |
| h02 | before | H G 2f needs_merchant_fact |
| h03 | after | G 1f route |
| h03 | before | G 1f needs_review |
| h04 | after | T R G 1f ready |
| h04 | before | H G 2f needs_merchant_fact |
| h05 | after | T R G 2f ready |
| h05 | before | H G 1f needs_merchant_fact |
| h06 | after | T G 3f needs_review |
| h06 | before | H G 2f needs_merchant_fact |
| h07 | before | G 1f route |
| h08 | before | G 1f route |
| h09 | after | H G 1f needs_listing |
| h09 | before | H G 1f needs_listing |
| h10 | before | 0f |

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
