<?php
// Dijalankan `wp eval-file` oleh seed.sh. Logikanya ada di mu-plugin deciqo-store.php.
echo wp_json_encode(deciqo_store_seed()) . PHP_EOL;
