"""Outbox alert: kapan alert dibuat, isi pesannya (metadata saja), dan status kirimnya."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/deciqo", tags=["deciqo-alerts"])
