function UserDetails({currentUser, setCurrentUser}) {

    function handleLogout() {
      setCurrentUser(null)
      fetch('/api/logout', { method: 'DELETE' })
    }
  
      return (
        <div className='user-details'>
          <h2>Welcome {currentUser.username}!</h2>
          <button onClick={handleLogout}>Logout</button>
        </div>
      )
    
    }
    
    export default UserDetails
    