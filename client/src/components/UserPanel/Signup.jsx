import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../../lib/api'
import { useAuth } from '../../context/auth-context.js'

const Signup = () => {
  const { setCurrentUser } = useAuth()
  const [form, setForm] = useState({
    username: '', first_name: '', last_name: '', password: '',
  })
  const [error, setError] = useState(null)
  const navigate = useNavigate()

  const update = (field) => (event) =>
    setForm((previous) => ({ ...previous, [field]: event.target.value }))

  function handleSignup(event) {
    event.preventDefault()
    setError(null)
    // Sends `password`; the server does the hashing. The old form posted a
    // field literally named `_hashed_password` straight from the input.
    api.post('/signup', form)
      .then((user) => {
        setCurrentUser(user)
        navigate('/videos')
      })
      .catch((err) => setError(err.message))
  }

  return (
    <div className="page auth-page auth-page-signup">
      <h2 className="create-account">CREATE AN ACCOUNT</h2>
      <form className="card auth-form" onSubmit={handleSignup}>
        <h5>Sign Up</h5>
        {error && <p className="error">{error}</p>}
        <input
          name="username" type="text" placeholder="USERNAME" autoComplete="username"
          value={form.username} onChange={update('username')} required
        />
        <input
          type="text" placeholder="FIRST NAME" autoComplete="given-name"
          value={form.first_name} onChange={update('first_name')} required
        />
        <input
          type="text" placeholder="LAST NAME" autoComplete="family-name"
          value={form.last_name} onChange={update('last_name')} required
        />
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
