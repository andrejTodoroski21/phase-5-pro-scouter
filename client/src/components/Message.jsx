import React, { useState, useEffect } from 'react';
import io from 'socket.io-client';
// import 'client/src/index.css';

const socket = io('/api');

const Chat = () => {
    const [messages, setMessages] = useState([]);
    const [message, setMessage] = useState('');

    useEffect(() => {
        socket.on('message', (msg) => {
            setMessages(prevMessages => [...prevMessages, msg]);
        });

        return () => {
            socket.off('message');
        };
    }, []);

    const sendMessage = () => {
        const msg = { user_id: 1, recruiter_id: 2, content: message };  // Replace with actual IDs
        socket.emit('message', msg);
        setMessage('');
    };

    return (
        <div className="chat-container">
            <div className="messages-container">
                {messages.map((msg, index) => (
                    <div key={index} className="message">
                        <div className="message-content">
                            {msg.content}
                        </div>
                    </div>
                ))}
            </div>
            <div className="input-container">
                <input 
                    type="text" 
                    className="message-input" 
                    placeholder="Type your message..." 
                    value={message} 
                    onChange={(e) => setMessage(e.target.value)} 
                />
                <button 
                    className="send-button" 
                    onClick={sendMessage}
                >
                    Send
                </button>
            </div>
        </div>
    );
};

export default Chat;
