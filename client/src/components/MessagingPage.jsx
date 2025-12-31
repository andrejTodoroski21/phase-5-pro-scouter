import React, {useState, useEffect} from "react";

function MessagingPage({currentUser}){
    const  [conversations, setConversations] = useState([]);
    const  [activeChat, setActiveChat] = useState(null);
    const  [messages, setMessages] = useState([]);
    const  [newMessage, setNewMessage] = useState("");

    useEffect(()=>{
        fetch('api/conversations')
        .then(res=> res.json())
        .then(data => setConversations(data))
    },[]);

    useEffect(()=>{
        if(activeChat && activeChat.id){
            fetch('api/messages/${activeChat.id}')
            .then(res => res.json())
            .then(data=> setMessages(data))
        }
    },[activeChat]);

    const handleSend = () =>{
        fetch('api/messages',{
            method: 'Post',
            headers: {'Content-Type' : 'application/json'},
            body: Json.stringify({
                recipient_id: activeChat.id,
                content: newMessage
            })
        })
        .then(res=> res.json())
        .then(msg=> {
            setMessages([...messages, msg])
            setNewMessage("")
        })
        
    }
    return (
        <div className="flex h-screen bg-black text-white">
          {/* LEFT PANEL: Conversation List */}
          <div className="w-1/3 border-r border-gray-800 overflow-y-auto">
            <h2 className="p-4 text-xl font-bold border-b border-gray-800">Messages</h2>
            {conversations.map(chat => (
              <div 
                key={chat.id} 
                onClick={() => setActiveChat(chat)}
                className={`flex items-center p-4 cursor-pointer hover:bg-gray-900 ${activeChat?.id === chat.id ? 'bg-gray-800' : ''}`}
              >
                <img src={chat.profile_pic || '/default-avatar.png'} className="w-12 h-12 rounded-full mr-3" alt="avatar" />
                <div className="flex-1 min-w-0">
                  <p className="font-semibold truncate">{chat.username}</p>
                  <p className="text-sm text-gray-400 truncate">{chat.last_message}</p>
                </div>
                <span className="text-xs text-gray-500">{chat.timestamp}</span>
              </div>
            ))}
          </div>
    
          {/* RIGHT PANEL: Active Conversation */}
          <div className="w-2/3 flex flex-col">
            {activeChat ? (
              <>
                <div className="p-4 border-b border-gray-800 flex items-center">
                  <img src={activeChat.profile_pic} className="w-8 h-8 rounded-full mr-2" />
                  <span className="font-bold">{activeChat.username}</span>
                </div>
                
                <div className="flex-1 overflow-y-auto p-4 space-y-4">
                  {messages.map(msg => (
                    <div key={msg.id} className={`flex ${msg.sender_id === currentUser.id ? 'justify-end' : 'justify-start'}`}>
                      <div className={`max-w-xs p-3 rounded-2xl ${msg.sender_id === currentUser.id ? 'bg-blue-600 rounded-br-none' : 'bg-gray-800 rounded-bl-none'}`}>
                        {msg.content}
                      </div>
                    </div>
                  ))}
                </div>
    
                <div className="p-4 border-t border-gray-800 flex items-center">
                  <input 
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    className="flex-1 bg-gray-900 border border-gray-700 rounded-full px-4 py-2 focus:outline-none focus:border-blue-500"
                    placeholder="Message..."
                  />
                  <button onClick={handleSend} className="ml-3 text-blue-500 font-bold hover:text-white transition">Send</button>
                </div>
              </>
            ) : (
              <div className="flex-1 flex flex-col items-center justify-center text-gray-500">
                 <p className="text-lg">Select a conversation to start messaging</p>
              </div>
            )}
          </div>
        </div>
      );
}

export default MessagingPage;

