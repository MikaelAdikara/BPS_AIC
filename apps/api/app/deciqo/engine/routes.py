"""Endpoint engine: katalog, analisis, temuan, fakta, draf, keputusan, dan read model."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/deciqo", tags=["deciqo-engine"])
