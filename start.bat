@echo off
REM Deciqo - jalankan lokal di Windows. Butuh Docker Desktop yang sedang berjalan.
cd /d "%~dp0"
if not exist .env copy .env.example .env >nul
for /f %%i in ('git rev-parse --short HEAD 2^>nul') do set APP_COMMIT=%%i
docker compose up --build -d
if errorlevel 1 (
  echo Docker Compose gagal. Pastikan Docker Desktop berjalan.
  pause
  exit /b 1
)
start "" http://localhost:3000
