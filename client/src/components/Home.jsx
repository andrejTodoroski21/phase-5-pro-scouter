import React from 'react';
import { useOutletContext } from 'react-router-dom';

const Home = () => {
    const {currentUser} = useOutletContext();
    const {setCurrentUser} = useOutletContext();

    function handleLogout() {
        setCurrentUser(null)
        fetch('/api/logout', { method: 'DELETE' })
    }

    return (
        <div>
            <div>
            <h1>Welcome to Our App!</h1>
            <h3>Welcome, {currentUser ? currentUser.username : 'Guest'}!</h3>
            </div>
            <div class="window-body">
                    <p>Enjoy browsing, selling, and discussing your old crap!</p>
                    {currentUser && <button onClick={handleLogout}>Logout</button>}
                </div>
    
        </div>
    );
};

export default Home;
