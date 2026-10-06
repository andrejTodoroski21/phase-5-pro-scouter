import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../lib/api'
import ClipPlayer from './ClipPlayer.jsx'
import { useAuth } from '../context/auth-context.js'

function Profile() {
  const { currentUser, loading } = useAuth()
  const [videos, setVideos] = useState([])
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!currentUser) return undefined
    const controller = new AbortController()
    // Filtered server-side. This used to download every video in the database
    // and throw away everything that was not the current user's.
    api.get(`/videos?user_id=${currentUser.id}&per_page=50`, { signal: controller.signal })
      .then((data) => setVideos(data.videos))
      .catch((err) => {
        if (err.name !== 'AbortError') setError('Could not load your videos.')
      })
    return () => controller.abort()
  }, [currentUser])

  const deleteVideo = (videoId) => {
    api.del(`/videos/${videoId}`)
      .then(() => setVideos((previous) => previous.filter((v) => v.id !== videoId)))
      .catch(() => setError('Failed to delete video.'))
  }

  if (loading) return <p className="muted page">Loading…</p>
  if (!currentUser) {
    return (
      <div className="page">
        <p>Please <Link to="/login">log in</Link> to see your profile.</p>
      </div>
    )
  }

  return (
    <div className="page profile-page">
      <header className="profile-header">
        <h1>My Videos</h1>
        <p className="muted">{currentUser.username}</p>
      </header>
      {error && <p className="error">{error}</p>}
      {videos.length === 0 ? (
        <p className="muted">No videos yet. <Link to="/add-video">Add one</Link>.</p>
      ) : (
        <div className="video-grid">
          {videos.map((video) => (
            <article className="video-card" key={video.id}>
              <ClipPlayer video={video} />
              <p className="video-title">{video.title}</p>
              <button type="button" onClick={() => deleteVideo(video.id)}>Delete</button>
            </article>
          ))}
        </div>
      )}
    </div>
  )
}

export default Profile
