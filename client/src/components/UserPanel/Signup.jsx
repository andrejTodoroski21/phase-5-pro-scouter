import { useState } from 'react'
import { useOutletContext } from 'react-router-dom'
import { useNavigate } from 'react-router-dom';


function Signup() {
  const { setCurrentUser } = useOutletContext()
  // STATE //

  const [username, setUsername] = useState('')
  const [_hashed_password, setPassword] = useState('')
  const [first_name, setFirstName] = useState('')
  const [last_name, setLastName] = useState('')
  const navigate = useNavigate();


  // EVENTS //

  function handleSubmit(e) {
    e.preventDefault()

    fetch('/api/users', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: JSON.stringify({ first_name, last_name, username, _hashed_password})
    })
    .then(response => {
      if (response.ok) {
        response.json()
        .then( newUser => {
          setCurrentUser(newUser) 
          navigate('/');
        });
      } else {
        alert("Signup unsuccessful")
      }
    })
  }

  // RENDER //

  return (
    <div>


    <form className='user-form' onSubmit={handleSubmit}>

      <h2>Signup</h2>

      <input type="text"
      onChange={e => setUsername(e.target.value)}
      value={username}
      placeholder='username'
      />

      <input type="password"
      onChange={e => setPassword(e.target.value)}
      value={_hashed_password}
      placeholder='password'
      />

      <input type="text"
      onChange={e => setFirstName(e.target.value)}
      value={first_name}
      placeholder='first name'
      />

      <input type="text"
      onChange={e => setLastName(e.target.value)}
      value={last_name}
      placeholder='last name'
      />

      <input type="submit"
      value='Signup'
      />

    </form>

      </div>
  )

}

export default Signup