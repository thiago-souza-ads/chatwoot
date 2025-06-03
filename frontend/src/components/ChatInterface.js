import React, { useState, useEffect, useRef } from 'react';
import useWebSocket from '../hooks/useWebSocket';
import { useAuth } from '../contexts/AuthContext';

// Determine WebSocket URL based on API_URL (replace http with ws/wss)
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';
const WS_URL_BASE = API_URL.replace(/^http/, 'ws');

function ChatInterface() {
  const { user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const messagesEndRef = useRef(null); // To auto-scroll

  // Construct WebSocket URL including user and company ID
  const wsUrl = user ? `${WS_URL_BASE}/ws/${user.empresa_id || 0}/${user.id}` : null; // Use 0 or handle superuser case if needed

  const { isConnected, lastMessage, error, sendMessage } = useWebSocket(wsUrl);

  // Add incoming messages to the list
  useEffect(() => {
    if (lastMessage) {
      // Basic filtering: only add chat messages (adjust based on backend structure)
      if (lastMessage.type === 'chat_message') {
        setMessages((prevMessages) => [...prevMessages, lastMessage]);
      } else if (lastMessage.type === 'new_message') { // Handle messages from Evolution webhook
         setMessages((prevMessages) => [
           ...prevMessages,
           {
             sender_id: `External: ${lastMessage.sender}`,
             content: lastMessage.content,
             timestamp: new Date().toISOString(), // Add timestamp
           },
         ]);
      } else {
          console.log("Received non-chat WebSocket message:", lastMessage);
      }
    }
  }, [lastMessage]);

  // Auto-scroll to the bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = (e) => {
    e.preventDefault();
    if (newMessage.trim() && isConnected) {
      const messagePayload = {
        type: 'chat_message', // Define message type for backend processing
        content: newMessage,
      };
      sendMessage(messagePayload);
      setNewMessage('');
    } else if (!isConnected) {
        console.error("Cannot send message, WebSocket not connected.");
        // Optionally show an error to the user
    }
  };

  return (
    <div style={{ border: '1px solid #ccc', padding: '10px', height: '500px', display: 'flex', flexDirection: 'column' }}>
      <h3>Chat Interno / Mensagens</h3>
      <p>Status Conexão: {isConnected ? 'Conectado' : 'Desconectado'}</p>
      {error && <p style={{ color: 'red' }}>Erro WebSocket: {error}</p>}
      <div style={{ flexGrow: 1, overflowY: 'auto', border: '1px solid #eee', marginBottom: '10px', padding: '5px' }}>
        {messages.map((msg, index) => (
          <p key={index}>
            <strong>{msg.sender_id === user?.id ? 'Você' : (msg.sender_id || 'Sistema')}:</strong> {msg.content}
            {/* Add timestamp if available */}
          </p>
        ))}
        <div ref={messagesEndRef} /> {/* Anchor for auto-scrolling */}
      </div>
      <form onSubmit={handleSendMessage} style={{ display: 'flex' }}>
        <input
          type="text"
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          placeholder="Digite sua mensagem..."
          style={{ flexGrow: 1, marginRight: '5px' }}
          disabled={!isConnected}
        />
        <button type="submit" disabled={!isConnected || !newMessage.trim()}>Enviar</button>
      </form>
    </div>
  );
}

export default ChatInterface;

