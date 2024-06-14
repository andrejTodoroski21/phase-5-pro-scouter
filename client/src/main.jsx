import React from 'react'
import ReactDOM from 'react-dom/client'
import Home from './components/Home.jsx'
import Video from './components/Video.jsx'
// import Profile from './components/Profile.jsx'
// import About from './components/About.jsx'
import Login from './components/UserPanel/Login.jsx'
import Signup from './components/UserPanel/Signup.jsx'
import AddVideo from './components/AddVideo.jsx'
import Message from './components/Message.jsx'
import App from './components/App.jsx'
import './index.css'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'



const routes = [
  {
    path: "/",
    element: <App />,
    children: [
      {
        index: true,
        element: <Home />
      },
      {
        path: "videos",
        element: <Video />
      },
      // {
      //   path: "profile",
      //   element: <Profile />
      // },
      // {
      //   path: "about",
      //   element: <About />
      // },
      {
        path: "login",
        element: <Login />
      },
      {
        path: 'signup',
        element: <Signup />
      },
      {
        path: "add-video",
        element: <AddVideo />
      },
      {
        path: "messages",
        element: <Message />
      }
    ]
  }
]


const router = createBrowserRouter(routes)

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <RouterProvider router={router}/>
  </React.StrictMode>,
)
