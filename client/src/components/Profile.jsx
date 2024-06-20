import React, { useEffect, useState } from "react";
import { Link, useOutletContext } from 'react-router-dom';
import YouTube from 'react-youtube';


function Profile() {
    const { currentUser } = useOutletContext();
    const { setCurrentUser } = useOutletContext();

    const [videos, setVideos] = useState([]);

    useEffect(() => {
        fetch('/api/get-session')
            .then(response => {
                if (response.status === 200) {
                    response.json()
                        .then(loggedInUser => setCurrentUser(loggedInUser))
                }
            })
    }, []);

    useEffect(() => {
        fetch('/api/videos')
            .then(res => res.json())
            .then(data => setVideos(data));
    }, []);
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
        <>
                <div >
                    <div className="profile-bg">
                        <div className="profile-card">
                            <h1>My Videos</h1>             
                        </div>
                    </div>
                    <div className="profile-background">
                    
                        <div >
                            {currentUser && videos.filter(video => video.user_id === currentUser.id).length > 0 ? (
                                <div className="profile-div">
                                    {videos
                                        .filter(video => video.user_id === currentUser.id)
                                        .map(video => (
                                                <div className="my-listing">
                                                    <YouTube  videoId={video.file_path} />
                                                    {/* <h4>{video.title}</h4> */}
                                                    {/* <h5>{video.time_uploaded}</h5> */}
                                                    <button onClick={()=>deleteVideos(video.id)}>Delete</button>

                                                <br />
                                                </div>
                                        ))}
                                </div>
                            ) : (
                                <h3>No Videos found</h3>
                            )}
                        </div>
                    </div>
                </div>
        </>
    )
}

export default Profile;

