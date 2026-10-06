import { useEffect, useRef, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../lib/api'
import { useAuth } from '../context/auth-context.js'

const MAX_BYTES = 100 * 1024 * 1024
const MAX_SECONDS = 60

function AddVideo() {
  const { currentUser, loading } = useAuth()
  const [mode, setMode] = useState('upload')
  const [games, setGames] = useState([])
  const [title, setTitle] = useState('')
  const [game, setGame] = useState('')
  const [link, setLink] = useState('')
  const [file, setFile] = useState(null)
  const [fileError, setFileError] = useState(null)
  const [progress, setProgress] = useState(null)
  const [error, setError] = useState(null)
  const [submitting, setSubmitting] = useState(false)
  const abortRef = useRef(null)
  const navigate = useNavigate()

  useEffect(() => {
    const controller = new AbortController()
    api.get('/games', { signal: controller.signal }).then(setGames).catch(() => {})
    return () => controller.abort()
  }, [])

  /**
   * Check size and duration before uploading rather than after. The server
   * enforces both again — this only saves the user a pointless 100 MB round
   * trip to be told no.
   */
  function pickFile(event) {
    const chosen = event.target.files?.[0] ?? null
    setFile(null)
    setFileError(null)
    if (!chosen) return

    if (chosen.size > MAX_BYTES) {
      setFileError(`That file is ${Math.round(chosen.size / 1024 / 1024)} MB; the limit is 100 MB.`)
      return
    }
    const probe = document.createElement('video')
    probe.preload = 'metadata'
    probe.onloadedmetadata = () => {
      URL.revokeObjectURL(probe.src)
      if (probe.duration && probe.duration > MAX_SECONDS) {
        setFileError(`That clip is ${Math.round(probe.duration)}s; the limit is ${MAX_SECONDS}s.`)
      } else {
        setFile(chosen)
      }
    }
    probe.onerror = () => {
      URL.revokeObjectURL(probe.src)
      setFileError('That file does not look like a video the browser can read.')
    }
    probe.src = URL.createObjectURL(chosen)
  }

  function handleSubmit(event) {
    event.preventDefault()
    setError(null)
    setSubmitting(true)

    if (mode === 'link') {
      api.post('/videos', { title, file_path: link, game })
        .then(() => navigate('/profile'))
        .catch((err) => setError(err.message))
        .finally(() => setSubmitting(false))
      return
    }

    const body = new FormData()
    body.append('title', title)
    body.append('game', game)
    body.append('file', file)
    abortRef.current = new AbortController()
    setProgress(0)
    api.upload('/videos/upload', body, {
      onProgress: setProgress,
      signal: abortRef.current.signal,
    })
      .then(() => navigate('/profile'))
      .catch((err) => { if (err.name !== 'AbortError') setError(err.message) })
      .finally(() => { setSubmitting(false); setProgress(null) })
  }

  if (loading) return <p className="muted page">Loading…</p>
  if (!currentUser) {
    return (
      <div className="page">
        <p>Please <Link to="/login">log in</Link> to add a clip.</p>
      </div>
    )
  }

  const canSubmit = title && game && (mode === 'link' ? link : file) && !submitting

  return (
    <div className="page add-video-page">
      <form className="card submit-video-form" onSubmit={handleSubmit}>
        <h2>New Clip</h2>
        <div className="role-toggle">
          <button
            type="button" className={mode === 'upload' ? 'is-selected' : ''}
            onClick={() => setMode('upload')}
          >
            Upload a file
          </button>
          <button
            type="button" className={mode === 'link' ? 'is-selected' : ''}
            onClick={() => setMode('link')}
          >
            YouTube link
          </button>
        </div>

        {error && <p className="error">{error}</p>}

        <input
          id="title" type="text" placeholder="TITLE" required
          value={title} onChange={(e) => setTitle(e.target.value)}
        />

        {mode === 'link' ? (
          <input
            id="link" type="text" placeholder="YOUTUBE LINK OR ID" required
            value={link} onChange={(e) => setLink(e.target.value)}
          />
        ) : (
          <>
            <input id="file" type="file" accept="video/mp4,video/*" onChange={pickFile} />
            <p className="muted upload-hint">MP4, up to 60 seconds and 100 MB.</p>
            {fileError && <p className="error">{fileError}</p>}
            {file && !fileError && <p className="muted">{file.name}</p>}
          </>
        )}

        <select id="game" required value={game} onChange={(e) => setGame(e.target.value)}>
          <option value="" disabled>SELECT A GAME</option>
          {games.map((g) => (
            <option key={g.slug} value={g.slug}>{g.name}</option>
          ))}
        </select>

        {progress !== null && (
          <div className="upload-progress">
            <div className="upload-bar" style={{ width: `${progress}%` }} />
            <span>{progress}%</span>
          </div>
        )}

        <button type="submit" disabled={!canSubmit}>
          {submitting ? 'Uploading…' : 'Submit'}
        </button>
      </form>
    </div>
  )
}

export default AddVideo
