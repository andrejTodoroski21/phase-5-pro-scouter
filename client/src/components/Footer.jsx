import { Link } from 'react-router-dom'

function Footer() {
  return (
    <footer className="footer-container">
      <div className="footer-links">
        <h5>Contact</h5>
        <a href="https://github.com/andrejTodoroski21">Github</a>
        <a href="https://www.linkedin.com/in/andrej-todoroski-18a2bb214/">LinkedIn</a>
      </div>
      <div className="footer-links">
        <h5>Support</h5>
        <span>Phone: 999-999-9999</span>
        <span>Email: JohnDoe@yahoo.com</span>
      </div>
      <div className="footer-links">
        <h5>What we&apos;re about</h5>
        <Link to="/about">About</Link>
      </div>
    </footer>
  )
}

export default Footer
