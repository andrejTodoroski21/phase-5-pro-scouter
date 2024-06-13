import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './Navbar';
import Home from './Home';
import Login from './UserPanel/Login';
import Signup from './UserPanel/Signup';
import UserDetails from './UserPanel/Userdetails';
import Video from './Video';
import AddVideo from './AddVideo';

const App = () => {
    return (
        <Router>
            <div>
                <Navbar />
                <Routes>
                    <Route path="/" element={<Home />} />
                    <Route path="/login" element={<Login />} />
                    <Route path="/signup" element={<Signup />} />
                    <Route path="/userdetails" element={<UserDetails />} />
                    <Route path="/videos" element={<Video />} />
                    <Route path="/add-video" element={<AddVideo />} /> 
                </Routes>
            </div>
        </Router>
    );
};

export default App;
