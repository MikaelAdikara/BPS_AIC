import { common } from "./messages-common.js";
import { errors } from "./messages-errors.js";
import { landing } from "./messages-landing.js";
export const messages = {
  en: { common: common.en, errors: errors.en, landing: landing.en },
  id: { common: common.id, errors: errors.id, landing: landing.id },
};
export function translate(language, key, values = {}) {
  const [namespace, ...parts] = key.split(".");
  const value = messages[language]?.[namespace]?.[parts.join(".")];
  if (typeof value !== "string") return messages[language].common.unknownError;
  return value.replace(/\{(\w+)\}/g, (match, name) =>
    String(values[name] ?? match),
  );
}
export function localizeError(code, language = "en") {
  return errors[language]?.[code] ?? common[language].unknownError;
}
export function plural(language, count) {
  return translate(
    language,
    count === 1 ? "common.pluralOne" : "common.pluralOther",
    { count },
  );
}
