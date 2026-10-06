import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../../lib/api'
import { useAuth } from '../../context/auth-context.js'

/** One form for both account types; `role` is the only thing that differs. */
const Signup = () => {
  const { setCurrentUser } = useAuth()
  const [role, setRole] = useState('player')
  const [form, setForm] = useState({
    username: '', first_name: '', last_name: '', organization: '', password: '',
  })
  const [error, setError] = useState(null)
  const navigate = useNavigate()

  const update = (field) => (event) =>
    setForm((previous) => ({ ...previous, [field]: event.target.value }))

  function handleSignup(event) {
    event.preventDefault()
    setError(null)
    const body = role === 'recruiter'
      ? { username: form.username, password: form.password, role, organization: form.organization }
      : { username: form.username, password: form.password, role,
          first_name: form.first_name, last_name: form.last_name }
    api.post('/signup', body)
      .then((user) => {
        setCurrentUser(user)
        navigate(role === 'recruiter' ? '/recruiter-home' : '/videos')
      })
      .catch((err) => setError(err.message))
  }

  return (
    <div className="page auth-page auth-page-signup">
      <h2 className="create-account">CREATE AN ACCOUNT</h2>
      <form className="card auth-form" onSubmit={handleSignup}>
        <div className="role-toggle">
          <button
            type="button"
            className={role === 'player' ? 'is-selected' : ''}
            onClick={() => setRole('player')}
          >
            Player
          </button>
          <button
            type="button"
            className={role === 'recruiter' ? 'is-selected' : ''}
            onClick={() => setRole('recruiter')}
          >
            Recruiter
          </button>
        </div>
        {error && <p className="error">{error}</p>}
        <input
          name="username" type="text" placeholder="USERNAME" autoComplete="username"
          value={form.username} onChange={update('username')} required
        />
        {role === 'player' ? (
          <>
            <input
              type="text" placeholder="FIRST NAME" autoComplete="given-name"
              value={form.first_name} onChange={update('first_name')} required
            />
            <input
              type="text" placeholder="LAST NAME" autoComplete="family-name"
              value={form.last_name} onChange={update('last_name')} required
            />
          </>
        ) : (
          <input
            type="text" placeholder="ORGANIZATION" autoComplete="organization"
            value={form.organization} onChange={update('organization')} required
          />
        )}
        <input
          type="password" placeholder="PASSWORD" autoComplete="new-password"
          value={form.password} onChange={update('password')} required
        />
        <button type="submit">Sign Up</button>
        <Link className="auth-alt" to="/login">Already have an account?</Link>
      </form>
    </div>
  )
}

export default Signup
