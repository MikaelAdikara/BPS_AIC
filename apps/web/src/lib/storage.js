export function readPreference(key, fallback, storage) {
  try {
    return (storage ?? globalThis.localStorage).getItem(key) ?? fallback;
  } catch {
    return fallback;
  }
}
export function writePreference(key, value) {
  try {
    globalThis.localStorage.setItem(key, value);
  } catch {
    /* Preferences remain active in memory. */
  }
}
