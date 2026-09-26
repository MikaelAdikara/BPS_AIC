import type { CSSProperties } from "react";

/** Kilau yang mengitari tepi kontainer ber-`position: relative`. Dekoratif; induknya menentukan
 *  radius sudut. Disembunyikan saat reduced-motion. */
export function BorderBeam({
  size = 220,
  duration = 12,
  width = 1.5,
  delay = 0,
  from = "var(--blue)",
  to = "var(--sky-deep)",
}: {
  size?: number;
  duration?: number;
  width?: number;
  delay?: number;
  from?: string;
  to?: string;
}) {
  return (
    <div
      className="border-beam"
      aria-hidden
      style={
        {
          "--beam-size": size,
          "--beam-duration": duration,
          "--beam-width": width,
          "--beam-delay": -delay + "s",
          "--beam-from": from,
          "--beam-to": to,
        } as CSSProperties
      }
    />
  );
}
