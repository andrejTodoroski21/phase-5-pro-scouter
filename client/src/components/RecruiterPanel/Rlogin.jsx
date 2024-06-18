import React, { useState } from 'react';
import { useNavigate, useOutletContext } from 'react-router-dom';

const RecruiterLogin = () => {
    const [recruiter_username, setRecruiterUsername] = useState('');
    const [password, setPassword] = useState('');
    const {setCurrentRecruiter} = useOutletContext()

    const navigate = useNavigate();

    const handleRecruiterLogin = async (event) => {
        event.preventDefault();
        
            fetch('/api/recruiters-login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({ recruiter_username, password }),
            }).then(response =>{
                if (response.ok) {
                    response.json().then(recruiter_username=>{
                        setCurrentRecruiter(recruiter_username);
                        navigate('/videos');
                    })
                } else {
                    alert('Invalid username or password')
                }
            });
    };

    return (
        <div className='login-bg-image'>
            <div className='login-container'>
                    <form className='login-form' onSubmit={handleRecruiterLogin}>
                    <div className='login-card'>
                        <h3 className='login-text-center'>Recruiter Login</h3>
                        <div>
                            <input
                            type="text"
                            value={recruiter_username}
                            placeholder='USERNAME'
                            onChange={(e) => setRecruiterUsername(e.target.value)}
                            />
                        </div>
                    <div>
                        <input
                        type="password"
                        placeholder='PASSWORD'
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        />
                    </div>
                    <button type="submit">Login</button>
                    
                        </div>
                </form>
            </div>
        </div>
    );
};

export default RecruiterLogin;
