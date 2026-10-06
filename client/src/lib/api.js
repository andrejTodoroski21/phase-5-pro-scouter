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

/**
 * Multipart upload with progress.
 *
 * Uses XMLHttpRequest rather than fetch because fetch still cannot report
 * upload progress, and a 100 MB clip with no progress bar looks like a hang.
 */
function upload(path, formData, { onProgress, signal } = {}) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest()
    xhr.open('POST', `/api${path}`)
    xhr.withCredentials = true

    xhr.upload.onprogress = (event) => {
      if (event.lengthComputable && onProgress) {
        onProgress(Math.round((event.loaded / event.total) * 100))
      }
    }
    xhr.onload = () => {
      let payload = null
      try { payload = JSON.parse(xhr.responseText) } catch { /* no body */ }
      if (xhr.status >= 200 && xhr.status < 300) resolve(payload)
      else reject(new Error(payload?.error || `Upload failed (${xhr.status})`))
    }
    xhr.onerror = () => reject(new Error('Upload failed'))
    xhr.onabort = () => reject(Object.assign(new Error('Aborted'), { name: 'AbortError' }))
    signal?.addEventListener('abort', () => xhr.abort())
    xhr.send(formData)
  })
}

export const api = {
  get: (path, opts) => request(path, opts),
  post: (path, body, opts) => request(path, { ...opts, method: 'POST', body }),
  del: (path, opts) => request(path, { ...opts, method: 'DELETE' }),
  upload,
}

export default api
