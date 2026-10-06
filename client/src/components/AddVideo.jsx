import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../lib/api'
import { useAuth } from '../context/auth-context.js'

function AddVideo() {
  const { currentUser, loading } = useAuth()
  const [games, setGames] = useState([])
  const [title, setTitle] = useState('')
  const [link, setLink] = useState('')
  const [game, setGame] = useState('')
  const [error, setError] = useState(null)
  const [submitting, setSubmitting] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    const controller = new AbortController()
    api.get('/games', { signal: controller.signal })
      .then(setGames)
      .catch(() => {})
    return () => controller.abort()
  }, [])

  function handleSubmit(event) {
    event.preventDefault()
    setSubmitting(true)
    setError(null)
    // The server derives user_id from the session and pulls the id out of a
    // full YouTube URL, so either form of link works here.
    api.post('/videos', { title, file_path: link, game })
      .then(() => navigate('/profile'))
      .catch((err) => setError(err.message))
      .finally(() => setSubmitting(false))
  }

  if (loading) return <p className="muted page">Loading…</p>
  if (!currentUser) {
    return (
      <div className="page">
        <p>Please <Link to="/login">log in</Link> to add a video.</p>
      </div>
    )
  }

  return (
    <div className="page add-video-page">
      <form className="card submit-video-form" onSubmit={handleSubmit}>
        <h2>New Clip</h2>
        {error && <p className="error">{error}</p>}
        <input
          id="title" type="text" placeholder="TITLE" required
          value={title} onChange={(e) => setTitle(e.target.value)}
        />
        <input
          id="link" type="text" placeholder="YOUTUBE LINK OR ID" required
          value={link} onChange={(e) => setLink(e.target.value)}
        />
        <select
          id="game" required value={game}
          onChange={(e) => setGame(e.target.value)}
        >
          <option value="" disabled>SELECT A GAME</option>
          {games.map((g) => (
            <option key={g.slug} value={g.slug}>{g.name}</option>
          ))}
        </select>
        <button type="submit" disabled={submitting}>
          {submitting ? 'Adding…' : 'Submit'}
        </button>
      </form>
    </div>
  )
}

export default AddVideo
