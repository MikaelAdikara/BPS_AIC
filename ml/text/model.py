"""Definisi arsitektur NLP-01 - dipakai bersama oleh pelatihan dan inferensi.

Kelas ini semula tinggal di `finetune.py`. Memindahkannya bukan penataan kosmetik: pemuatan
checkpoint di `apps/api` harus meng-import kelasnya, dan meng-import `finetune` ikut menarik
seluruh dependensi pelatihan (pandas, sklearn.metrics, DataLoader). Di image API - yang
sengaja tidak memasang paket pelatihan (apps/api/requirements.txt) - import itu melempar
ModuleNotFoundError, tertangkap oleh penanganan fallback, dan sistem berjalan memakai leksikon
**tanpa satu pun pesan kesalahan yang terlihat pengguna**. Deployment Docker karenanya diam-diam
tidak pernah memakai model yang di-fine-tune sama sekali.

Modul ini hanya bergantung pada torch dan transformers, keduanya memang dependensi runtime.
"""

from __future__ import annotations

import sys
from pathlib import Path

import torch.nn as nn
from transformers import AutoModel

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lexicon import ALL_ASPECTS  # noqa: E402

MODEL_NAME = "indobenchmark/indobert-base-p1"
SENTIMENTS = ["negatif", "netral", "positif"]


class DualHeadClassifier(nn.Module):
    """Encoder IndoBERT bersama + dua head klasifikasi terpisah (bagian 18.1)."""

    def __init__(self, model_name: str = MODEL_NAME, n_aspects: int = len(ALL_ASPECTS)):
        super().__init__()
        self.encoder = AutoModel.from_pretrained(model_name)
        hidden = self.encoder.config.hidden_size
        self.dropout = nn.Dropout(0.1)
        self.aspect_head = nn.Linear(hidden, n_aspects)
        self.sentiment_head = nn.Linear(hidden, len(SENTIMENTS))

    def forward(self, input_ids, attention_mask):
        out = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        # Mean pooling atas token non-padding - lebih stabil dari [CLS] untuk teks pendek.
        mask = attention_mask.unsqueeze(-1).float()
        pooled = (out.last_hidden_state * mask).sum(1) / mask.sum(1).clamp(min=1e-9)
        pooled = self.dropout(pooled)
        return self.aspect_head(pooled), self.sentiment_head(pooled)
