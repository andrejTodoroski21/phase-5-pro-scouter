import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../lib/api'
import { useAuth } from '../context/auth-context.js'

function AddVideo() {
  const { currentUser, loading } = useAuth()
  const [title, setTitle] = useState('')
  const [link, setLink] = useState('')
  const [error, setError] = useState(null)
  const [submitting, setSubmitting] = useState(false)
  const navigate = useNavigate()

  function handleSubmit(event) {
    event.preventDefault()
    setSubmitting(true)
    setError(null)
    // The server derives user_id from the session and pulls the id out of a
    // full YouTube URL, so either form of link works here.
    api.post('/videos', { title, file_path: link })
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
        <h2>New Video</h2>
        {error && <p className="error">{error}</p>}
        <input
          id="title"
          type="text"
          onChange={(e) => setTitle(e.target.value)}
          value={title}
          placeholder="TITLE"
          required
        />
        <input
          id="link"
          type="text"
          onChange={(e) => setLink(e.target.value)}
          value={link}
          placeholder="YOUTUBE LINK OR ID"
          required
        />
        <button type="submit" disabled={submitting}>
          {submitting ? 'Adding…' : 'Submit'}
        </button>
      </form>
    </div>
  )
}

export default AddVideo
