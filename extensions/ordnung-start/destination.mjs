export function destination(input) {
  const value = input.trim();
  if (!value) return null;
  if (/^https?:\/\//i.test(value)) {
    try {
      const url = new URL(value);
      return url.hostname && !url.username && !url.password ? url.href : null;
    } catch { return null; }
  }
  // Never execute javascript/data/file URIs from the search field.
  if (/^[a-z][a-z0-9+.-]*:/i.test(value) && !/^localhost:\d+(\/|$)/i.test(value)) return null;
  if (!/\s/.test(value) && (/^[^/]+\.[^/]+/.test(value) || /^localhost(:\d+)?(\/|$)/i.test(value))) {
    try {
      const url = new URL(`https://${value}`);
      return url.username || url.password ? null : url.href;
    } catch { return null; }
  }
  return `https://duckduckgo.com/?q=${encodeURIComponent(value)}`;
}
