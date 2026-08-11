"""VIS-01 — klasifikasi visual zero-shot dengan abstention (blueprint bagian 19.1-19.2).

Encoder **beku**, tidak dilatih dari nol. Yang dikustomisasi adalah prompt ensemble dan ambang
abstention-nya, sesuai keputusan bagian 19.1: dengan ~100 foto berlabel, melatih ulang encoder
hanya akan menghafal, bukan belajar.

**Abstention wajib, bukan opsional.** Model yang memaksakan label pada foto buram atau
terpotong akan memberi pemilik toko keyakinan palsu tepat pada kasus yang paling perlu ia
periksa sendiri. Dua ambang mengaturnya:

- `min_confidence` — probabilitas kelas teratas harus melewati ini
- `min_margin` — jarak ke kelas kedua harus melewati ini

Keduanya sengaja `null` di `configs/visual_classes.yaml` sejak Fase 0 dan baru diisi dari
distribusi skor nyata (lihat `evaluate_gate.py`), bukan dari angka bawaan yang enak dilihat.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import yaml

REPO = Path(__file__).resolve().parents[2]
CONFIG = REPO / "configs" / "visual_classes.yaml"

# CLIP dasar dipilih, bukan varian besar: seluruh sistem menargetkan CPU-only (bagian 30.3),
# dan varian besar menambah waktu muat berkali lipat untuk keuntungan yang belum terbukti
# pada foto ulasan Indonesia — persis hal yang sedang diuji gerbang ini.
DEFAULT_MODEL = "openai/clip-vit-base-patch32"


@dataclass
class VisualScore:
    """Hasil satu foto: probabilitas per kelas, plus keputusan abstain."""

    image_file: str
    probs: dict[str, float]
    top_label: str
    top_prob: float
    margin: float

    def decide(self, min_confidence: float, min_margin: float) -> str | None:
        """Label akhir, atau None bila sistem menolak menyimpulkan."""
        if self.top_prob < min_confidence or self.margin < min_margin:
            return None
        return self.top_label


def load_classes(path: Path = CONFIG) -> list[dict]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))["classes"]


class ZeroShotVisual:
    def __init__(self, model_name: str = DEFAULT_MODEL, prompt_lang: str = "all"):
        """`prompt_lang` menentukan varian prompt yang dipakai.

        CLIP dilatih dominan pada data berbahasa Inggris, sehingga prompt Bahasa Indonesia
        berpotensi justru mengencerkan sinyalnya. Opsi ini ada supaya dugaan itu dapat DIUKUR
        (`all` vs `en`), bukan diasumsikan ke salah satu arah.
        """
        self.model_name = model_name
        self.prompt_lang = prompt_lang
        self.classes = load_classes()
        self._model = None
        self._processor = None

    # ------------------------------------------------------------------ pemuatan
    def _ensure_loaded(self):
        if self._model is not None:
            return
        import torch
        from transformers import CLIPModel, CLIPProcessor

        self._torch = torch
        self._model = CLIPModel.from_pretrained(self.model_name).eval()
        self._processor = CLIPProcessor.from_pretrained(self.model_name)

    # ------------------------------------------------------------------ prompt
    @staticmethod
    def _is_english(text: str) -> bool:
        # Prompt Inggris pada konfigurasi selalu diawali artikel "a photo of".
        return text.lower().startswith(("a photo", "an photo", "a picture"))

    def _prompts_for(self, cls: dict) -> list[str]:
        prompts = list(cls["prompts_positive"])
        if self.prompt_lang == "en":
            hanya_en = [p for p in prompts if self._is_english(p)]
            # Kelas "normal" hanya punya prompt Indonesia; membuangnya akan menghapus kelasnya
            # sama sekali, jadi bila tidak ada varian Inggris, seluruh prompt tetap dipakai.
            return hanya_en or prompts
        return prompts

    # ------------------------------------------------------------------ skoring
    def score(self, image_paths: list[Path], batch_size: int = 16) -> list[VisualScore]:
        self._ensure_loaded()
        torch = self._torch
        from PIL import Image

        ids = [c["id"] for c in self.classes]
        per_class = [self._prompts_for(c) for c in self.classes]
        flat = [p for group in per_class for p in group]
        # Batas kelas pada daftar prompt yang sudah diratakan.
        spans, start = [], 0
        for group in per_class:
            spans.append((start, start + len(group)))
            start += len(group)

        def as_tensor(out):
            """transformers 5 mengembalikan objek keluaran, versi sebelumnya tensor langsung."""
            if hasattr(out, "pooler_output"):
                return out.pooler_output
            if hasattr(out, "last_hidden_state"):
                return out.last_hidden_state[:, 0]
            return out

        with torch.no_grad():
            tok = self._processor(text=flat, return_tensors="pt", padding=True)
            tfeat = as_tensor(self._model.get_text_features(**tok))
            tfeat = tfeat / tfeat.norm(dim=-1, keepdim=True)

            out: list[VisualScore] = []
            for i in range(0, len(image_paths), batch_size):
                chunk = image_paths[i : i + batch_size]
                images = [Image.open(p).convert("RGB") for p in chunk]
                pix = self._processor(images=images, return_tensors="pt")
                ifeat = as_tensor(self._model.get_image_features(**pix))
                ifeat = ifeat / ifeat.norm(dim=-1, keepdim=True)

                sims = (ifeat @ tfeat.T).cpu().numpy()  # (n_img, n_prompt)
                scale = float(self._model.logit_scale.exp())

                for row, path in zip(sims, chunk):
                    # Bagian 19.1: skor kelas = RATA-RATA seluruh varian promptnya, bukan
                    # satu prompt tunggal. Satu prompt yang kebetulan cocok tidak boleh
                    # menentukan keputusan sendirian.
                    kelas = np.array([row[a:b].mean() for a, b in spans])
                    logits = kelas * scale
                    e = np.exp(logits - logits.max())
                    probs = e / e.sum()
                    urut = np.argsort(-probs)
                    out.append(
                        VisualScore(
                            image_file=path.name,
                            probs={k: float(v) for k, v in zip(ids, probs)},
                            top_label=ids[urut[0]],
                            top_prob=float(probs[urut[0]]),
                            margin=float(probs[urut[0]] - probs[urut[1]]),
                        )
                    )
        return out
