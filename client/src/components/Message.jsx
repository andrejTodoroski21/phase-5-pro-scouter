import React, { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';

const Message = () => {
  const { currentUser } = useOutletContext();
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [recruiterId, setRecruiterId] = useState('');
  const [interactionId, setInteractionId] = useState(null);

  useEffect(() => {
    if (currentUser?.id && recruiterId) {
      fetch(`/api/messages/${currentUser.id}/${recruiterId}`)
        .then(response => response.json())
        .then(data => {
          setMessages(data.messages); // assuming data contains messages and interactionId
          setInteractionId(data.interactionId); // set interactionId from the fetched data
        })
        .catch(error => console.error('Error fetching messages:', error));
    }
  }, [currentUser, recruiterId]);

  const handleSendMessage = () => {
    if (newMessage.trim()) {
      const payload = {
        content: newMessage,
        user_message: currentUser.id,
        recruiter_message: recruiterId,
        interaction_id: interactionId,
      };
      console.log('Sending message payload:', payload);
  
      fetch('/api/messages', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
        .then(response => {
          if (!response.ok) {
            return response.json().then(error => {
              console.error('Error response from server:', error);
              throw new Error('Failed to send message');
            });
          }
          return response.json();
        })
        .then(message => {
          setMessages(prevMessages => [...prevMessages, message]);
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
        onChange={e => setRecruiterId(e.target.value)}
      />
      <div className="messages">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`message ${message.user_message === currentUser.id ? 'sent' : 'received'}`}
          >
            <p>{message.content}</p>
          </div>
        ))}
      </div>
      <div className="message-input">
        <input
          type="text"
          placeholder="Type a message..."
          value={newMessage}
          onChange={e => setNewMessage(e.target.value)}
        />
        <button onClick={handleSendMessage}>Send</button>
      </div>
    </div>
  );
};

export default Message;
