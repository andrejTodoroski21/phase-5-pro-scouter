import { Link, useOutletContext } from 'react-router-dom'

function Home () {
    const{currentUser} =useOutletContext()
    // const{setCurrentUser} =useOutletContext()

    

    return (

    <div>
       
            <Link to="/videos"></Link>
            <p className='icon-text'>Listings</p>
        
            <br/>

            {/* <Link to="/profile"></Link>
            <p className='icon-text'>My Profile</p> */}

            <br/>

            <Link to="/about"></Link>
            <p className='icon-text' >About</p>
            
                    <h3 style={{color: 'white'}}>Welcome, {currentUser ? currentUser.username : 'Guest'}!</h3>
                
            </div>
                
                
            
    )
}

export default Home
