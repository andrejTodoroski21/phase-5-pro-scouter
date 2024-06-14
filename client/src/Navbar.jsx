import React from 'react';
import { Link, BrowserRouter } from 'react-router-dom';

const Navbar = () => {
    return (
        <BrowserRouter>
        
        <header>

        <nav>
            <ul className='nav-links'>
                <li>
                    <Link to="/signup">Signup</Link><a> / </a><Link to="/login">Login</Link>
                </li>
                <li>
                    <Link to="/userdetails">User Details</Link>
                </li>
                <li>
                    <Link to="/videos">Videos</Link>
                </li>
                <li>
                    <Link to="/add-video">Add Video</Link>
                </li>
                <li>
                    <Link to="/messages">Messages</Link>
                </li>
            </ul>
        </nav>
        </header>
        </BrowserRouter>
    );
};

export default Navbar;

