import { common } from "./messages-common.js";
import { errors } from "./messages-errors.js";
import { landing } from "./messages-landing.js";
import { workspace } from "./messages-workspace.js";
import { product } from "./messages-product.js";
import { catalog } from "./messages-catalog.js";
import { settings } from "./messages-settings.js";
import { sources } from "./messages-sources.js";
export const messages = {
  en: {
    common: common.en,
    errors: errors.en,
    landing: landing.en,
    workspace: workspace.en,
    product: product.en,
    catalog: catalog.en,
    settings: settings.en,
    sources: sources.en,
  },
  id: {
    common: common.id,
    errors: errors.id,
    landing: landing.id,
    workspace: workspace.id,
    product: product.id,
    catalog: catalog.id,
    settings: settings.id,
    sources: sources.id,
  },
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
