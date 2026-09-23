import { Link } from 'react-router-dom'
import { useAuth } from '../context/auth-context.js'

function RecruiterHome() {
  const { currentRecruiter, logoutRecruiter } = useAuth()

  if (!currentRecruiter) {
    return (
      <div className="page">
        <p>Please <Link to="/recruiter-login">log in</Link> as a recruiter.</p>
      </div>
    )
  }

  return (
    <section className="page">
      <h3>Welcome, {currentRecruiter.recruiter_username}!</h3>
      <p className="muted">{currentRecruiter.recruiter_name}</p>
      <button type="button" onClick={logoutRecruiter}>Logout</button>
    </section>
  )
}

export default RecruiterHome
