import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import { messages, translate, localizeError, plural } from "./messages.js";
import { readPreference, writePreference } from "./storage.js";
export type Language = "en" | "id";
type Values = Record<string, string | number>;
const Context = createContext<{
  language: Language;
  setLanguage: (language: Language) => void;
  t: (key: string, values?: Values) => string;
  localizeError: (code: string) => string;
  plural: (count: number) => string;
} | null>(null);
export function I18nProvider({ children }: { children: ReactNode }) {
  const [language, setLanguage] = useState<Language>(() =>
    readPreference("deciqo-language", "en") === "id" ? "id" : "en",
  );
  useEffect(() => {
    document.documentElement.lang = language;
    writePreference("deciqo-language", language);
  }, [language]);
  return (
    <Context.Provider
      value={{
        language,
        setLanguage,
        t: (key, values) => translate(language, key, values),
        localizeError: (code) => localizeError(code, language),
        plural: (count) => plural(language, count),
      }}
    >
      {children}
    </Context.Provider>
  );
}
export function useI18n() {
  const value = useContext(Context);
  if (!value) throw new Error("I18nProvider required");
  return value;
}
export { messages };
