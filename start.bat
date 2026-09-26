@echo off
setlocal EnableDelayedExpansion
REM Deciqo - jalankan lokal di Windows dengan sekali klik.
REM Menyalakan Docker Desktop bila belum jalan, build + start container, menunggu app siap,
REM lalu membuka browser. Hentikan dengan stop.bat (data tetap tersimpan di volume Docker).
cd /d "%~dp0"
title Deciqo - start

if not exist .env (
  copy .env.example .env >nul
  echo [.env] dibuat dari .env.example
)

REM --- 1. Pastikan Docker engine menjawab --------------------------------------------------
docker info >nul 2>&1
if not errorlevel 1 goto docker_ready

set "DOCKER_EXE="
for %%P in (
  "%ProgramFiles%\Docker\Docker\Docker Desktop.exe"
  "%LOCALAPPDATA%\Programs\DockerDesktop\Docker Desktop.exe"
  "%LOCALAPPDATA%\Docker\Docker Desktop.exe"
) do if not defined DOCKER_EXE if exist %%P set "DOCKER_EXE=%%~P"

if not defined DOCKER_EXE (
  echo Docker Desktop tidak ditemukan. Pasang dari https://www.docker.com/products/docker-desktop/
  pause
  exit /b 1
)

echo Menyalakan Docker Desktop...
start "" "%DOCKER_EXE%"
set /a TRIES=0
:wait_docker
set /a TRIES+=1
if %TRIES% gtr 90 (
  echo Docker Desktop belum siap setelah 3 menit. Buka Docker Desktop manual lalu jalankan ulang start.bat.
  pause
  exit /b 1
)
ping -n 3 127.0.0.1 >nul
docker info >nul 2>&1
if errorlevel 1 goto wait_docker

:docker_ready
echo Docker siap.

REM --- 2. Build + start ---------------------------------------------------------------------
set "APP_COMMIT=unknown"
for /f %%i in ('git rev-parse --short HEAD 2^>nul') do set "APP_COMMIT=%%i"
echo Build dan start container (commit %APP_COMMIT%). Build pertama bisa beberapa menit...
docker compose up --build -d
if errorlevel 1 (
  echo.
  echo Docker Compose gagal. Lihat pesan di atas, atau jalankan: docker compose logs
  pause
  exit /b 1
)

REM --- 3. Tunggu web + API menjawab ----------------------------------------------------------
echo Menunggu aplikasi siap...
set /a TRIES=0
:wait_app
set /a TRIES+=1
if %TRIES% gtr 90 (
  echo Aplikasi belum menjawab setelah 3 menit. Cek: docker compose ps  /  docker compose logs api
  pause
  exit /b 1
)
ping -n 3 127.0.0.1 >nul
curl -fs -o nul http://127.0.0.1:3000/api/v1/health >nul 2>&1
if errorlevel 1 goto wait_app

echo.
echo ============================================================
echo   Deciqo jalan di  http://localhost:3000
echo   API docs         http://localhost:8000/api/docs
echo   Akun demo        demo@deciqo.app / deciqo-demo
echo   Model IndoBERT dimuat di latar (~1 menit); app sudah bisa dipakai.
echo   Stop: stop.bat
echo ============================================================
start "" http://localhost:3000
endlocal
