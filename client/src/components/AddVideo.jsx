// import React, { useState } from 'react';
// import { useNavigate } from 'react-router-dom';

// const AddVideo = () => {
//     const [title, setTitle] = useState('');
//     const [youtubeLink, setYoutubeLink] = useState('');
//     const [userId, setUserId] = useState(1); // Change this according to your user management logic
//     const [error, setError] = useState(null);
//     const navigate = useNavigate();

//     const handleSubmit = async (event) => {
//         event.preventDefault();
//         try {
//             const response = await fetch('/api/videos', {
//                 method: 'POST',
//                 headers: {
//                     'Content-Type': 'application/json'
//                 },
//                 body: JSON.stringify({ title, file_path: youtubeLink, user_id: userId })
//             });

//             if (!response.ok) {
//                 throw new Error('Failed to add video');
//             }

//             navigate('/videos');
//         } catch (error) {
//             setError(error.message);
//         }
//     };

//     return (
//         <div>
//             <h1>Add Video</h1>
//             {error && <div>Error: {error}</div>}
//             <form onSubmit={handleSubmit}>
//                 <div>
//                     <label htmlFor="title">Title:</label>
//                     <input
//                         id="title"
//                         type="text"
//                         value={title}
//                         onChange={(e) => setTitle(e.target.value)}
//                         required
//                     />
//                 </div>
//                 <div>
//                     <label htmlFor="youtubeLink">YouTube Link:</label>
//                     <input
//                         id="youtubeLink"
//                         type="text"
//                         value={youtubeLink}
//                         onChange={(e) => setYoutubeLink(e.target.value)}
//                         required
//                     />
//                 </div>
//                 <button class='btn' type="submit">Add Video</button>
//             </form>
//         </div>
//     );
// };

// export default AddVideo;

import { useState } from 'react'
import { useOutletContext } from 'react-router-dom'
import { useNavigate } from 'react-router-dom';


function NewListing() {
  const { currentUser, setCurrentUser } = useOutletContext()
  // STATE //

  const [title, setTitle] = useState('')
  const [file_path, setFilePath] = useState('')
  const navigate = useNavigate();



  // EVENTS //

  function handleSubmit(e) {
    e.preventDefault()

    const user_id = currentUser.id;

    fetch('/api/videos', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: JSON.stringify({ title, file_path, user_id }),
    })
    .then(response => {
      if (response.ok) {
        response.json()
        .then( newVideo => {
          setCurrentUser(newVideo) 
          navigate('/profile');
        });
      } else {
        alert("adding video unsuccessful")
      }
    })
  }

  // RENDER //

  return (

    <div className="window" style={{ marginLeft: '5em', width: 300 }}>
    <div className="title-bar">
    </div>
    <div className="window-body">
    <form className='user-form' onSubmit={handleSubmit}>

      <h2>New Videos</h2>


    <div>
        <label for="item_name">Video Title</label>
        <input id="item_name" type="text" onChange={e => setTitle(e.target.value)}
      value={title}/>
    </div>

    <div>
        <label for="link">Link</label>
        <input id="link" type="text" onChange={e => setFilePath(e.target.value)}
      value={file_path}/>
    </div>

    <input type="submit"
      value='Add item'
    />

    </form>


  </div>
  </div>
  )

}

export default NewListing

