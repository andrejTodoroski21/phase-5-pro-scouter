import { useState } from 'react'
import {useOutletContext} from 'react-router-dom'
import { useNavigate } from 'react-router-dom';

function Login() {

  const [user, setUser] = useState('')
  const [password, setPassword] = useState('')
  const {setCurrentUser} = useOutletContext()
  const navigate = useNavigate();

  // SUBMIT EVENT

  function handleSubmit(e) {
    e.preventDefault();

    fetch('/api/login', {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json', 
        'Accept': 'application/json' 
      },
      body: JSON.stringify({ user, password })
    }).then(res => {
      if (res.ok) {
        res.json().then(user => {
          setCurrentUser(user);
          navigate('/'); 
        });
      } else {
        alert('Invalid username or password');
      }
    });
  }

  // RENDER //

  return (
    <div>

        <form className='user-form' onSubmit={handleSubmit}>

        <h2>Login</h2>

        <input type="text"
        onChange={e => setUser(e.target.value)}
        value={user}
        placeholder='username'
        />

        <input type="password"
        onChange={e => setPassword(e.target.value)}
        value={password}
        placeholder='password'
        />

        <input type="submit"
        value='Login'
        />

        </form>

    </div>
  )

}

export default Login