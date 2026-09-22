import { useState } from 'react'

/**
 * A YouTube embed that costs one image until you click it.
 *
 * `react-youtube` mounts a real <iframe> per video immediately, and each one
 * pulls well over a megabyte of player JavaScript plus its own trackers. A grid
 * of a dozen videos meant a dozen of those competing for the main thread on
 * page load, which is what made the video and profile pages crawl.
 *
 * Here we render the thumbnail and only swap in the iframe on click, which is
 * the same trick YouTube itself uses for embeds above the fold.
 */
function LiteYouTube({ videoId, title = 'Video' }) {
  const [active, setActive] = useState(false)

  if (!videoId) return null

  if (active) {
    return (
      <div className="video-frame">
        <iframe
          src={`https://www.youtube-nocookie.com/embed/${videoId}?autoplay=1&rel=0&modestbranding=1&iv_load_policy=3`}
          title={title}
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
          loading="lazy"
        />
      </div>
    )
  }

  return (
    <button
      type="button"
      className="video-frame video-facade"
      onClick={() => setActive(true)}
      aria-label={`Play ${title}`}
    >
      <img
        src={`https://i.ytimg.com/vi/${videoId}/hqdefault.jpg`}
        alt=""
        loading="lazy"
        decoding="async"
        width="480"
        height="360"
      />
      <span className="video-play" aria-hidden="true" />
    </button>
  )
}

export default LiteYouTube
