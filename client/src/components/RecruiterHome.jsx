import React from 'react';
import { useOutletContext} from 'react-router-dom';

function RecruiterHome() {
  const { currentRecruiter, setCurrentRecruiter } = useOutletContext();

  function handleRecruiterLogout() {
    setCurrentRecruiter(null);
    fetch('/api/recruiters', { method: 'DELETE' })
  }

  return (
    <div>
      <div></div>
      <h3>Welcome, {currentRecruiter ? currentRecruiter.recruiter_username : 'Guest'}!</h3>
      <button onClick={handleRecruiterLogout}>Logout</button>
    </div>
  );
}

export default RecruiterHome;