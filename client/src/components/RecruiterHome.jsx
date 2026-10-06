import { Link } from 'react-router-dom'
import { useAuth } from '../context/auth-context.js'

function RecruiterHome() {
  const { currentUser, isRecruiter, logout, loading } = useAuth()

  if (loading) return <p className="muted page">Loading…</p>
  if (!isRecruiter) {
    return (
      <div className="page">
        <p>
          This page is for recruiter accounts.{' '}
          {currentUser ? 'You are signed in as a player.' : <Link to="/login">Log in</Link>}
        </p>
      </div>
    )
  }

  return (
    <section className="page">
      <h3>Welcome, {currentUser.organization}!</h3>
      <p className="muted">Signed in as {currentUser.username}</p>
      <button type="button" onClick={logout}>Logout</button>
    </section>
  )
}

export default RecruiterHome
