import { useCallback, useEffect, useState } from 'react'
import api from '../lib/api'
import LiteYouTube from './LiteYouTube.jsx'

const Video = () => {
  const [videos, setVideos] = useState([])
  const [games, setGames] = useState([])
  const [game, setGame] = useState('')
  const [page, setPage] = useState(1)
  const [hasNext, setHasNext] = useState(false)
  const [status, setStatus] = useState('loading')
  const [error, setError] = useState(null)

  useEffect(() => {
    const controller = new AbortController()
    api.get('/games', { signal: controller.signal }).then(setGames).catch(() => {})
    return () => controller.abort()
  }, [])

  const loadPage = useCallback((pageNumber, gameSlug, signal) => {
    setStatus('loading')
    const gameParam = gameSlug ? `&game=${gameSlug}` : ''
    // Paginated: the endpoint used to return every row in the table at once.
    api.get(`/videos?page=${pageNumber}&per_page=12${gameParam}`, { signal })
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
    loadPage(page, game, controller.signal)
    return () => controller.abort()
  }, [page, game, loadPage])

  function pickGame(slug) {
    setGame(slug)
    setPage(1)
    setVideos([])
  }

  return (
    <div className="page videos-page">
      <h1 className="browse">Browse Clips</h1>
      <div className="game-filter">
        <button
          type="button"
          className={game === '' ? 'is-selected' : ''}
          onClick={() => pickGame('')}
        >
          All games
        </button>
        {games.filter((g) => g.clip_count > 0).map((g) => (
          <button
            type="button"
            key={g.slug}
            className={game === g.slug ? 'is-selected' : ''}
            onClick={() => pickGame(g.slug)}
          >
            {g.name} ({g.clip_count})
          </button>
        ))}
      </div>
      {error && <p className="error">{error}</p>}
      <div className="video-grid">
        {videos.map((video) => (
          <article className="video-card" key={video.id}>
            <LiteYouTube videoId={video.file_path} title={video.title} />
            <p className="video-title">{video.title}</p>
            <p className="video-meta">
              {video.game_name} · by {video.uploader?.username ?? 'unknown'} · {video.like_count} likes
            </p>
          </article>
        ))}
      </div>
      {status === 'loading' && <p className="muted">Loading…</p>}
      {status === 'ready' && videos.length === 0 && <p className="muted">No clips yet.</p>}
      {hasNext && status !== 'loading' && (
        <button type="button" onClick={() => setPage((p) => p + 1)}>Load more</button>
      )}
    </div>
  )
}

export default Video
