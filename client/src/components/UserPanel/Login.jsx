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
        <div>
            <h2>Login</h2>
            <form onSubmit={handleLogin}>
                <div>
                    <label>Username:</label>
                    <input
                        type="text"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                    />
                </div>
                <div>
                    <label>Password:</label>
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                    />
                </div>
                <button type="submit">Login</button>
                
            </form>
        </div>
    );
};

export default Login;
