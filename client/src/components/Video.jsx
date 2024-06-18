// src/components/Video.jsx
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

    const deleteVideos =(videoId)=>{
        fetch(`/api/videos/${videoId}`, {
            method: 'DELETE'
        })
        .then(response=>{
            if(response.ok){
                setVideos(videos.filter(video=> video.id !== videoId));
            }else{
                alert("Failed to delete video")
            }
        })
        .catch(error=>{
            console.error('Error deleting video:', error);
            alert("Error deleting video");
        });
        
    }
    

    return (
        <div>
            <h1>Browse Videos</h1>
            <div className='video-container'>
                {videos.map((video) => (
                    <div key={video.id}>
                        <p>{video.title}</p>
                        <YouTube videoId={video.file_path} />
                        <button onClick={()=>deleteVideos(video.id)}>Delete</button>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default Video;
