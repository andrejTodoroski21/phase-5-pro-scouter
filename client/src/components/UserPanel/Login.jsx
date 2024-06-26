import React, { useState } from 'react';
import { useNavigate, useOutletContext } from 'react-router-dom';

const Login = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const {setCurrentUser} = useOutletContext()

    const navigate = useNavigate();

    const handleLogin = async (event) => {
        event.preventDefault();
        
            fetch('/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({ username, password }),
            }).then(response =>{
                if (response.ok) {
                    response.json().then(username=>{
                        setCurrentUser(username);
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
                    <form className='login-form' onSubmit={handleLogin}>
                    <div className='login-card'>
                        <h3 className='login-text-center'>Login</h3>
                        <div>
                            <input
                            type="text"
                            value={username}
                            placeholder='USERNAME'
                            onChange={(e) => setUsername(e.target.value)}
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

export default Login;
