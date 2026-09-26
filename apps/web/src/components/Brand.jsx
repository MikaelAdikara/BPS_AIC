import { Moon, Sun, Languages } from "lucide-react";
import { useI18n } from "../lib/i18n";
import { useTheme } from "../lib/theme";
import { Button } from "./ui";
export function BrandMark({ size = 30, className = "" }) {
  return (
    <img
      className={className}
      src="/brand/mark.png"
      width={size}
      height={size}
      alt=""
      aria-hidden
      decoding="async"
    />
  );
}
export function Brand({ onClick = undefined } = {}) {
  const { t } = useI18n();
  return (
    <a
      className="brand"
      href="#/"
      onClick={onClick}
      aria-label={"Deciqo · " + t("common.home")}
    >
      <BrandMark />
      <span className="brand__name">Deciqo</span>
    </a>
  );
}
export function BrandLockup() {
  return <Brand />;
}
export function ThemeToggle({
  theme: providedTheme = undefined,
  onToggle = undefined,
} = {}) {
  const context = useTheme();
  const theme = providedTheme ?? context.theme;
  const { t } = useI18n();
  return (
    <Button
      variant="outline"
      size="sm"
      onClick={onToggle ?? context.toggleTheme}
      aria-label={t(
        theme === "dark" ? "common.lightTheme" : "common.darkTheme",
      )}
      aria-pressed={theme === "dark"}
    >
      {theme === "dark" ? (
        <Sun size={16} aria-hidden />
      ) : (
        <Moon size={16} aria-hidden />
      )}
      <span>
        {t(theme === "dark" ? "common.lightTheme" : "common.darkTheme")}
      </span>
    </Button>
  );
}
export function LangToggle() {
  const { language, setLanguage, t } = useI18n();
  return (
    <Button
      variant="outline"
      size="sm"
      onClick={() => setLanguage(language === "en" ? "id" : "en")}
      aria-label={t("common.language")}
    >
      <Languages size={16} aria-hidden />
      {language === "en" ? "ID" : "EN"}
    </Button>
  );
}
export function BotMark() {
  return null;
}
