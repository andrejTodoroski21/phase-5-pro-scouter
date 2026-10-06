import { NavLink } from 'react-router-dom'
import { useAuth } from './context/auth-context.js'

const linkClass = ({ isActive }) => (isActive ? 'nav-link is-active' : 'nav-link')

function Navbar() {
  const { currentUser, isRecruiter } = useAuth()

  return (
    <nav className="navbar-container">
      <NavLink className={linkClass} to="/">Home</NavLink>
      <NavLink className={linkClass} to="/videos">Clips</NavLink>
      {currentUser && <NavLink className={linkClass} to="/messages">Messages</NavLink>}
      {currentUser && !isRecruiter && (
        <NavLink className={linkClass} to="/add-video">Add Clip</NavLink>
      )}
      {currentUser && !isRecruiter && (
        <NavLink className={linkClass} to="/profile">Profile</NavLink>
      )}
      {isRecruiter && <NavLink className={linkClass} to="/recruiter-home">Recruiter</NavLink>}
      {!currentUser && (
        <>
          <NavLink className={linkClass} to="/login">Login</NavLink>
          <NavLink className={linkClass} to="/signup">Signup</NavLink>
        </>
      )}
    </nav>
  )
}

export default Navbar
