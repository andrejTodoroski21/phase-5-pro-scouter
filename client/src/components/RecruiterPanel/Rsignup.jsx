// import React, { useState } from 'react';
// import { useNavigate, useOutletContext } from 'react-router-dom';


// const Signup = () => {
//     const { setCurrentRecruiter} = useOutletContext();
//     const [recruiterUsername, setRecruiterUsername] = useState('');
//     const [ recruiterName, setRecruiterName] = useState('');
//     const [_hashed_password, setPassword] = useState('');
//     const navigate = useNavigate();

//     const handleRecruiterSignup = async (event) => {
//         event.preventDefault();
//           fetch('/api/recruiters', {
//                 method: 'POST',
//                 headers: {'Content-Type': 'application/json', 'Accept': 'application/json'},
//                 body: JSON.stringify({recruiterUsername, recruiterName, _hashed_password}),
//             }).then(response => {
//                 if (response.ok) {
//                     response.json()
//                     .then(new_recruiter => {
//                         setCurrentRecruiter(new_recruiter)
//                         navigate('/videos');
//                     });
//                 } else {
//                     alert('signup unsuccessful')
//                 }
//             })
//     };

//     return (
//     <>
//         <main >
//         <body className='bg-image'>

           
        
//         <div className='create-account-div'>
//         <h2 className='create-account'>CREATE A RECRUITER ACCOUNT</h2>
//         </div>

//             <div className='signup-container'>
//                 <form className='signup-form' onSubmit={handleRecruiterSignup}>
//                     <div className = 'form-card'>
//                 <h5 className = 'signup text-center'>Sign Up</h5>
//                                 <div className='ivhuok field'>
//                                     <input
//                                         className='username-input'
//                                         name='username'
//                                         placeholder='USERNAME'
//                                         type="text"
//                                         value={recruiterUsername}
//                                         onChange={(e) => setRecruiterUsername(e.target.value)}
//                                         />
//                                 </div>
//                 <div>
//                     <input
//                         type="text"
//                         className='first-name'
//                         placeholder='FIRST NAME'
//                         value={recruiterName}
//                         onChange={(e) => setRecruiterName(e.target.value)}
//                         />
//                 </div>
//                 <div>
//                     <input
//                         type="password"
//                         className='password'
//                         placeholder='PASSWORD'
//                         value={_hashed_password}
//                         onChange={(e) => setPassword(e.target.value)}
//                         />
//                 </div>
//                 <br></br>
                
//                 <button className='valorant-button' type='submit'>Sign Up</button>
//                 <br></br>
//                 <a href='/login'>Already have an account?</a>
//                 </div>
//                 </form>
//             </div>
//             </body>
//             </main>
//     </>

//     );
// };

// export default Signup;
import React, { useState } from 'react';
import { useNavigate, useOutletContext } from 'react-router-dom';

const Signup = () => {
    const { setCurrentRecruiter } = useOutletContext();
    const [recruiter_username, setRecruiterUsername] = useState('');
    const [recruiter_name, setRecruiterName] = useState('');
    const [_hashed_password, setPassword] = useState('');
    const navigate = useNavigate();

    const handleRecruiterSignup = async (event) => {
        event.preventDefault();
        try {
            const response = await fetch('/api/recruiters', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json', 
                    'Accept': 'application/json' 
                },
                body: JSON.stringify({ recruiter_username, recruiter_name, _hashed_password }),
            });

            if (response.ok) {
                const new_recruiter = await response.json();
                setCurrentRecruiter(new_recruiter);
                navigate('/videos');
            } else {
                const errorData = await response.json();
                console.error('Signup unsuccessful:', errorData);
                alert('Signup unsuccessful. Please check your input and try again.');
            }
        } catch (error) {
            console.error('Error during signup:', error);
            alert('An error occurred during signup. Please try again later.');
        }
    };

    return (
        <main>
            <body className='bg-image'>
                <div className='create-account-div'>
                    <h2 className='create-account'>CREATE A RECRUITER ACCOUNT</h2>
                </div>
                <div className='signup-container'>
                    <form className='signup-form' onSubmit={handleRecruiterSignup}>
                        <div className='form-card'>
                            <h5 className='signup text-center'>Recruiter Sign Up</h5>
                            <div className='ivhuok field'>
                                <input
                                    className='username-input'
                                    name='username'
                                    placeholder='USERNAME'
                                    type='text'
                                    value={recruiter_username}
                                    onChange={(e) => setRecruiterUsername(e.target.value)}
                                />
                            </div>
                            <div>
                                <input
                                    type='text'
                                    className='first-name'
                                    placeholder='FIRST NAME'
                                    value={recruiter_name}
                                    onChange={(e) => setRecruiterName(e.target.value)}
                                />
                            </div>
                            <div>
                                <input
                                    type='password'
                                    className='password'
                                    placeholder='PASSWORD'
                                    value={_hashed_password}
                                    onChange={(e) => setPassword(e.target.value)}
                                />
                            </div>
                            <br />
                            <button className='valorant-button' type='submit'>Sign Up</button>
                            <br />
                            <a href='/login'>Already have an account?</a>
                        </div>
                    </form>
                </div>
            </body>
        </main>
    );
};

export default Signup;

