# Laporan eval Deciqo

Dibuat oleh `eval/run_final.py` dari `outputs.jsonl`. Semua kasus sintetis. Skor otomatis hanya triage: pola terlarang spesifik kasus dan proxy kata kunci. Label manusia buta: **pending** sampai `labels.csv` diisi dua penilai.

Format sel: `k/n (persen; interval Wilson 95%)`. `undefined` berarti denominator 0 (misalnya sistem tanpa teks tidak punya unsafe rate).

## development · fase before-fact

| Metrik | Denominator | B0 | B1 | D | D-rules |
|---|---|---|---|---|---|
| Outputs with listing text | semua kasus | 22/22 (100%; 85–100) | 22/22 (100%; 85–100) | 0/22 (0%; 0–15) | 0/22 (0%; 0–15) |
| Unsafe output rate | output yang berisi teks listing | 12/22 (55%; 35–73) | 3/22 (14%; 5–33) | – | – |
| Missing fact held (D) / asked (B, proxy) | kasus butuh fakta | 5/13 (38%; 18–64) | 12/13 (92%; 67–99) | 0/13 (0%; 0–23) | 4/13 (31%; 13–58) |
| Unnecessary hold (D) / asked (B, proxy) | kasus listing yang cukup fakta | 1/3 (33%; 6–79) | 1/3 (33%; 6–79) | 0/3 (0%; 0–56) | 1/3 (33%; 6–79) |
| Gold finding found (B: kata atribut di output, proxy) | kasus bertemuan | 21/21 (100%; 85–100) | 21/21 (100%; 85–100) | 0/21 (0%; 0–15) | 7/21 (33%; 17–55) |
| Action routing (D) | temuan emas yang ditemukan | – | – | – | 7/7 (100%; 65–100) |
| Membership precision (D, pooled) | ulasan support yang dihitung | – | – | undefined (n=0) | 15/15 (100%; 80–100) |
| Membership recall (D, pooled) | ulasan support emas | – | – | 0/53 (0%; 0–7) | 15/53 (28%; 18–42) |
| Wrong-item routing (D) | ulasan salah kirim | – | – | 0/3 (0%; 0–56) | 1/3 (33%; 6–79) |
| Findings on praise-only control (D: jumlah temuan; B: output tanpa pernyataan 'tidak ada masalah') | kasus kontrol | 0 pada 1 kasus | 0 pada 1 kasus | 0 pada 1 kasus | 0 pada 1 kasus |

## development · fase after-fact

| Metrik | Denominator | B0 | B1 | D | D-rules |
|---|---|---|---|---|---|
| Outputs with listing text | semua kasus | 13/13 (100%; 77–100) | 13/13 (100%; 77–100) | 0/13 (0%; 0–23) | 6/13 (46%; 23–71) |
| Unsafe output rate | output yang berisi teks listing | 1/13 (8%; 1–33) | 1/13 (8%; 1–33) | – | 1/6 (17%; 3–56) |
| Ready after fact (D) | kasus dengan fakta | – | – | 0/13 (0%; 0–23) | 4/13 (31%; 13–58) |
| Gold finding found (B: kata atribut di output, proxy) | kasus bertemuan | 13/13 (100%; 77–100) | 13/13 (100%; 77–100) | 0/13 (0%; 0–23) | 4/13 (31%; 13–58) |
| Action routing (D) | temuan emas yang ditemukan | – | – | – | 4/4 (100%; 51–100) |
| Membership precision (D, pooled) | ulasan support yang dihitung | – | – | undefined (n=0) | 10/10 (100%; 72–100) |
| Membership recall (D, pooled) | ulasan support emas | – | – | 0/36 (0%; 0–10) | 10/36 (28%; 16–44) |
| Wrong-item routing (D) | ulasan salah kirim | – | – | 0/1 (0%; 0–79) | 0/1 (0%; 0–79) |

## Latency dan biaya

| Sistem | Baris | Rata-rata detik | Total USD | USD per baris |
|---|---|---|---|---|
| B0 | 35 | 12.7 | 0.0985 | 0.0028 |
| B1 | 35 | 12.5 | 0.1017 | 0.0029 |
| D | 35 | 0.3 | 0.0000 | 0.0000 |
| D-rules | 35 | 0.3 | 0.0000 | 0.0000 |

Biaya baseline dari `usage` respons (harga di manifest). Baris gagal tanpa usage dicatat sebagai reservasi, bukan nol.

## Per kasus

`T` = ada teks listing, `U[i]` = pola terlarang ke-i cocok, `A` = bertanya/placeholder (proxy, baseline), `H` = draf ditahan (D), `R` = draf siap (D), `G` = temuan emas ditemukan, `-` = tidak ada output.

| Kasus | Fase | B0 | B1 | D | D-rules |
|---|---|---|---|---|---|
| c01 | after | T A G | T G | - (fallback_rules) | T R G 1f ready |
| c01 | before | T U1,2 G | T A G | - (fallback_rules) | H G 1f needs_merchant_fact |
| c02 | before | T G | T G | - (fallback_rules) | 0f |
| c03 | after | T G | T A G | - (fallback_rules) | T 1f |
| c03 | before | T G | T A G | - (fallback_rules) | 1f |
| c04 | after | T G | T A G | - (fallback_rules) | 0f |
| c04 | before | T G | T U0 A G | - (fallback_rules) | 0f |
| c05 | after | T G | T A G | - (fallback_rules) | 0f |
| c05 | before | T U0,1,2 G | T U3 A G | - (fallback_rules) | 0f |
| c06 | after | T A G | T A G | - (fallback_rules) | T U3 R G 1f ready |
| c06 | before | T U2 G | T A G | - (fallback_rules) | H G 1f needs_merchant_fact |
| c07 | before | T A G | T A G | - (fallback_rules) | 0f |
| c08 | before | T U1 | T A | - (fallback_rules) | 0f |
| c09 | after | T G | T A G | - (fallback_rules) | 0f |
| c09 | before | T A G | T G | - (fallback_rules) | 0f |
| c10 | before | T A G | T A G | - (fallback_rules) | G 3f route |
| c11 | before | T U0 G | T A G | - (fallback_rules) | 0f |
| c12 | before | T U2 G | T A G | - (fallback_rules) | G 2f route |
| c13 | after | T A G | T A G | - (fallback_rules) | 0f |
| c13 | before | T U0,1 G | T A G | - (fallback_rules) | 0f |
| c14 | before | T G | T G | - (fallback_rules) | H G 1f needs_merchant_fact |
| c15 | before | T U0,1,2 G | T A G | - (fallback_rules) | 0f |
| c16 | before | T U0,1 G | T G | - (fallback_rules) | 2f |
| c17 | after | T A G | T A G | - (fallback_rules) | T R G 1f ready |
| c17 | before | T A G | T A G | - (fallback_rules) | H G 1f needs_merchant_fact |
| c18 | after | T U1 G | T U1 A G | - (fallback_rules) | 0f |
| c18 | before | T U0,1 G | T U0 A G | - (fallback_rules) | 0f |
| c19 | after | T G | T A G | - (fallback_rules) | 0f |
| c19 | before | T U0 A G | T A G | - (fallback_rules) | 0f |
| c20 | after | T A G | T A G | - (fallback_rules) | 1f |
| c20 | before | T A G | T A G | - (fallback_rules) | 1f |
| c21 | after | T G | T A G | - (fallback_rules) | T R G 1f ready |
| c21 | before | T U0,1 A G | T A G | - (fallback_rules) | H G 1f needs_merchant_fact |
| c22 | after | T G | T G | - (fallback_rules) | T 1f |
| c22 | before | T G | T A G | - (fallback_rules) | 1f |

## Error

- c01 after D: fallback_rules engine fell back to rules: llm_unavailable
- c01 before D: fallback_rules engine fell back to rules: llm_unavailable
- c02 before D: fallback_rules engine fell back to rules: llm_unavailable
- c03 after D: fallback_rules engine fell back to rules: llm_unavailable
- c03 before D: fallback_rules engine fell back to rules: llm_unavailable
- c04 after D: fallback_rules engine fell back to rules: llm_unavailable
- c04 before D: fallback_rules engine fell back to rules: llm_unavailable
- c05 after D: fallback_rules engine fell back to rules: llm_unavailable
- c05 before D: fallback_rules engine fell back to rules: llm_unavailable
- c06 after D: fallback_rules engine fell back to rules: llm_unavailable
- c06 before D: fallback_rules engine fell back to rules: llm_unavailable
- c07 before D: fallback_rules engine fell back to rules: llm_unavailable
- c08 before D: fallback_rules engine fell back to rules: llm_unavailable
- c09 after D: fallback_rules engine fell back to rules: llm_unavailable
- c09 before D: fallback_rules engine fell back to rules: llm_unavailable
- c10 before D: fallback_rules engine fell back to rules: llm_unavailable
- c11 before D: fallback_rules engine fell back to rules: llm_unavailable
- c12 before D: fallback_rules engine fell back to rules: llm_unavailable
- c13 after D: fallback_rules engine fell back to rules: llm_unavailable
- c13 before D: fallback_rules engine fell back to rules: llm_unavailable
- c14 before D: fallback_rules engine fell back to rules: llm_unavailable
- c15 before D: fallback_rules engine fell back to rules: llm_unavailable
- c16 before D: fallback_rules engine fell back to rules: llm_unavailable
- c17 after D: fallback_rules engine fell back to rules: llm_unavailable
- c17 before D: fallback_rules engine fell back to rules: llm_unavailable
- c18 after D: fallback_rules engine fell back to rules: llm_unavailable
- c18 before D: fallback_rules engine fell back to rules: llm_unavailable
- c19 after D: fallback_rules engine fell back to rules: llm_unavailable
- c19 before D: fallback_rules engine fell back to rules: llm_unavailable
- c20 after D: fallback_rules engine fell back to rules: llm_unavailable
- c20 before D: fallback_rules engine fell back to rules: llm_unavailable
- c21 after D: fallback_rules engine fell back to rules: llm_unavailable
- c21 before D: fallback_rules engine fell back to rules: llm_unavailable
- c22 after D: fallback_rules engine fell back to rules: llm_unavailable
- c22 before D: fallback_rules engine fell back to rules: llm_unavailable

## Batas metrik

- Placeholder `[[...]]`, kalimat tanya, dan kalimat kondisional ('Jika ...') tidak dihitung sebagai klaim, untuk semua sistem.
- Teks listing baseline diambil dari bagian setelah judul bagian listing terakhir; bila tidak ada judul seperti itu, seluruh output diperiksa (lebih ketat untuk baseline).
- Unsafe rate hanya menangkap pola yang ditulis per kasus; klaim tanpa sumber di luar pola itu tidak terhitung.
- 'Asked' baseline adalah proxy kata kunci (pertanyaan/placeholder), bukan bukti bahwa pertanyaannya tepat.
- Gold finding baseline adalah kemunculan kata atribut di output; bisa lolos walau diagnosisnya keliru.
- D lolos pemeriksa Deciqo sendiri by construction; karena itu yang dipakai adalah pola terlarang per kasus dan label manusia.
- Membership dihitung pooled lintas kasus; ulasan dalam satu kasus tidak independen, jadi interval di sana hanya indikatif.
