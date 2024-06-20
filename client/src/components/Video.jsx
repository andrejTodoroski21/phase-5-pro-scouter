import React, { useEffect, useState } from 'react';
import YouTube from 'react-youtube';

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
    const opts = {
        height: '390',
        width: '640',
        playerVars: {
            autoplay: 0,
            rel: 0, // Disable related videos at the end
            modestbranding: 1, // Remove YouTube logo
            iv_load_policy: 3, // Disable video annotations
            showinfo: 0, // Hide video title and uploader info
        },
    };

    return (
        <body className='videos-bg-image'>
            <div>
                <h1 className='browse'>Browse Videos</h1>
                <div className='video-container'>
                    {videos.map((video) => (
                        <div className='videos' key={video.id}>
                            <YouTube opts={opts} videoId={video.file_path} />
                            <br />
                            <p className='video-title'>{video.title}</p>
                            <p>By: {video.uploader?.username}</p> 
                        </div>
                    ))}
                </div>
            </div>
        </body>
    );
};

export default Video;
