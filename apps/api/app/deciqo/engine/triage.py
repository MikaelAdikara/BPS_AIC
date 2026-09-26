"""Triage: memilih ulasan yang dikirim ke discovery. Ini SELEKSI INPUT, bukan hitungan.

Sinyal keluhan = aspek negatif dari klasifier IndoBERT yang sudah ada di API (bila checkpoint
termuat) ATAU klausa keluhan menurut leksikon engine, apa pun bintangnya. Ulasan ★5 yang menulis
"bagus tapi agak sempit" harus ikut.

Hasil per ulasan di-cache di `reviews.triage_json` dengan kunci `version_hash` ulasan + versi
model, sehingga analisis ulang tidak menjalankan klasifier untuk ulasan yang tidak berubah.
"""

from __future__ import annotations

import logging
import os
import sys
from datetime import datetime, timezone

from .. import store
from . import lexicon

log = logging.getLogger("deciqo.engine.triage")

MAX_CANDIDATES = 45
MAX_CHARS = 600
LEXICON_ONLY = "lexicon-only"

_adapter = None
_adapter_checked = False


def set_text_adapter(adapter) -> None:
    """Dipakai tes/eval untuk memasang (atau melepas, dengan None) klasifier secara eksplisit."""
    global _adapter, _adapter_checked
    _adapter, _adapter_checked = adapter, True


def text_adapter():
    """Klasifier yang sudah dimuat API lama, tanpa memuat ulang checkpoint 500 MB.

    Proses lain (eval, tes) memakai leksikon saja kecuali `DECIQO_TRIAGE_LOAD_MODEL=true`."""
    global _adapter, _adapter_checked
    if _adapter_checked:
        return _adapter
    main = sys.modules.get("app.main")
    service = getattr(main, "state", {}).get("service") if main else None
    if service is not None:
        adapter = getattr(service, "text_adapter", None)
    elif os.getenv("DECIQO_TRIAGE_LOAD_MODEL", "").lower() in {"1", "true", "yes"}:
        from ...adapters.text_model import TextModelAdapter  # noqa: PLC0415

        adapter = TextModelAdapter()
    else:
        # API lama belum selesai memuat model (startup Deciqo berjalan lebih dulu): leksikon
        # untuk sekarang, dicek lagi pada analisis berikutnya.
        return None
    _adapter_checked = True
    _adapter = adapter if adapter is not None and getattr(adapter, "model", None) is not None else None
    return _adapter


def model_version() -> str:
    adapter = text_adapter()
    return getattr(adapter, "model_version", LEXICON_ONLY) if adapter else LEXICON_ONLY


def _indobert_negative(reviews: list[dict]) -> dict[str, list[str]]:
    adapter = text_adapter()
    if adapter is None or not reviews:
        return {}
    from ...schemas import Category, ProcessedReview  # noqa: PLC0415

    processed = [
        ProcessedReview(review_id=str(r["id"]), clean_text=r["text"], pii_redacted=True,
                        rating=r.get("rating"), category=Category.OTHER, has_image=False)
        for r in reviews
    ]
    try:
        predictions = adapter.classify(processed)
    except Exception as exc:  # noqa: BLE001 - triage turun ke leksikon, bukan gagal
        log.warning(f"klasifier triage gagal, memakai leksikon: {type(exc).__name__}")
        return {}
    out: dict[str, list[str]] = {}
    for pred in predictions:
        out[pred.review_id] = sorted({p.aspect.value for p in pred.predictions
                                      if p.sentiment.value == "negatif"})
    return out


def signals(reviews: list[dict], conn=None) -> dict[str, dict]:
    """Sinyal per ulasan: `{"lexicon": bool, "neg_aspects": [...], "model": str}`.

    Memakai cache `triage_json` bila `version_hash` dan versi model sama."""
    version = model_version()
    out: dict[str, dict] = {}
    todo: list[dict] = []
    for review in reviews:
        cached = store.loads(review.get("triage_json"), None)
        if (cached and cached.get("v") == review.get("version_hash") and cached.get("model") == version
                and cached.get("lexicon_version") == lexicon.LEXICON_VERSION):
            out[review["id"]] = cached
        else:
            todo.append(review)
    neural = _indobert_negative(todo) if version != LEXICON_ONLY else {}
    for review in todo:
        result = {
            "v": review.get("version_hash"),
            "model": version,
            "lexicon_version": lexicon.LEXICON_VERSION,
            # Pertanyaan pembeli ("1,8 liter itu air atau beras?") menandai informasi yang kurang
            # walau tidak ada kata keluhan; ini seleksi input, bukan hitungan.
            "lexicon": lexicon.complaint_signal(review["text"]) or "?" in review["text"],
            "neg_aspects": neural.get(str(review["id"]), []),
        }
        out[review["id"]] = result
        if conn is not None and review.get("product_id"):
            conn.execute("UPDATE reviews SET triage_json = ? WHERE product_id = ? AND id = ?",
                         (store.dumps(result), review["product_id"], review["id"]))
    return out


def _time_key(review: dict) -> float:
    parsed = store.parse_time(review.get("review_time"))
    return parsed.timestamp() if parsed else datetime.min.replace(tzinfo=timezone.utc).timestamp()


def candidates(reviews: list[dict], conn=None) -> tuple[list[dict], dict]:
    """Kandidat keluhan untuk discovery (≤45, teks dipotong) dan ringkasan untuk trace."""
    found = signals(reviews, conn)
    scored = []
    for review in reviews:
        s = found[review["id"]]
        strength = int(bool(s["lexicon"])) + int(bool(s["neg_aspects"]))
        if strength:
            scored.append((strength, _time_key(review), review))
    if len(reviews) <= MAX_CANDIDATES:
        # Seleksi hanya perlu bila ulasan lebih banyak dari yang bisa dibaca discovery. Produk kecil
        # dikirim utuh supaya keluhan yang kosakatanya belum dikenal leksikon ("ga sampe 20000",
        # "redup bgt") tetap sampai ke model; yang bersinyal tetap didahulukan.
        flagged = {id(r) for _, _, r in scored}
        scored += [(0, _time_key(r), r) for r in reviews if id(r) not in flagged]
    scored.sort(key=lambda item: (item[0], item[1]), reverse=True)
    picked = [{**r, "text": r["text"][:MAX_CHARS]} for _, _, r in scored[:MAX_CANDIDATES]]
    return picked, {"stage": "triage", "kept": len(picked), "of": len(reviews),
                    "signal": "indobert+lexicon" if model_version() != LEXICON_ONLY else "lexicon"}
