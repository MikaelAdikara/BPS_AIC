"""Menulis holdout ketiga (h23–h30) ke eval/final/cases_holdout3.jsonl.

Ditulis 26 Sep 2026 setelah gap-v1.13 dikodekan tetapi SEBELUM gap-v1.13 dijalankan pada kasus
apa pun, lalu dikunci dengan SHA-256 di eval/final/cases_holdout3.lock. Holdout kedua (h11–h22)
sudah dipakai mendiagnosis gap-v1.13, jadi statusnya kini regresi; holdout ketiga inilah uji
segar pertama gap-v1.13. Penulisnya sama dengan yang memperbaiki engine (bukan independen).
"""

from __future__ import annotations

import json
from pathlib import Path

from make_holdout2 import WARRANTY, case, rv

OUT = Path(__file__).resolve().parent / "final" / "cases_holdout3.jsonl"

CASES = [
    case("h23", ["missing_fact", "hidden_high_star", "informal"],
         "Tripod HP Portable dengan Remote",
         "Tripod HP ringan bahan aluminium, kaki bisa dipanjangkan, dilengkapi remote bluetooth dan holder HP.",
         [rv(1, 2, "pendek banget, kirain bisa setinggi badan", "2026-08-03"),
          rv(2, 3, "buat video berdiri harus ditaruh di meja dulu, ga nyampe tinggi kepala", "2026-08-07"),
          rv(3, 5, "remotenya nyambung cepet, mantap", "2026-08-11"),
          rv(4, 4, "kokoh, cuma tinggi maksimalnya kurang, deskripsi ga nyebut berapa cm", "2026-08-15"),
          rv(5, 5, "ringan gampang dibawa", "2026-08-19"),
          rv(6, 1, "holder hp nya longgar, hp ku jatoh", "2026-08-23"),
          rv(7, 3, "harusnya dicantumin tinggi maksimal, aku kira 1,5 meter", "2026-08-27")],
         {"attribute_words": ["tinggi", "height", "panjang", "maksimal", "max", "cm", "meter"], "route": "listing",
          "finding_type": "missing_fact", "supports": ["r1", "r2", "r4", "r7"],
          "not_supports": ["r3", "r5", "r6"], "fact_needed": True},
         fact="tinggi maksimal 102 cm, tinggi terlipat 26 cm",
         fb=[r"(?i)\b\d{2,3}(?:[.,]\d+)?\s*(?:cm|meter|m)\b"],
         fa=[r"(?i)\b(?:150|1[.,]5)\s*(?:cm|meter|m)\b"]),

    case("h24", ["capacity_conflict", "informal"],
         "Tumbler Stainless 500ml Tahan Panas 12 Jam",
         "Tumbler stainless steel double wall 500ml. Tahan panas 12 jam dan tahan dingin 24 jam. Tutup anti tumpah.",
         [rv(1, 2, "katanya 12 jam, baru 4 jam udah anget kuku", "2026-08-02"),
          rv(2, 1, "air panas pagi siangnya udah dingin, ga sesuai klaim", "2026-08-06"),
          rv(3, 5, "desainnya cakep, pas di cup holder mobil", "2026-08-10"),
          rv(4, 4, "es batu masih ada sampe sore, oke", "2026-08-14"),
          rv(5, 3, "panasnya ga awet, paling 5 jam", "2026-08-18"),
          rv(6, 5, "tutupnya rapet beneran ga tumpah", "2026-08-22"),
          rv(7, 5, "panasnya awet seharian, sesuai deskripsi", "2026-08-26")],
         {"attribute_words": ["panas", "hot", "heat", "jam", "tahan", "suhu", "insulat", "thermal", "retention"],
          "route": "listing", "finding_type": "conflicting_fact", "supports": ["r1", "r2", "r5"],
          "not_supports": ["r3", "r4", "r6", "r7"], "contradicts": ["r7"], "fact_needed": True},
         fact="menjaga air panas di atas 60 derajat Celsius selama sekitar 6 jam",
         fb=[r"(?i)\b(?:4|5|8|10)\s*jam\b"],
         fa=[r"(?i)\b(?:4|5|8|10|12)\s*jam\b.{0,20}panas|panas.{0,20}\b(?:4|5|8|10|12)\s*jam\b"]),

    case("h25", ["water_claims", "negation", "informal"],
         "Smartwatch Sport IP68",
         "Smartwatch sport layar 1.8 inch, tahan air IP68 untuk cipratan dan hujan, tidak untuk berenang atau mandi air panas.",
         [rv(1, 1, "dipake renang langsung embun di layar, katanya tahan air", "2026-08-01"),
          rv(2, 2, "kemasukan air pas mandi, sekarang layarnya burem", "2026-08-05"),
          rv(3, 5, "kena hujan aman, masih normal", "2026-08-09"),
          rv(4, 4, "fitur olahraganya lengkap", "2026-08-13"),
          rv(5, 2, "kirain ip68 bisa dibawa diving, ternyata engga", "2026-08-17"),
          rv(6, 5, "baterai tahan 5 hari", "2026-08-21")],
         {"attribute_words": ["air", "water", "ip68", "renang", "swim", "tahan air", "waterproof"],
          "route": "listing", "finding_type": "expectation_mismatch", "supports": ["r1", "r2", "r5"],
          "not_supports": ["r3", "r4", "r6"], "contradicts": ["r3"], "fact_needed": False},
         fb=[r"(?i)\b\d+\s*atm\b", r"(?i)(?<!tidak )(?<!bukan )(?:bisa|aman)\s*(?:untuk\s*)?(?:berenang|renang|diving|menyelam)",
             r"(?i)(?<!not )\bwaterproof\b"]),

    case("h26", ["size_chart_variant", "wrong_item", "informal"],
         "Sepatu Sneakers Pria Canvas",
         "Sepatu sneakers canvas, sol karet anti slip. Ukuran tersedia 39 sampai 44.",
         [rv(1, 2, "ukurannya kecilan, biasa 42 ini harus 43", "2026-08-02", "42"),
          rv(2, 3, "sempit di jari, mending naik 1 nomor", "2026-08-06", "41"),
          rv(3, 1, "pesen 43 yang dateng 41", "2026-08-10", "43"),
          rv(4, 5, "solnya empuk, enak buat jalan", "2026-08-14", "40"),
          rv(5, 4, "pas di kaki, sesuai size biasa", "2026-08-18", "42"),
          rv(6, 3, "ga ada panjang insole nya, jadi nebak2 ukuran", "2026-08-22", "44"),
          rv(7, 5, "jahitan rapi", "2026-08-26", "43")],
         {"attribute_words": ["ukuran", "size", "nomor", "insole", "panjang", "chart", "tabel"],
          "route": "listing", "finding_type": "missing_fact", "supports": ["r1", "r2", "r6"],
          "not_supports": ["r3", "r4", "r5", "r7"], "contradicts": ["r5"], "ops_reviews": ["r3"],
          "wrong_item_reviews": ["r3"], "fact_needed": True},
         fact="panjang insole: 39 = 24,5 cm; 40 = 25 cm; 41 = 25,5 cm; 42 = 26 cm; 43 = 26,5 cm; 44 = 27 cm",
         fb=[r"(?i)\b2\d(?:[.,]\d)?\s*cm\b", r"(?i)insole\D{0,15}\d"],
         fa=[r"(?i)\b(?:28|23)(?:[.,]\d)?\s*cm\b"]),

    case("h27", ["capacity_conflict", "informal"],
         "Lampu LED Bohlam 12W 1000 Lumen",
         "Lampu LED 12W setara 100W, 1000 lumen, cahaya putih 6500K, fitting E27.",
         [rv(1, 2, "redup bgt, ga kaya 100 watt", "2026-08-03"),
          rv(2, 1, "katanya 1000 lumen tapi terangnya kalah sama lampu 8w ku yg lama", "2026-08-07"),
          rv(3, 5, "terang banget, sesuai deskripsi", "2026-08-11"),
          rv(4, 4, "pengiriman cepat, dibungkus rapi", "2026-08-15"),
          rv(5, 3, "cahayanya remang2 buat ruang tamu", "2026-08-19"),
          rv(6, 2, "baru 2 minggu udah kedip2", "2026-08-23"),
          rv(7, 5, "hemat listrik", "2026-08-27")],
         {"attribute_words": ["terang", "brightness", "lumen", "redup", "cahaya", "watt"], "route": "listing",
          "finding_type": "conflicting_fact", "supports": ["r1", "r2", "r5"],
          "not_supports": ["r3", "r4", "r6", "r7"], "contradicts": ["r3"], "quality_reviews": ["r6"],
          "fact_needed": True},
         fact="terukur sekitar 850 lumen; setara lampu pijar 75W",
         fb=[r"(?i)\b(?!1000)\d{3,4}\s*lumen\b", r"(?i)setara\D{0,10}(?!100)\d{2,3}\s*w"],
         fa=[r"(?i)\b1000\s*lumen\b", r"(?i)setara\D{0,10}100\s*w"]),

    case("h28", ["delivery", "informal"],
         "Mouse Pad Gaming XL",
         "Mouse pad gaming ukuran 80 x 30 cm, permukaan speed, jahitan tepi, alas karet anti slip.",
         [rv(1, 1, "chat ga dibales 3 hari, pas nanya resi", "2026-08-02"),
          rv(2, 2, "admin slow respon, komplain ga ditanggepin", "2026-08-06"),
          rv(3, 5, "permukaannya licin enak buat gaming", "2026-08-10"),
          rv(4, 4, "jahitan tepinya rapi", "2026-08-14"),
          rv(5, 2, "nanya stok ga dijawab, akhirnya asal checkout", "2026-08-18"),
          rv(6, 5, "anti slipnya beneran nempel", "2026-08-22")],
         {"attribute_words": ["respon", "response", "chat", "seller", "penjual", "admin", "balas", "service",
                              "pelayanan", "communication", "komunikasi"],
          "route": "operations", "finding_type": "operational", "supports": ["r1", "r2", "r5"],
          "not_supports": ["r3", "r4", "r6"], "ops_reviews": ["r1", "r2", "r5"], "fact_needed": False},
         fb=[WARRANTY, r"(?i)\b(?!80\s*x\s*30)\d{2,3}\s*x\s*\d{2,3}\s*cm"]),

    case("h29", ["praise_only", "praise_low_star", "negation"],
         "Stand Laptop Aluminium Adjustable",
         "Stand laptop aluminium, tinggi bisa diatur 6 level, untuk laptop 10–17 inch, lipat.",
         [rv(1, 3, "ga goyang sama sekali, kokoh", "2026-08-03"),
          rv(2, 5, "laptop 15 inch muat pas", "2026-08-08"),
          rv(3, 4, "ga ada lecet, packing aman", "2026-08-13"),
          rv(4, 3, "sesuai foto, ga nyesel", "2026-08-18"),
          rv(5, 5, "bisa dilipat kecil, praktis dibawa", "2026-08-23"),
          rv(6, 4, "leher ga pegel lagi", "2026-08-28")],
         {"attribute_words": [], "route": "none", "finding_type": "none", "supports": [],
          "not_supports": ["r1", "r2", "r3", "r4", "r5", "r6"], "fact_needed": False},
         fb=[WARRANTY, r"(?i)\b(?:18|19|20)\s*inch\b"]),

    case("h30", ["quality", "hidden_high_star", "delivery", "informal"],
         "Headphone Bluetooth Over Ear",
         "Headphone bluetooth over ear, bass kuat, baterai hingga 30 jam, busa telinga lembut, bisa dilipat.",
         [rv(1, 4, "suaranya mantap, sayang busanya mulai ngelupas bulan kedua", "2026-06-02"),
          rv(2, 2, "busa kupingnya kelupas2 kaya kulit jeruk", "2026-06-09"),
          rv(3, 5, "bass nya nendang", "2026-06-16"),
          rv(4, 5, "enak dipake lama, cuma earcup nya udah retak kulitnya", "2026-06-23"),
          rv(5, 3, "pengiriman lama banget", "2026-06-30"),
          rv(6, 5, "baterai awet beneran", "2026-07-07"),
          rv(7, 1, "3 bulan pemakaian kulit busanya hancur semua", "2026-07-14"),
          rv(8, 4, "nyaman di kepala", "2026-07-21"),
          rv(9, 5, "koneksi stabil", "2026-07-28"),
          rv(10, 2, "bantalan telinga sobek di jahitan", "2026-08-04"),
          rv(11, 5, "harga segini kualitas top", "2026-08-11"),
          rv(12, 4, "suara jernih, cuma pas dilipat engselnya bunyi krek", "2026-08-18")],
         {"attribute_words": ["busa", "ear", "cushion", "bantalan", "kulit", "earcup", "pad", "mengelupas",
                              "peel"],
          "route": "quality", "finding_type": "product_quality", "supports": ["r1", "r2", "r4", "r7", "r10"],
          "not_supports": ["r3", "r5", "r6", "r8", "r9", "r11", "r12"], "ops_reviews": ["r5"],
          "fact_needed": False},
         fb=[WARRANTY, r"(?i)\b(?:40|50|60)\s*jam\b", r"(?i)anti\s*(?:sobek|mengelupas|kelupas)|kulit\s*asli|genuine\s*leather"]),
]


def main() -> None:
    OUT.write_text("".join(json.dumps(c, ensure_ascii=False) + "\n" for c in CASES), encoding="utf-8")
    print(f"{len(CASES)} kasus -> {OUT}")


if __name__ == "__main__":
    main()
