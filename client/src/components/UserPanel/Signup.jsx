import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';


const Signup = () => {
    const [username, setUsername] = useState('');
    const [firstName, setFirstName] = useState('');
    const [lastName, setLastName] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleSignup = async (event) => {
        event.preventDefault();
        try {
            const response = await fetch('/api/signup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username,
                    first_name: firstName,
                    last_name: lastName,
                    _hashed_password: password,
                }),
            });
            if (response.ok) {
                navigate('/');
            } else {
                const data = await response.json();
                setError(data.error || 'Error signing up');
            }
        } catch (err) {
            setError('Error signing up');
        }
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
                        value={firstName}
                        onChange={(e) => setFirstName(e.target.value)}
                        />
                </div>
                <div>
                    <input
                        type="text"
                        className='last-name'
                        placeholder='LAST NAME'
                        value={lastName}
                        onChange={(e) => setLastName(e.target.value)}
                        />
                </div>
                <div>
                    <input
                        type="password"
                        className='password'
                        placeholder='PASSWORD'
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        />
                </div>
                <br></br>
                
                <button className='valorant-button' type='submit'>Sign Up</button>
                <br></br>
                <a href='/login'>Already have an account?</a>
                
                {error && <p>{error}</p>}
                </div>
                </form>
            </div>
            </main>
                        </>

    );
};

export default Signup;
