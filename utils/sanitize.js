export function sanitizeHistory(history) {
  if (!Array.isArray(history)) return [];

  return history
    .slice(-20)
    .map(item => ({
      role: item.role?.trim().slice(0, 20) || "user",
      content: item.content?.trim().slice(0, 2000) || ""
    }));
}
