import {
  createContext,
  useContext,
  useLayoutEffect,
  useState,
  type ReactNode,
} from "react";
import { readPreference, writePreference } from "./storage.js";
export type Theme = "light" | "dark";
const Context = createContext<{ theme: Theme; toggleTheme: () => void } | null>(
  null,
);
export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<Theme>(() =>
    readPreference("deciqo-theme", "light") === "dark" ? "dark" : "light",
  );
  useLayoutEffect(() => {
    const root = document.documentElement;
    root.setAttribute("data-theme-changing", "");
    root.dataset.theme = theme;
    writePreference("deciqo-theme", theme);
    const frame = requestAnimationFrame(() =>
      requestAnimationFrame(() => root.removeAttribute("data-theme-changing")),
    );
    return () => {
      cancelAnimationFrame(frame);
      root.removeAttribute("data-theme-changing");
    };
  }, [theme]);
  return (
    <Context.Provider
      value={{
        theme,
        toggleTheme: () =>
          setTheme((value) => (value === "dark" ? "light" : "dark")),
      }}
    >
      {children}
    </Context.Provider>
  );
}
export function useTheme() {
  const value = useContext(Context);
  if (!value) throw new Error("ThemeProvider required");
  return value;
}
