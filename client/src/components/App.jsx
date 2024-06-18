import { Outlet } from 'react-router-dom'
import React, {useState, useEffect} from 'react'
import Navbar from '../Navbar.jsx'
import Footer from './Footer.jsx';

const App = () => {
    const [currentUser, setCurrentUser] = useState(null);
    const [currentRecruiter, setCurrentRecruiter] = useState(null);
     // STATE //
     
    useEffect(() => {
        fetch('/api/get-session-user')
        .then(response => {
          if (response.status === 200) {
            response.json()
            .then(loggedInUser => setCurrentUser(loggedInUser))
            console.log("this works?")
          }
        })
    }, []);

    useEffect(() => {
      fetch('/api/get-session-recruiter')
     .then(response => {
       if (response.status === 200) {
         response.json()
        .then(loggedinrecruiter => setCurrentRecruiter(loggedinrecruiter))
         console.log("this works?")
       }
     })
    }, []);


    return (
            <div>
                {/* <Navbar className='navbar'/> */}
                <div>
                    <Outlet context={{currentUser, setCurrentUser, currentRecruiter, setCurrentRecruiter}}/>
                </div>
                <Footer/>
                </div>
          

    );
};

export default App;
