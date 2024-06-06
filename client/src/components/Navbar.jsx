import React from 'react';
import { Link } from 'react-router-dom';

const Navbar = () => {
    return (
        <nav>
            <ul>
                <li>
                    <Link to="/">Home</Link>
                </li>
                <li>
                    <Link to="/signup">Signup</Link>
                </li>
                <li>
                    <Link to="/login">Login</Link>
                </li>
                <li>
                    <Link to="/userdetails">User Details</Link>
                </li>
                <li>
                    <Link to="/videos">Videos</Link>
                </li>
                <li>
                    <Link to="/add-video">Add Video</Link> {/* Add this link */}
                </li>
            </ul>
        </nav>
    );
};

export default Navbar;
