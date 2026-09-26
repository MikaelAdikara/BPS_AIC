import { useCallback, useEffect, useRef, useState, type RefObject } from "react";
import { useAuth } from "@/api/auth";
import { navigate } from "@/lib/router.js";

/** Semua CTA landing bermuara ke akun demo. Sudah masuk → langsung ke workspace. */
export function useDemoStart() {
  const { user, demo } = useAuth();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const start = useCallback(async () => {
    if (user) {
      navigate("/app");
      return;
    }
    setBusy(true);
    setError(null);
    try {
      await demo();
      navigate("/app");
    } catch (e) {
      setError((e as { code?: string }).code ?? "request_failed");
    } finally {
      setBusy(false);
    }
  }, [user, demo]);
  return { start, busy, error, signedIn: Boolean(user) };
}

export function prefersReducedMotion() {
  return (
    typeof window !== "undefined" &&
    window.matchMedia?.("(prefers-reduced-motion: reduce)").matches
  );
}

/** Menulis progres scroll elemen (0 saat bagian atasnya di atas layar, 1 saat sudah lewat)
 *  ke variabel CSS `--p`. Geraknya sendiri murni CSS; reduced-motion membekukannya di 0. */
export function useScrollProgress<T extends HTMLElement>(): RefObject<T> {
  const ref = useRef<T>(null);
  useEffect(() => {
    const el = ref.current;
    if (!el || prefersReducedMotion()) return;
    let frame = 0;
    const update = () => {
      frame = 0;
      const rect = el.getBoundingClientRect();
      const span = rect.height + window.innerHeight;
      const p = Math.min(1, Math.max(0, (window.innerHeight - rect.top) / span));
      el.style.setProperty("--p", p.toFixed(4));
    };
    const onScroll = () => {
      if (!frame) frame = requestAnimationFrame(update);
    };
    update();
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll);
    return () => {
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", onScroll);
      if (frame) cancelAnimationFrame(frame);
    };
  }, []);
  return ref;
}

/** True sekali saat elemen pertama kali terlihat; tidak kembali false. */
export function useRevealOnce<T extends HTMLElement>(threshold = 0.4) {
  const ref = useRef<T>(null);
  const [shown, setShown] = useState(false);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    if (prefersReducedMotion() || typeof IntersectionObserver === "undefined") {
      setShown(true);
      return;
    }
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries.some((e) => e.isIntersecting)) {
          setShown(true);
          observer.disconnect();
        }
      },
      { threshold },
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, [threshold]);
  return { ref, shown };
}

/** Nav berubah padat setelah halaman digulir lebih dari 12px. */
export function useScrolledPast(offset = 12) {
  const [past, setPast] = useState(false);
  useEffect(() => {
    const update = () => setPast(window.scrollY > offset);
    update();
    window.addEventListener("scroll", update, { passive: true });
    return () => window.removeEventListener("scroll", update);
  }, [offset]);
  return past;
}
