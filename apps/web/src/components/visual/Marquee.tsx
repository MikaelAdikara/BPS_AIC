import type { CSSProperties, ReactNode } from "react";
import { cn } from "@/lib/cn";

/** Pita berjalan tanpa akhir. Isi diulang `repeat` kali; hanya salinan pertama yang dibaca pembaca
 *  layar. Gerak murni CSS (`.marquee` di motion.css) dan berhenti saat reduced-motion. */
export function Marquee({
  children,
  vertical = false,
  reverse = false,
  pauseOnHover = false,
  fade = false,
  repeat = 3,
  duration = 40,
  gap = 16,
  className,
  label,
}: {
  children: ReactNode;
  vertical?: boolean;
  reverse?: boolean;
  pauseOnHover?: boolean;
  fade?: boolean;
  repeat?: number;
  duration?: number;
  gap?: number;
  className?: string;
  label?: string;
}) {
  return (
    <div
      className={cn(
        "marquee",
        vertical && "marquee--vertical",
        reverse && "marquee--reverse",
        pauseOnHover && "marquee--pause",
        fade && "marquee--fade",
        className,
      )}
      style={{ "--duration": duration + "s", "--gap": gap + "px" } as CSSProperties}
      role={label ? "region" : undefined}
      aria-label={label}
    >
      {Array.from({ length: repeat }, (_, index) => (
        <div key={index} className="marquee__track" aria-hidden={index > 0 || undefined}>
          {children}
        </div>
      ))}
    </div>
  );
}
