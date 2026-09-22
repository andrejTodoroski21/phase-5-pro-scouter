import { NavLink } from 'react-router-dom'
import { useAuth } from './context/auth-context.js'

const linkClass = ({ isActive }) => (isActive ? 'nav-link is-active' : 'nav-link')

function Navbar() {
  const { currentUser, currentRecruiter } = useAuth()

  return (
    <nav className="navbar-container">
      <NavLink className={linkClass} to="/">Home</NavLink>
      <NavLink className={linkClass} to="/videos">Videos</NavLink>
      <NavLink className={linkClass} to="/messages">Messages</NavLink>
      <NavLink className={linkClass} to="/add-video">Add Video</NavLink>
      {currentUser ? (
        <NavLink className={linkClass} to="/profile">Profile</NavLink>
      ) : (
        // These were previously one <Link> nested inside another, which is
        // invalid HTML — the browser silently unnested it.
        <>
          <NavLink className={linkClass} to="/login">Login</NavLink>
          <NavLink className={linkClass} to="/signup">Signup</NavLink>
        </>
      )}
      {currentRecruiter && (
        <NavLink className={linkClass} to="/recruiter-home">Recruiter</NavLink>
      )}
    </nav>
  )
}

export default Navbar
