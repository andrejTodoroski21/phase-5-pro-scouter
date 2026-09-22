import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../../lib/api'
import { useAuth } from '../../context/auth-context.js'

const RecruiterLogin = () => {
  const [recruiterUsername, setRecruiterUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const { setCurrentRecruiter } = useAuth()
  const navigate = useNavigate()

  function handleRecruiterLogin(event) {
    event.preventDefault()
    setError(null)
    api.post('/recruiters-login', { recruiter_username: recruiterUsername, password })
      .then((recruiter) => {
        setCurrentRecruiter(recruiter)
        navigate('/recruiter-home')
      })
      .catch((err) => setError(err.message))
  }

  return (
    <div className="page auth-page">
      <form className="card auth-form" onSubmit={handleRecruiterLogin}>
        <h3>Recruiter Login</h3>
        {error && <p className="error">{error}</p>}
        <input
          type="text" value={recruiterUsername} placeholder="USERNAME" autoComplete="username"
          onChange={(e) => setRecruiterUsername(e.target.value)} required
        />
        <input
          type="password" value={password} placeholder="PASSWORD" autoComplete="current-password"
          onChange={(e) => setPassword(e.target.value)} required
        />
        <button type="submit">Login</button>
        <Link className="auth-alt" to="/recruiter-signup">Need a recruiter account?</Link>
      </form>
    </div>
  )
}

export default RecruiterLogin
