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

    return (
        <>
            <br />
            <br />
                <div >
                    <div >
                        <div >
                            <h3>My Videos</h3>
                        </div>
                        <div >
                            {currentUser && videos.filter(video => video.user_id === currentUser.id).length > 0 ? (
                                <div>
                                    {videos
                                        .filter(video => video.user_id === currentUser.id)
                                        .map(video => (
                                                <div className="my-listing">
                                                    <h4>{video.title}</h4>
                                                    <YouTube videoId={video.file_path} />
                                                    <h5>{video.time_uploaded}</h5>
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

