import React, { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';

const Message = () => {
  const { currentUser } = useOutletContext();
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [recruiterId, setRecruiterId] = useState(null);

  useEffect(() => {
    if (currentUser && recruiterId) {
      fetch(`/api/messages/${currentUser.id}/${recruiterId}`)
        .then(response => response.json())
        .then(data => setMessages(data))
        .catch(error => console.error('Error fetching messages:', error));
    }
  }, [currentUser, recruiterId]);

  const handleSendMessage = () => {
    if (newMessage.trim() !== '') {
      fetch('/api/messages', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content: newMessage,
          user_message: currentUser.id,
          recruiter_message: recruiterId,
        }),
      })
        .then(response => response.json())
        .then(message => {
          setMessages([...messages, message]);
          setNewMessage('');
        })
        .catch(error => console.error('Error sending message:', error));
    }
  };

  return (
    <div className="message-container">
      <h2>Messages with Recruiter</h2>
      <input
        type="number"
        placeholder="Enter Recruiter ID"
        value={recruiterId}
        onChange={(e) => setRecruiterId(e.target.value)}
      />
      <div className="messages">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.user_message === currentUser.id ? 'sent' : 'received'}`}>
            <p>{message.content}</p>
          </div>
        ))}
      </div>
      <div className="message-input">
        <input
          type="text"
          placeholder="Type a message..."
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
        />
        <button onClick={handleSendMessage}>Send</button>
      </div>
    </div>
  );
};

export default Message;
