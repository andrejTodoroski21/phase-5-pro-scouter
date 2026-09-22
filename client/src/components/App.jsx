import { Outlet } from 'react-router-dom'
import Navbar from '../Navbar.jsx'
import Footer from './Footer.jsx'
import { AuthProvider } from '../context/AuthContext.jsx'

const App = () => (
  <AuthProvider>
    <div className="app-shell">
      <Navbar />
      <main className="app-main">
        <Outlet />
      </main>
      <Footer />
    </div>
  </AuthProvider>
)

export default App
