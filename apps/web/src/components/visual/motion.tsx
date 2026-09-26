import {
  Fragment,
  useEffect,
  useRef,
  useState,
  type CSSProperties,
  type ElementType,
  type HTMLAttributes,
  type ReactNode,
} from "react";
import { cn } from "@/lib/cn";

export function prefersReducedMotion() {
  return (
    typeof window !== "undefined" &&
    window.matchMedia?.("(prefers-reduced-motion: reduce)").matches
  );
}

/** True sekali saat elemen pertama kali terlihat; tidak kembali false. Reduced-motion atau
 *  peramban tanpa IntersectionObserver langsung dianggap terlihat. */
export function useInView<T extends Element>(threshold = 0.2) {
  const ref = useRef<T>(null);
  const [inView, setInView] = useState(false);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    if (prefersReducedMotion() || typeof IntersectionObserver === "undefined") {
      setInView(true);
      return;
    }
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries.some((entry) => entry.isIntersecting)) {
          setInView(true);
          observer.disconnect();
        }
      },
      { threshold, rootMargin: "0px 0px -6% 0px" },
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, [threshold]);
  return { ref, inView };
}

/** Bungkus yang naik dan menajam saat masuk layar. `delay` dalam milidetik. */
export function Reveal({
  as: Tag = "div",
  delay = 0,
  scale = false,
  className,
  style,
  children,
  ...props
}: HTMLAttributes<HTMLElement> & {
  as?: ElementType;
  delay?: number;
  scale?: boolean;
  children: ReactNode;
}) {
  const { ref, inView } = useInView<HTMLElement>(0.15);
  return (
    <Tag
      {...props}
      ref={ref}
      className={cn("reveal", scale && "reveal--scale", inView && "is-in", className)}
      style={{ ...style, "--reveal-delay": delay + "ms" } as CSSProperties}
    >
      {children}
    </Tag>
  );
}

/** Memecah teks menjadi kata yang muncul bergantian (lihat `.words` di motion.css). */
export function Words({ text, offset = 0 }: { text: string; offset?: number }) {
  return (
    <span className="words">
      {text.split(" ").map((word, index) => (
        <Fragment key={index}>
          <span style={{ "--w": index + offset } as CSSProperties}>{word}</span>{" "}
        </Fragment>
      ))}
    </span>
  );
}

/** Angka yang menghitung naik ke nilainya saat terlihat. Nilai bukan angka ditampilkan apa adanya;
 *  pembaca layar selalu mendapat nilai akhir. */
export function CountUp({
  value,
  decimals,
  duration = 900,
  format,
}: {
  value: number | null | undefined;
  decimals?: number;
  duration?: number;
  format?: (value: number) => string;
}) {
  const { ref, inView } = useInView<HTMLSpanElement>(0.3);
  const target = typeof value === "number" && Number.isFinite(value) ? value : null;
  const places = decimals ?? (target != null && !Number.isInteger(target) ? 1 : 0);
  const [shown, setShown] = useState(() => (prefersReducedMotion() ? target ?? 0 : 0));
  useEffect(() => {
    if (target == null || !inView) return;
    if (prefersReducedMotion()) {
      setShown(target);
      return;
    }
    let frame = 0;
    const start = performance.now();
    const from = 0;
    const tick = (now: number) => {
      const p = Math.min(1, (now - start) / duration);
      const eased = 1 - Math.pow(1 - p, 3);
      setShown(from + (target - from) * eased);
      if (p < 1) frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [target, inView, duration]);
  if (target == null) return <span ref={ref}>—</span>;
  const text = format
    ? format(Number(shown.toFixed(places)))
    : shown.toFixed(places);
  const final = format ? format(target) : target.toFixed(places);
  return (
    <span ref={ref} className="count-up">
      <span aria-hidden>{text}</span>
      <span className="visually-hidden">{final}</span>
    </span>
  );
}
