# syntax=docker/dockerfile:1
# ------------------------------------------------------------------------------------
# Toko WooCommerce ASLI untuk demo (profile Compose `store`).
#
# WordPress + WooCommerce + tema Storefront, diisi katalog demo yang sama dengan toko sintetis
# (`docker/wordpress/catalog.json`, diekspor dari `demo_catalog.py`). Ulasan yang ditulis di
# storefront memicu webhook WooCommerce ke Deciqo, lalu Deciqo sinkron dan menganalisis.
#
# Plugin dan tema diunduh saat build (butuh internet sekali). Setelah itu image dan volume
# cukup untuk demo tanpa internet.
# ------------------------------------------------------------------------------------
FROM wordpress:php8.3-apache

ARG WOOCOMMERCE_VERSION=11.1.2
ARG STOREFRONT_VERSION=4.6.2
# Paket bahasa Indonesia terbaru untuk inti WP (belum ada untuk 7.1.x) dan untuk WooCommerce.
ARG WP_LANG_VERSION=7.0.6

COPY --from=wordpress:cli-php8.3 /usr/local/bin/wp /usr/local/bin/wp

RUN apt-get update \
 && apt-get install -y --no-install-recommends unzip \
 && rm -rf /var/lib/apt/lists/* \
 && curl -fsSL -o /tmp/woo.zip "https://downloads.wordpress.org/plugin/woocommerce.${WOOCOMMERCE_VERSION}.zip" \
 && curl -fsSL -o /tmp/storefront.zip "https://downloads.wordpress.org/theme/storefront.${STOREFRONT_VERSION}.zip" \
 && unzip -q /tmp/woo.zip -d /usr/src/wordpress/wp-content/plugins \
 && unzip -q /tmp/storefront.zip -d /usr/src/wordpress/wp-content/themes \
 && rm /tmp/woo.zip /tmp/storefront.zip  && mkdir -p /opt/deciqo/languages/plugins  && curl -fsSL -o /tmp/core-id.zip "https://downloads.wordpress.org/translation/core/${WP_LANG_VERSION}/id_ID.zip"  && curl -fsSL -o /tmp/woo-id.zip "https://downloads.wordpress.org/translation/plugin/woocommerce/${WOOCOMMERCE_VERSION}/id_ID.zip"  && unzip -q /tmp/core-id.zip -d /opt/deciqo/languages  && unzip -q /tmp/woo-id.zip -d /opt/deciqo/languages/plugins  && rm /tmp/core-id.zip /tmp/woo-id.zip

# Image resmi hanya menyalin /usr/src/wordpress ke volume /var/www/html saat volume masih kosong,
# jadi mu-plugin, seed, dan katalog disimpan di /opt/deciqo dan seed.sh menyalin mu-plugin setiap
# start: rebuild image selalu memperbarui toko yang volumenya sudah ada.
COPY docker/wordpress/mu-plugins/ /opt/deciqo/mu-plugins/
COPY docker/wordpress/seed.sh docker/wordpress/seed.php docker/wordpress/catalog.json /opt/deciqo/
COPY docker/wordpress/images/ /opt/deciqo/images/
COPY docker/wordpress/entrypoint.sh /usr/local/bin/deciqo-entrypoint.sh
RUN chmod +x /usr/local/bin/deciqo-entrypoint.sh /opt/deciqo/seed.sh

ENTRYPOINT ["deciqo-entrypoint.sh"]
CMD ["apache2-foreground"]
