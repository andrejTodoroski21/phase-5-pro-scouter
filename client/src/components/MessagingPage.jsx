import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../lib/api'
import { useAuth } from '../context/auth-context.js'

function MessagingPage() {
  const { currentUser, loading } = useAuth()
  const [conversations, setConversations] = useState([])
  const [activeChat, setActiveChat] = useState(null)
  const [messages, setMessages] = useState([])
  const [draft, setDraft] = useState('')
  const [error, setError] = useState(null)
  const bottomRef = useRef(null)

  // Hooks stay above the early returns below — the previous version returned
  // before calling useEffect, which breaks the rules of hooks and crashed the
  // page the moment a logged-out visitor opened it.
  useEffect(() => {
    if (!currentUser) return undefined
    const controller = new AbortController()
    api.get('/conversations', { signal: controller.signal })
      .then(setConversations)
      .catch((err) => {
        if (err.name !== 'AbortError') setError('Could not load conversations.')
      })
    return () => controller.abort()
  }, [currentUser])

  useEffect(() => {
    if (!activeChat?.id) return undefined
    const controller = new AbortController()
    api.get(`/messages/${activeChat.id}`, { signal: controller.signal })
      .then(setMessages)
      .catch((err) => {
        if (err.name !== 'AbortError') setError('Could not load this conversation.')
      })
    return () => controller.abort()
  }, [activeChat])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ block: 'end' })
  }, [messages])

  function handleSend(event) {
    event.preventDefault()
    const content = draft.trim()
    if (!content || !activeChat) return
    api.post('/messages', { recipient_id: activeChat.id, content })
      .then((message) => {
        setMessages((previous) => [...previous, message])
        setDraft('')
      })
      .catch((err) => setError(err.message))
  }

  if (loading) return <p className="muted page">Loading…</p>
  if (!currentUser) {
    return (
      <div className="page">
        <p>Please <Link to="/login">log in</Link> to view your messages.</p>
      </div>
    )
  }

  return (
    <div className="messaging">
      <aside className="messaging-list">
        <h2>Messages</h2>
        {conversations.length === 0 && <p className="muted">No conversations yet.</p>}
        {conversations.map((chat) => (
          <button
            type="button"
            key={chat.id}
            onClick={() => setActiveChat(chat)}
            className={`messaging-row${activeChat?.id === chat.id ? ' is-active' : ''}`}
          >
            <span className="messaging-name">{chat.username}</span>
            <span className="messaging-preview">{chat.last_message}</span>
          </button>
        ))}
      </aside>

      <section className="messaging-thread">
        {error && <p className="error">{error}</p>}
        {activeChat ? (
          <>
            <header className="messaging-header">{activeChat.username}</header>
            <div className="messaging-bubbles">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`bubble${message.sender_id === currentUser.id ? ' bubble-mine' : ''}`}
                >
                  {message.content}
                </div>
              ))}
              <div ref={bottomRef} />
            </div>
            <form className="messaging-compose" onSubmit={handleSend}>
              <input
                value={draft}
                onChange={(e) => setDraft(e.target.value)}
                placeholder="Message…"
              />
              <button type="submit">Send</button>
            </form>
          </>
        ) : (
          <p className="muted messaging-empty">Select a conversation to start messaging</p>
        )}
      </section>
    </div>
  )
}

export default MessagingPage
