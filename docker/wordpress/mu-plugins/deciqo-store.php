<?php
/**
 * Plugin Name: Deciqo demo store
 * Description: Isi katalog demo, webhook ulasan ke Deciqo, dan reset toko. Hanya untuk toko demo lokal.
 *
 * Semua isi toko ditulis tim (data sintetis). Webhook yang dipakai adalah webhook bawaan
 * WooCommerce (WooCommerce → Settings → Advanced → Webhooks) bertopik Action. Woo hanya menerima
 * action berawalan `wc_`/`woocommerce_`, jadi plugin ini menembakkan `wc_deciqo_review_changed`
 * setiap ulasan produk dibuat, diubah, atau berganti status. Selain itu plugin ini hanya:
 * - mengirimnya langsung (bukan lewat antrean Action Scheduler) supaya ulasan terasa real-time,
 * - mengizinkan tujuan `api` di jaringan internal Docker,
 * - mematikan pembatas "komentar terlalu cepat" supaya demo bisa mengirim beberapa ulasan beruntun.
 */

if (!defined('ABSPATH')) {
    exit;
}

const DECIQO_CATALOG = '/opt/deciqo/catalog.json';
const DECIQO_IMAGES = '/opt/deciqo/images';
const DECIQO_WEBHOOK_OPTION = 'deciqo_webhook_ids';
const DECIQO_REVIEW_ACTION = 'wc_deciqo_review_changed';
const DECIQO_WEBHOOK_TOPICS = [
    'action.' . DECIQO_REVIEW_ACTION => 'Deciqo · ulasan produk berubah',
];

foreach (['comment_post', 'edit_comment', 'wp_set_comment_status'] as $deciqo_hook) {
    add_action($deciqo_hook, function ($comment_id) {
        $comment = get_comment((int) $comment_id);
        if ($comment && get_post_type($comment->comment_post_ID) === 'product') {
            do_action(DECIQO_REVIEW_ACTION, (int) $comment_id);
        }
    });
}

// --- perilaku runtime -------------------------------------------------------------------------

add_filter('woocommerce_webhook_deliver_async', '__return_false');
// Webhook tidak dimatikan otomatis bila Deciqo sempat mati di tengah latihan demo.
add_filter('woocommerce_max_webhook_delivery_failures', fn() => 1000);
add_filter('woocommerce_webhook_should_deliver', function ($deliver) {
    return empty($GLOBALS['deciqo_silent']) && $deliver;
});

add_filter('http_request_host_is_external', function ($external, $host) {
    return $host === deciqo_webhook_host() ? true : $external;
}, 10, 2);
add_filter('http_allowed_safe_ports', function ($ports, $host) {
    if ($host === deciqo_webhook_host()) {
        $ports[] = (int) (wp_parse_url(deciqo_env('DECIQO_WEBHOOK_URL'), PHP_URL_PORT) ?: 80);
    }
    return $ports;
}, 10, 2);

add_filter('comment_flood_filter', '__return_false', 99);
// Toko bisa dibuka publik lewat tunnel: tutup XML-RPC (login brute force) dan daftar user REST.
add_filter('xmlrpc_enabled', '__return_false');
if (defined('XMLRPC_REQUEST') && XMLRPC_REQUEST) {
    status_header(403);
    exit;
}
add_filter('rest_endpoints', function ($endpoints) {
    if (!current_user_can('list_users')) {
        unset($endpoints['/wp/v2/users'], $endpoints['/wp/v2/users/(?P<id>[\d]+)']);
    }
    return $endpoints;
});

add_action('rest_api_init', function () {
    register_rest_route('deciqo/v1', '/reset', [
        'methods' => 'POST',
        'permission_callback' => fn() => current_user_can('manage_options'),
        'callback' => fn() => rest_ensure_response(deciqo_store_reset()),
    ]);
});

if (defined('WP_CLI') && WP_CLI) {
    WP_CLI::add_command('deciqo seed', fn() => WP_CLI::success(wp_json_encode(deciqo_store_seed())));
    WP_CLI::add_command('deciqo reset', fn() => WP_CLI::success(wp_json_encode(deciqo_store_reset())));
}

function deciqo_env(string $name, string $default = ''): string
{
    $value = getenv($name);
    return $value === false || $value === '' ? $default : $value;
}

function deciqo_webhook_host(): string
{
    return (string) wp_parse_url(deciqo_env('DECIQO_WEBHOOK_URL'), PHP_URL_HOST);
}

function deciqo_catalog(): array
{
    return json_decode((string) file_get_contents(DECIQO_CATALOG), true)['products'] ?? [];
}

// --- seed -------------------------------------------------------------------------------------

function deciqo_store_seed(): array
{
    $GLOBALS['deciqo_silent'] = true;
    deciqo_store_settings();
    $result = ['products' => 0, 'reviews' => 0];
    // Semua post produk dibuat dulu: lampiran gambar juga memakai id post, dan bila dibuat lebih
    // awal ia bisa mengambil id produk berikutnya.
    foreach (deciqo_catalog() as $item) {
        deciqo_reserve_product($item);
    }
    foreach (deciqo_catalog() as $item) {
        deciqo_upsert_product($item);
        $result['products']++;
        $result['reviews'] += deciqo_upsert_reviews($item);
    }
    deciqo_api_password();
    $result['webhooks'] = deciqo_webhooks();
    $GLOBALS['deciqo_silent'] = false;
    return $result;
}

function deciqo_store_settings(): void
{
    if (!get_option('deciqo_seeded')) {
        // Konten bawaan WordPress tidak relevan untuk toko demo.
        wp_delete_post(1, true);
        wp_delete_post(2, true);
        update_option('deciqo_seeded', gmdate('c'));
    }
    $options = [
        'blogdescription' => 'Toko demo WooCommerce · semua isi ditulis tim Deciqo',
        'timezone_string' => 'Asia/Jakarta',
        'date_format' => 'j F Y',
        'WPLANG' => 'id_ID',
        // Ulasan langsung tampil: tanpa moderasi dan tanpa syarat pernah disetujui sebelumnya.
        'comment_moderation' => '0',
        'comment_previously_approved' => '0',
        'require_name_email' => '0',
        'comment_registration' => '0',
        'woocommerce_enable_reviews' => 'yes',
        'woocommerce_enable_review_rating' => 'yes',
        'woocommerce_review_rating_required' => 'yes',
        'woocommerce_review_rating_verification_required' => 'no',
        'woocommerce_review_rating_verification_label' => 'no',
        'woocommerce_currency' => 'IDR',
        'woocommerce_currency_pos' => 'left_space',
        'woocommerce_price_num_decimals' => '0',
        'woocommerce_price_thousand_sep' => '.',
        'woocommerce_price_decimal_sep' => ',',
        'woocommerce_default_country' => 'ID:JK',
        'woocommerce_store_city' => 'Jakarta',
        'woocommerce_coming_soon' => 'no',
        'woocommerce_store_pages_only' => 'no',
        'woocommerce_onboarding_profile' => ['skipped' => true],
        'woocommerce_task_list_hidden' => 'yes',
        'woocommerce_show_marketplace_suggestions' => 'no',
        'woocommerce_allow_tracking' => 'no',
        'storefront_nux_dismissed' => true,
    ];
    foreach ($options as $name => $value) {
        update_option($name, $value);
    }
    // Sidebar bawaan (Recent Posts, Archives, ...) kosong di toko ini; sisakan pencarian produk.
    $sidebars = (array) get_option('sidebars_widgets', []);
    foreach ($sidebars as $name => $widgets) {
        if (is_array($widgets) && $name !== 'wp_inactive_widgets') {
            $sidebars[$name] = [];
        }
    }
    update_option('sidebars_widgets', $sidebars);
    delete_transient('_wc_activation_redirect');
    $shop = (int) wc_get_page_id('shop');
    if ($shop > 0) {
        update_option('show_on_front', 'page');
        update_option('page_on_front', $shop);
    }
}

function deciqo_reserve_product(array $item): void
{
    $id = (int) $item['id'];
    $post = get_post($id);
    if ($post && $post->post_type !== 'product') {
        throw new RuntimeException('id produk demo sudah terpakai: ' . $id);
    }
    if (!$post) {
        // `import_id` menjaga id produk sama dengan katalog demo Deciqo (101, 102, ...), sehingga
        // sinkron pertama tidak membuat produk ganda di akun demo.
        $id = wp_insert_post([
            'import_id' => $id,
            'post_type' => 'product',
            'post_status' => 'publish',
            'post_title' => $item['name'],
            'comment_status' => 'open',
        ], true);
        if (is_wp_error($id) || $id !== (int) $item['id']) {
            throw new RuntimeException('id produk demo sudah terpakai: ' . $item['id']);
        }
    }
}

function deciqo_upsert_product(array $item): void
{
    $id = (int) $item['id'];
    $product = new WC_Product_Simple($id);
    $product->set_name($item['name']);
    $product->set_sku($item['sku']);
    $product->set_regular_price($item['price']);
    $product->set_description($item['description']);
    $product->set_short_description($item['short_description'] ?? '');
    $product->set_status('publish');
    $product->set_reviews_allowed(true);
    $product->set_stock_status('instock');
    $product->set_total_sales((int) ($item['total_sales'] ?? 0));
    $attributes = [];
    foreach ($item['attributes'] as $i => $spec) {
        $attribute = new WC_Product_Attribute();
        $attribute->set_name($spec['name']);
        $attribute->set_options($spec['options']);
        $attribute->set_position($i);
        $attribute->set_visible(true);
        $attributes[] = $attribute;
    }
    $product->set_attributes($attributes);
    if (!$product->get_image_id()) {
        $image = deciqo_attach_image($id, $item);
        if ($image) {
            $product->set_image_id($image);
        }
    }
    $product->save();
}

function deciqo_attach_image(int $product_id, array $item): int
{
    $source = DECIQO_IMAGES . '/' . strtolower($item['sku']) . '.png';
    if (!is_file($source)) {
        return 0;
    }
    require_once ABSPATH . 'wp-admin/includes/file.php';
    require_once ABSPATH . 'wp-admin/includes/media.php';
    require_once ABSPATH . 'wp-admin/includes/image.php';
    $tmp = wp_tempnam(basename($source));
    copy($source, $tmp);
    $attachment = media_handle_sideload(['name' => basename($source), 'tmp_name' => $tmp], $product_id, $item['name']);
    return is_wp_error($attachment) ? 0 : (int) $attachment;
}

function deciqo_upsert_reviews(array $item): int
{
    global $wpdb;
    $product_id = (int) $item['id'];
    $count = 0;
    foreach ($item['reviews'] as $review) {
        $id = (int) $review['id'];
        $gmt = gmdate('Y-m-d 03:00:00', time() - (int) $review['days_ago'] * DAY_IN_SECONDS);
        $row = [
            'comment_post_ID' => $product_id,
            'comment_author' => $review['author'],
            'comment_author_email' => '',
            'comment_content' => $review['text'],
            'comment_date' => get_date_from_gmt($gmt),
            'comment_date_gmt' => $gmt,
            'comment_approved' => '1',
            'comment_type' => 'review',
            'comment_agent' => 'deciqo-seed',
            'user_id' => 0,
        ];
        $existing = get_comment($id);
        if ($existing) {
            // Ulasan seed yang diubah/disembunyikan saat latihan dikembalikan; tanggal tetap.
            unset($row['comment_date'], $row['comment_date_gmt']);
            $wpdb->update($wpdb->comments, $row, ['comment_ID' => $id]);
        } else {
            // id tetap (1011, 1012, ...) = id ulasan di katalog demo Deciqo.
            $wpdb->insert($wpdb->comments, ['comment_ID' => $id] + $row);
        }
        update_comment_meta($id, 'rating', (int) $review['rating']);
        update_comment_meta($id, 'verified', 0);
        update_comment_meta($id, 'deciqo_seed', 1);
        clean_comment_cache($id);
        $count++;
    }
    wp_update_comment_count_now($product_id);
    WC_Comments::clear_transients($product_id);
    return $count;
}

function deciqo_api_password(): void
{
    // Application password dengan nilai tetap dari env, supaya Deciqo bisa langsung terhubung
    // tanpa menyalin key. Toko ini hanya terjangkau dari jaringan Docker dan 127.0.0.1.
    $user = get_user_by('login', deciqo_env('DECIQO_STORE_ADMIN_USER', 'admin'));
    $plain = preg_replace('/[^a-z\d]/i', '', deciqo_env('DECIQO_STORE_API_PASSWORD'));
    if (!$user || $plain === '') {
        return;
    }
    $hash = method_exists('WP_Application_Passwords', 'hash_password')
        ? WP_Application_Passwords::hash_password($plain)
        : wp_hash_password($plain);
    $items = array_values(array_filter(
        WP_Application_Passwords::get_user_application_passwords($user->ID),
        fn($item) => $item['name'] !== 'Deciqo'
    ));
    $items[] = [
        'uuid' => wp_generate_uuid4(),
        'app_id' => '',
        'name' => 'Deciqo',
        'password' => $hash,
        'created' => time(),
        'last_used' => null,
        'last_ip' => null,
    ];
    update_user_meta($user->ID, WP_Application_Passwords::USERMETA_KEY_APPLICATION_PASSWORDS, $items);
    // Tanpa penanda ini WordPress melewati pengecekan application password sama sekali.
    update_network_option(null, WP_Application_Passwords::OPTION_KEY_IN_USE, true);
}

function deciqo_webhooks(): int
{
    $url = deciqo_env('DECIQO_WEBHOOK_URL');
    $secret = deciqo_env('DECIQO_WEBHOOK_SECRET');
    if ($url === '' || $secret === '') {
        return 0;
    }
    $ids = (array) get_option(DECIQO_WEBHOOK_OPTION, []);
    foreach (array_diff_key($ids, DECIQO_WEBHOOK_TOPICS) as $old) {
        $webhook = wc_get_webhook((int) $old);
        if ($webhook) {
            $webhook->delete(true);
        }
    }
    $ids = array_intersect_key($ids, DECIQO_WEBHOOK_TOPICS);
    $owner = get_user_by('login', deciqo_env('DECIQO_STORE_ADMIN_USER', 'admin'));
    foreach (DECIQO_WEBHOOK_TOPICS as $topic => $name) {
        $webhook = new WC_Webhook((int) ($ids[$topic] ?? 0));
        $webhook->set_name($name);
        $webhook->set_user_id($owner ? $owner->ID : 1);
        $webhook->set_topic($topic);
        $webhook->set_delivery_url($url);
        $webhook->set_secret($secret);
        $webhook->set_api_version('wp_api_v3');
        $webhook->set_failure_count(0);
        $webhook->set_status('active');
        $ids[$topic] = $webhook->save();
    }
    update_option(DECIQO_WEBHOOK_OPTION, $ids);
    return count($ids);
}

// --- reset ------------------------------------------------------------------------------------

function deciqo_store_reset(): array
{
    $GLOBALS['deciqo_silent'] = true;
    $seeded = [];
    foreach (deciqo_catalog() as $item) {
        foreach ($item['reviews'] as $review) {
            $seeded[(int) $review['id']] = true;
        }
    }
    $removed = 0;
    $ids = get_comments(['post_type' => 'product', 'status' => 'all', 'type' => 'all', 'fields' => 'ids']);
    foreach (array_merge($ids, get_comments(['post_type' => 'product', 'status' => 'trash', 'fields' => 'ids']),
                         get_comments(['post_type' => 'product', 'status' => 'spam', 'fields' => 'ids'])) as $id) {
        if (!isset($seeded[(int) $id])) {
            wp_delete_comment((int) $id, true);
            $removed++;
        }
    }
    $result = deciqo_store_seed();
    $result['removed'] = $removed;
    return $result;
}
