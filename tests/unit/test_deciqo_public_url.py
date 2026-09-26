"""Tautan alert selalu memakai satu fragmen router aplikasi."""
from app.deciqo import settings


def test_public_url_removes_router_fragment(monkeypatch):
    monkeypatch.setenv("DECIQO_PUBLIC_URL", "http://localhost:3000/#/deciqo")
    assert settings.public_url() == "http://localhost:3000"
    monkeypatch.setenv("DECIQO_PUBLIC_URL", "https://example.test/shop/")
    assert settings.public_url() == "https://example.test/shop"
