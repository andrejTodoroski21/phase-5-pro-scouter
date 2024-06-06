import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const AddVideo = () => {
    const [title, setTitle] = useState('');
    const [youtubeLink, setYoutubeLink] = useState('');
    const [userId, setUserId] = useState(1); // Change this according to your user management logic
    const [error, setError] = useState(null);
    const navigate = useNavigate();

    const handleSubmit = async (event) => {
        event.preventDefault();
        try {
            const response = await fetch('/api/videos', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ title, youtube_link: youtubeLink, user_id: userId })
            });

            if (!response.ok) {
                throw new Error('Failed to add video');
            }

            navigate('/videos');
        } catch (error) {
            setError(error.message);
        }
    };

    return (
        <div>
            <h1>Add Video</h1>
            {error && <div>Error: {error}</div>}
            <form onSubmit={handleSubmit}>
                <div>
                    <label htmlFor="title">Title:</label>
                    <input
                        id="title"
                        type="text"
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                        required
                    />
                </div>
                <div>
                    <label htmlFor="youtubeLink">YouTube Link:</label>
                    <input
                        id="youtubeLink"
                        type="text"
                        value={youtubeLink}
                        onChange={(e) => setYoutubeLink(e.target.value)}
                        required
                    />
                </div>
                <button type="submit">Add Video</button>
            </form>
        </div>
    );
};

export default AddVideo;
