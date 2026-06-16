export function safeJson(res, status, data) {
  const payload = {
    status,
    timestamp: new Date().toISOString(),
    ...data
  };

  res.status(status).json(payload);
}
