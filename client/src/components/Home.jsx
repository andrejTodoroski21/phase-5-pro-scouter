import React from 'react';
import { useOutletContext} from 'react-router-dom';



function Home(){
    const { currentUser } = useOutletContext()
    const { setCurrentUser } = useOutletContext()

    function handleLogout() {
        setCurrentUser(null)
        fetch('/api/logout', { method: 'DELETE' })
    
    }

return (
    <div>
        <div>
        </div>
        <h3>Welcome, {currentUser ? currentUser.username : 'Guest'}!</h3>
        <button onClick={handleLogout}>Logout</button>
    </div>

);
}
export default Home