export function sanitizeHistory(history) {
  if (!Array.isArray(history)) return [];
  return history.slice(-20);
}
