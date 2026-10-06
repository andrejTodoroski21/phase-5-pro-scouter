import LiteYouTube from './LiteYouTube.jsx'

/**
 * Plays a clip from either source.
 *
 * Uploaded clips are plain <video> elements with `preload="none"`, so the feed
 * costs one poster image per card until something is actually played — the
 * same reason YouTube clips go through the facade rather than a live iframe.
 */
function ClipPlayer({ video }) {
  if (video.source === 'upload' && video.video_url) {
    return (
      <div className="video-frame">
        <video
          src={video.video_url}
          controls
          preload="none"
          playsInline
          // Ask the browser for a frame a moment in, so the poster is not the
          // black first frame most clips start on.
          onLoadedMetadata={(e) => { if (e.target.currentTime === 0) e.target.currentTime = 0.1 }}
        />
      </div>
    )
  }
  return <LiteYouTube videoId={video.file_path} title={video.title} />
}

export default ClipPlayer
