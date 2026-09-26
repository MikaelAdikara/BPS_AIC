#!/bin/bash
# Seed berjalan di latar belakang: menunggu wp-config (dibuat entrypoint resmi) dan database,
# lalu memasang toko. Apache langsung melayani; healthcheck baru hijau setelah seed selesai.
set -e
rm -f /tmp/deciqo-ready
/opt/deciqo/seed.sh > /proc/1/fd/1 2>&1 &
exec docker-entrypoint.sh "$@"
