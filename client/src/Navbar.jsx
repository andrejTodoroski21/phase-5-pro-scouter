import { Link } from 'react-router-dom'
import '../src/Navbar.css';

function Navbar () {

    return (
        <div className='navbar-container'>
            
            <Link className='videos-navbar' to="/videos">Videos</Link>
            &nbsp; &nbsp;
            <Link className='messages-navbar' to="/messages">Messages</Link>
            &nbsp; &nbsp;
            <Link className='add-video-navbar' to="/add-video">Add Video</Link>
            &nbsp; &nbsp;
            <Link className='auth-navbar' to="/login">Login | <Link className='navbar' to='/signup'> Signup</Link></Link>
            &nbsp; &nbsp;
            <Link className='profile-navbar' to="/profile">Profile</Link>
            
        </div>
    )
}

export default Navbar