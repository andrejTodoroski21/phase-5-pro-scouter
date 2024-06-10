// src/components/Video.jsx
import React, { useEffect, useState } from 'react';
import YouTube from 'react-youtube';
import ValorantButton from './ValorantButton';
const Video = () => {
    const [videos, setVideos] = useState([]);
    const [error, setError] = useState(null);

    useEffect(() => {
        getVideos();
    }, []);

    const getVideos = async () => {
        try {
            const response = await fetch('/api/videos');
            if (!response.ok) {
                throw new Error('Failed to fetch videos');
            }
            const data = await response.json();
            setVideos(data);
            setError(null);
        } catch (error) {
            console.error('Error fetching videos:', error);
            setError('Error fetching videos. Please try again later.');
        }
    };

    return (
        <div>
            <h1>Video</h1>
            {error && <p>{error}</p>}
            <div>
                {videos.map((video) => (
                    <div key={video.id}>
                        <YouTube videoId={video.file_path} />
                        <p>{video.title}</p>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default Video;
