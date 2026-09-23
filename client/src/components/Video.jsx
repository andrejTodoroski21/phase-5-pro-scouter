import { useCallback, useEffect, useState } from 'react'
import api from '../lib/api'
import LiteYouTube from './LiteYouTube.jsx'

const Video = () => {
  const [videos, setVideos] = useState([])
  const [page, setPage] = useState(1)
  const [hasNext, setHasNext] = useState(false)
  const [status, setStatus] = useState('loading')
  const [error, setError] = useState(null)

  const loadPage = useCallback((pageNumber, signal) => {
    setStatus('loading')
    // Paginated: the endpoint used to return every row in the table at once.
    api.get(`/videos?page=${pageNumber}&per_page=12`, { signal })
      .then((data) => {
        if (signal?.aborted) return
        setVideos((previous) => (pageNumber === 1 ? data.videos : [...previous, ...data.videos]))
        setHasNext(data.has_next)
        setError(null)
        setStatus('ready')
      })
      .catch((err) => {
        if (signal?.aborted || err.name === 'AbortError') return
        setError('Could not load videos. Please try again later.')
        setStatus('error')
      })
  }, [])

  useEffect(() => {
    const controller = new AbortController()
    loadPage(page, controller.signal)
    return () => controller.abort()
  }, [page, loadPage])

  return (
    <div className="page videos-page">
      <h1 className="browse">Browse Videos</h1>
      {error && <p className="error">{error}</p>}
      <div className="video-grid">
        {videos.map((video) => (
          <article className="video-card" key={video.id}>
            <LiteYouTube videoId={video.file_path} title={video.title} />
            <p className="video-title">{video.title}</p>
            <p className="video-meta">
              By: {video.uploader?.username ?? 'unknown'} · {video.like_count} likes
            </p>
          </article>
        ))}
      </div>
      {status === 'loading' && <p className="muted">Loading…</p>}
      {status === 'ready' && videos.length === 0 && <p className="muted">No videos yet.</p>}
      {hasNext && status !== 'loading' && (
        <button type="button" onClick={() => setPage((p) => p + 1)}>Load more</button>
      )}
    </div>
  )
}

export default Video
