import { Link } from 'react-router-dom'

function Navbar () {

    return (
        <div>
            
            <Link className='navbar' to="/">Home</Link>
            &nbsp; &nbsp;
            <Link className='navbar' to="/videos">Videos</Link>
            &nbsp; &nbsp;
            <Link className='navbar' to="/profile">Profile</Link>
            &nbsp; &nbsp;
            <Link className='navbar' to="/about">About</Link>
            &nbsp; &nbsp;
            <Link className='navbar' to="/add-video">Add Video</Link>
            &nbsp; &nbsp;
            <Link className='navbar' to="/login">Login</Link>
            &nbsp; &nbsp;
            <Link className='navbar' to="/signup">Sign Up</Link>
            &nbsp; &nbsp;
            <Link className='navbar' to="/messages">Messages</Link>
            
        </div>
    )
}

export default Navbar