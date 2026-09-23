import React, { Suspense, lazy } from 'react'
import ReactDOM from 'react-dom/client'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import App from './components/App.jsx'
import Home from './components/Home.jsx'
import './index.css'

// Everything past the landing page is code-split, so the first paint no longer
// ships the messaging page, both signup flows and the video grid to a visitor
// who only wanted the home page.
const Video = lazy(() => import('./components/Video.jsx'))
const Profile = lazy(() => import('./components/Profile.jsx'))
const About = lazy(() => import('./components/About.jsx'))
const Login = lazy(() => import('./components/UserPanel/Login.jsx'))
const Signup = lazy(() => import('./components/UserPanel/Signup.jsx'))
const AddVideo = lazy(() => import('./components/AddVideo.jsx'))
const MessagingPage = lazy(() => import('./components/MessagingPage.jsx'))
const Rsignup = lazy(() => import('./components/RecruiterPanel/Rsignup.jsx'))
const Rlogin = lazy(() => import('./components/RecruiterPanel/Rlogin.jsx'))
const RecruiterHome = lazy(() => import('./components/RecruiterHome.jsx'))

const withSuspense = (element) => (
  <Suspense fallback={<p className="muted page">Loading…</p>}>{element}</Suspense>
)

const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      { index: true, element: <Home /> },
      { path: 'videos', element: withSuspense(<Video />) },
      { path: 'profile', element: withSuspense(<Profile />) },
      { path: 'about', element: withSuspense(<About />) },
      { path: 'login', element: withSuspense(<Login />) },
      { path: 'signup', element: withSuspense(<Signup />) },
      { path: 'add-video', element: withSuspense(<AddVideo />) },
      { path: 'messages', element: withSuspense(<MessagingPage />) },
      { path: 'recruiter-signup', element: withSuspense(<Rsignup />) },
      { path: 'recruiter-login', element: withSuspense(<Rlogin />) },
      { path: 'recruiter-home', element: withSuspense(<RecruiterHome />) },
    ],
  },
])

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>,
)
