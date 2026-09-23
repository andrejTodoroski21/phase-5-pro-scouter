/**
 * Thin fetch wrapper.
 *
 * Every call goes through here so the session cookie is always sent and errors
 * surface as thrown Errors instead of silently producing `undefined`.
 */
async function request(path, { method = 'GET', body, signal } = {}) {
  const response = await fetch(`/api${path}`, {
    method,
    credentials: 'include',
    signal,
    headers: body ? { 'Content-Type': 'application/json', Accept: 'application/json' } : { Accept: 'application/json' },
    body: body ? JSON.stringify(body) : undefined,
  })

  if (response.status === 204) return null

  const payload = await response.json().catch(() => null)
  if (!response.ok) {
    throw new Error(payload?.error || `Request failed (${response.status})`)
  }
  return payload
}

export const api = {
  get: (path, opts) => request(path, opts),
  post: (path, body, opts) => request(path, { ...opts, method: 'POST', body }),
  del: (path, opts) => request(path, { ...opts, method: 'DELETE' }),
}

export default api
