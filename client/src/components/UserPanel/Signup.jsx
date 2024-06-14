import React, { useState } from 'react';
import { useNavigate, useOutletContext } from 'react-router-dom';


const Signup = () => {
    const { setCurrentUser} = useOutletContext();
    const [username, setUsername] = useState('');
    const [first_name, setFirstName] = useState('');
    const [last_name, setLastName] = useState('');
    const [_hashed_password, setPassword] = useState('');
    const navigate = useNavigate();

    const handleSignup = async (event) => {
        event.preventDefault();
          fetch('/api/signup', {
                method: 'POST',
                headers: {'Content-Type': 'application/json', 'Accept': 'application/json'},
                body: JSON.stringify({username, first_name, last_name, _hashed_password}),
            }).then(response => {
                if (response.ok) {
                    response.json()
                    .then(new_user => {
                        setCurrentUser(new_user)
                        navigate('/videos');
                    });
                } else {
                    alert('signup unsuccessful')
                }
            })
    };

    return (
        <>
        <main>

        
        <div className='create-account-div'>
        <h2 className='create-account'>CREATE AN ACCOUNT</h2>
        </div>

            <div className='signup-container'>
                <form className='signup-form' onSubmit={handleSignup}>
                    <div className = 'form-card'>
                <h5 className = 'signup text-center'>Sign Up</h5>
                                <div className='ivhuok field'>
                                    <input
                                        className='username-input'
                                        name='username'
                                        placeholder='USERNAME'
                                        type="text"
                                        value={username}
                                        onChange={(e) => setUsername(e.target.value)}
                                        />
                                </div>
                <div>
                    <input
                        type="text"
                        className='first-name'
                        placeholder='FIRST NAME'
                        value={first_name}
                        onChange={(e) => setFirstName(e.target.value)}
                        />
                </div>
                <div>
                    <input
                        type="text"
                        className='last-name'
                        placeholder='LAST NAME'
                        value={last_name}
                        onChange={(e) => setLastName(e.target.value)}
                        />
                </div>
                <div>
                    <input
                        type="password"
                        className='password'
                        placeholder='PASSWORD'
                        value={_hashed_password}
                        onChange={(e) => setPassword(e.target.value)}
                        />
                </div>
                <br></br>
                
                <button className='valorant-button' type='submit'>Sign Up</button>
                <br></br>
                <a href='/login'>Already have an account?</a>
                </div>
                </form>
            </div>
            </main>
                        </>

    );
};

export default Signup;
