import { useEffect, useState, type CSSProperties } from "react";
import { Package } from "lucide-react";
import { safeImageUrl } from "./actions";

/** Gambar produk dengan fallback ikon bila URL kosong, tidak aman, atau gagal dimuat. */
export function ProductImage({
  src,
  alt = "",
  size,
  className = "",
}: {
  src?: string | null;
  alt?: string;
  size: number;
  className?: string;
}) {
  const url = safeImageUrl(src);
  const [failed, setFailed] = useState(false);
  useEffect(() => setFailed(false), [url]);
  const style = { "--thumb": size + "px" } as CSSProperties;
  if (!url || failed)
    return (
      <span
        className={"product-thumb product-thumb--empty " + className}
        style={style}
        aria-hidden
      >
        <Package size={Math.max(16, Math.round(size / 3))} />
      </span>
    );
  return (
    <img
      className={"product-thumb " + className}
      style={style}
      src={url}
      alt={alt}
      width={size}
      height={size}
      loading="lazy"
      decoding="async"
      referrerPolicy="no-referrer"
      onError={() => setFailed(true)}
    />
  );
}
