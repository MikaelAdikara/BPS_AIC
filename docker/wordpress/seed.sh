#!/bin/bash
# Pasang dan isi toko demo. Idempoten: aman dijalankan setiap container start.
set -u
cd /var/www/html
wp() { command wp --allow-root --path=/var/www/html "$@"; }

for _ in $(seq 1 90); do
  if [ -f wp-config.php ] && php -r '
      $h = explode(":", getenv("WORDPRESS_DB_HOST"));
      $c = @new mysqli($h[0], getenv("WORDPRESS_DB_USER"), getenv("WORDPRESS_DB_PASSWORD"),
                       getenv("WORDPRESS_DB_NAME"), (int)($h[1] ?? 3306));
      exit($c->connect_errno ? 1 : 0);'; then
    break
  fi
  sleep 2
done

mkdir -p wp-content/mu-plugins
cp /opt/deciqo/mu-plugins/*.php wp-content/mu-plugins/
mkdir -p wp-content/languages
cp -r /opt/deciqo/languages/. wp-content/languages/
chown -R www-data:www-data wp-content/mu-plugins wp-content/languages

if ! wp core is-installed 2>/dev/null; then
  echo "[deciqo-seed] memasang WordPress"
  wp core install --url="${DECIQO_STORE_URL}" --title="${DECIQO_STORE_TITLE:-Toko Rumah Deciqo}" \
    --admin_user="${DECIQO_STORE_ADMIN_USER}" --admin_password="${DECIQO_STORE_ADMIN_PASSWORD}" \
    --admin_email="admin@toko-demo.test" --skip-email || exit 1
fi

# Password admin mengikuti env setiap start, supaya kunci yang diganti (`demo_tunnel.py keys`)
# langsung berlaku juga untuk toko yang sudah terpasang.
wp user update "${DECIQO_STORE_ADMIN_USER}" --user_pass="${DECIQO_STORE_ADMIN_PASSWORD}" --skip-email >/dev/null || exit 1

wp plugin is-active woocommerce || wp plugin activate woocommerce || exit 1
wp theme is-active storefront || wp theme activate storefront || exit 1
# .htaccess sudah dibuat entrypoint resmi; cukup set struktur permalink.
wp rewrite structure '/%postname%/' >/dev/null

echo "[deciqo-seed] mengisi katalog"
wp eval-file /opt/deciqo/seed.php || exit 1
chown -R www-data:www-data wp-content/uploads 2>/dev/null
touch /tmp/deciqo-ready
echo "[deciqo-seed] toko siap di ${DECIQO_STORE_URL}"
