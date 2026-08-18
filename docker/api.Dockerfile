# syntax=docker/dockerfile:1
# ------------------------------------------------------------------------------------
# InsightUlasan - API inference (blueprint bagian 30)
# CPU-only sebagai default. GPU dipakai otomatis kalau terdeteksi, tetapi tidak pernah
# menjadi syarat menjalankan sistem ini.
# ------------------------------------------------------------------------------------
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/cache/hf \
    TRANSFORMERS_OFFLINE=0

WORKDIR /app

# Torch varian CPU dipasang dari indeks terpisah SEBELUM requirements lain. Tanpa ini pip
# menarik roda CUDA (~2 GB) yang tidak terpakai di mesin tanpa GPU.
COPY apps/api/requirements.txt /tmp/requirements.txt
RUN pip install --index-url https://download.pytorch.org/whl/cpu "torch>=2.6" \
 && pip install -r /tmp/requirements.txt

# Kode disalin setelah dependensi supaya perubahan kode tidak membatalkan cache paket.
COPY apps/api /app/apps/api
COPY ml /app/ml
COPY configs /app/configs

# Hanya dua berkas data yang dibaca saat melayani request. Menyalin seluruh data/ akan
# ikut membawa dataset pelatihan ratusan MB yang tidak pernah disentuh runtime.
#   - category_baseline.json : pembanding kategori (BEN-01)
#   - demo_reviews.csv       : dataset contoh untuk juri yang tidak punya data sendiri
COPY data/processed/category_baseline.json /app/data/processed/category_baseline.json
COPY data/samples/demo_reviews.csv /app/data/samples/demo_reviews.csv

# Berjalan sebagai pengguna non-root: proses ini memproses berkas yang diunggah pengguna,
# dan tidak ada alasan ia perlu hak root untuk itu.
RUN useradd --create-home --uid 10001 appuser \
 && mkdir -p /cache/hf && chown -R appuser:appuser /app /cache
USER appuser

EXPOSE 8000

# 0.0.0.0 WAJIB. Mengikat ke 127.0.0.1 membuat proses hanya terjangkau dari dalam
# container itu sendiri, sehingga port yang dipetakan compose tidak pernah menjawab.
CMD ["uvicorn", "app.main:app", "--app-dir", "apps/api", "--host", "0.0.0.0", "--port", "8000"]
