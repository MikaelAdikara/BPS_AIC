@echo off
REM Deciqo - hentikan container. Data (akun, katalog, temuan) tetap di volume Docker.
REM Untuk menghapus database juga: docker compose down -v
cd /d "%~dp0"
docker compose down
pause
