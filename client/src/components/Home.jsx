import { Link } from 'react-router-dom'
import { useAuth } from '../context/auth-context.js'

function Home() {
  const { currentUser, logoutUser } = useAuth()

  return (
    <section className="page page-home">
      <h1>Pro Scouter</h1>
      <h3>Welcome, {currentUser ? currentUser.username : 'Guest'}!</h3>
      {currentUser ? (
        <button type="button" onClick={logoutUser}>Logout</button>
      ) : (
        <div className="home-actions">
          <Link to="/login">Login</Link>
          <Link to="/signup">Sign up</Link>
        </div>
      )}
    </section>
  )
}

export default Home
