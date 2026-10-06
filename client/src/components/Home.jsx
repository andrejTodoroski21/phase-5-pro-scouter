import { Link } from 'react-router-dom'
import { useAuth } from '../context/auth-context.js'

function Home() {
  const { currentUser, logout } = useAuth()

  return (
    <section className="page page-home">
      <h1>Pro Scouter</h1>
      <h3>Welcome, {currentUser ? currentUser.display_name : 'Guest'}!</h3>
      {currentUser ? (
        <button type="button" onClick={logout}>Logout</button>
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
