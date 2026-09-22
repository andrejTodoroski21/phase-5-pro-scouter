import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../../lib/api'
import { useAuth } from '../../context/auth-context.js'

const RecruiterSignup = () => {
  const { setCurrentRecruiter } = useAuth()
  const [form, setForm] = useState({
    recruiter_username: '', recruiter_name: '', password: '',
  })
  const [error, setError] = useState(null)
  const navigate = useNavigate()

  const update = (field) => (event) =>
    setForm((previous) => ({ ...previous, [field]: event.target.value }))

  function handleRecruiterSignup(event) {
    event.preventDefault()
    setError(null)
    api.post('/recruiters', form)
      .then((recruiter) => {
        setCurrentRecruiter(recruiter)
        navigate('/recruiter-home')
      })
      .catch((err) => setError(err.message))
  }

  return (
    <div className="page auth-page auth-page-signup">
      <h2 className="create-account">CREATE A RECRUITER ACCOUNT</h2>
      <form className="card auth-form" onSubmit={handleRecruiterSignup}>
        <h5>Recruiter Sign Up</h5>
        {error && <p className="error">{error}</p>}
        <input
          type="text" placeholder="USERNAME" autoComplete="username"
          value={form.recruiter_username} onChange={update('recruiter_username')} required
        />
        <input
          type="text" placeholder="ORGANIZATION" autoComplete="organization"
          value={form.recruiter_name} onChange={update('recruiter_name')} required
        />
        <input
          type="password" placeholder="PASSWORD" autoComplete="new-password"
          value={form.password} onChange={update('password')} required
        />
        <button type="submit">Sign Up</button>
        <Link className="auth-alt" to="/recruiter-login">Already have an account?</Link>
      </form>
    </div>
  )
}

export default RecruiterSignup
