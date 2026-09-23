import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../../lib/api'
import { useAuth } from '../../context/auth-context.js'

const Login = () => {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const { setCurrentUser } = useAuth()
  const navigate = useNavigate()

  function handleLogin(event) {
    event.preventDefault()
    setError(null)
    api.post('/login', { username, password })
      .then((user) => {
        setCurrentUser(user)
        navigate('/videos')
      })
      .catch((err) => setError(err.message))
  }

  return (
    <div className="page auth-page">
      <form className="card auth-form" onSubmit={handleLogin}>
        <h3>Login</h3>
        {error && <p className="error">{error}</p>}
        <input
          type="text"
          value={username}
          placeholder="USERNAME"
          autoComplete="username"
          onChange={(e) => setUsername(e.target.value)}
          required
        />
        <input
          type="password"
          value={password}
          placeholder="PASSWORD"
          autoComplete="current-password"
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <button type="submit">Login</button>
        <Link className="auth-alt" to="/signup">Need an account?</Link>
      </form>
    </div>
  )
}

export default Login
