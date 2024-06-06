import React, { useEffect, useState } from 'react';

const Video = () => {
    const [videos, setVideos] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [selectedVideo, setSelectedVideo] = useState(null);

    useEffect(() => {
        const fetchVideos = async () => {
            try {
                const response = await fetch('/api/videos');
                if (!response.ok) {
                    throw new Error('Failed to fetch videos');
                }
                const data = await response.json();
                setVideos(data);
                setLoading(false);
            } catch (error) {
                setError(error.message);
                setLoading(false);
            }
        };

        fetchVideos();
    }, []);

    // Function to extract the YouTube video ID
    const getYouTubeID = (url) => {
        const regex = /(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})/;
        const match = url.match(regex);
        return match ? match[1] : null;
    };

    const handleLike = (id) => {
        // Implement like functionality here
        console.log(`Liked video with id: ${id}`);
    };

    const handleComment = (id) => {
        // Implement comment functionality here
        console.log(`Commented on video with id: ${id}`);
    };

    return (
        <div>
            <h1>Videos</h1>
            <div className="video-list">
                {videos.map((video) => (
                    <div key={video.id} className="video-item">
                        <div className="card">
                            <div className="card-header">{video.title}</div>
                            <div className="card-body">
                                <p>
                                    <a 
                                        href="#"
                                        onClick={(e) => {
                                            e.preventDefault();
                                            setSelectedVideo(video.youtube_link);
                                        }}
                                    >
                                        {video.youtube_link}
                                    </a>
                                </p>
                            </div>
                            <div className="card-footer">
                                <button onClick={() => handleLike(video.id)}>Like</button>
                                <button onClick={() => handleComment(video.id)}>Comment</button>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
            {selectedVideo && (
                <div className="video-player">
                    <h2>Playing Video</h2>
                    <iframe
                        width="560"
                        height="315"
                        src={`https://www.youtube.com/embed/${getYouTubeID(selectedVideo)}`}
                        frameBorder="0"
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                        allowFullScreen
                        title="YouTube video player"
                    ></iframe>
                </div>
            )}
        </div>
    );
};

export default Video;
