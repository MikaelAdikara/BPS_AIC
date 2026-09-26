"""Bentuk error tunggal untuk semua endpoint Deciqo.

Klien menerjemahkan berdasarkan `code` (EN/ID) dan memakai `message` hanya sebagai cadangan, jadi
kode harus stabil dan pesan tidak pernah memuat stack trace atau isi data pengguna.
"""

from __future__ import annotations

from fastapi import HTTPException


class DeciqoError(HTTPException):
    def __init__(self, status: int, code: str, message: str):
        super().__init__(status_code=status, detail={"code": code, "message": message})
        self.code = code


def not_found(what: str = "item") -> DeciqoError:
    # Data akun lain juga 404, bukan 403: keberadaannya tidak boleh bocor.
    return DeciqoError(404, "not_found", f"The {what} was not found.")


def unauthorized() -> DeciqoError:
    return DeciqoError(401, "not_signed_in", "Please sign in to continue.")
