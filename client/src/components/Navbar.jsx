import React from 'react';
import { Link } from 'react-router-dom';

const Navbar = () => {
    return (
        <header>

        <nav>
            <ul className='nav-links'>
                <li>
                    <Link to="/">Home</Link>
                </li>
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
            </ul>
        </nav>
        </header>
    );
};

export default Navbar;
