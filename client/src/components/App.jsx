import { Outlet } from 'react-router-dom'
import React, {useState, useEffect} from 'react'
import Navbar from './Navbar'

function App() {

  // STATE //

  const [currentUser, setCurrentUser] = useState(null);

  // FETCH SESSION FOR LOGIN

  useEffect(() => {
    fetch('/api/get-session')
    .then(response => {
      if (response.status === 200) {
        response.json()
        .then(loggedInUser => setCurrentUser(loggedInUser))
      }
    })
  }, []);

  return (
    <div>

      <Navbar />
      <Outlet context={{currentUser, setCurrentUser}}/>
    </div>
  )

}

export default App
