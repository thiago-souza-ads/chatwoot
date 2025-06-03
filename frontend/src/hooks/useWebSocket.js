import { useState, useEffect, useRef, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';

const useWebSocket = (url) => {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState(null);
  const [error, setError] = useState(null);
  const websocketRef = useRef(null);
  const { isAuthenticated } = useAuth(); // Use auth status

  const connect = useCallback(() => {
    if (!url || !isAuthenticated) {
        console.log("WebSocket URL not provided or user not authenticated, not connecting.");
        setIsConnected(false);
        return; // Don't connect if URL is missing or user not logged in
    }

    if (websocketRef.current && websocketRef.current.readyState === WebSocket.OPEN) {
        console.log("WebSocket already connected.");
        setIsConnected(true);
        return; // Already connected
    }

    console.log(`Attempting to connect WebSocket to: ${url}`);
    websocketRef.current = new WebSocket(url);

    websocketRef.current.onopen = () => {
      console.log('WebSocket connected');
      setIsConnected(true);
      setError(null);
    };

    websocketRef.current.onmessage = (event) => {
      // console.log('WebSocket message received:', event.data);
      try {
          const message = JSON.parse(event.data);
          setLastMessage(message);
      } catch (e) {
          console.error("Failed to parse WebSocket message:", e);
          setLastMessage(event.data); // Store raw data if JSON parsing fails
      }
    };

    websocketRef.current.onerror = (event) => {
      console.error('WebSocket error:', event);
      setError('WebSocket connection error.');
      setIsConnected(false);
    };

    websocketRef.current.onclose = (event) => {
      console.log('WebSocket disconnected:', event.reason, event.code);
      setIsConnected(false);
      // Optional: Implement automatic reconnection logic here if needed
      // if (event.code !== 1000) { // Don't reconnect on normal close
      //   setTimeout(connect, 5000); // Reconnect after 5 seconds
      // }
    };

  }, [url, isAuthenticated]);

  const disconnect = useCallback(() => {
    if (websocketRef.current) {
      console.log("Disconnecting WebSocket...");
      websocketRef.current.close(1000, "User disconnected"); // Normal closure
      websocketRef.current = null;
      setIsConnected(false);
      setLastMessage(null);
    }
  }, []);

  // Connect on mount if URL is provided and user is authenticated
  useEffect(() => {
    connect();
    // Cleanup on unmount
    return () => {
      disconnect();
    };
  }, [connect, disconnect]); // Dependencies ensure connect/disconnect are stable

  const sendMessage = useCallback((message) => {
    if (websocketRef.current && websocketRef.current.readyState === WebSocket.OPEN) {
      try {
          const messageString = JSON.stringify(message);
          websocketRef.current.send(messageString);
      } catch (e) {
          console.error("Failed to stringify message for WebSocket:", e);
      }
    } else {
      console.error('WebSocket not connected. Cannot send message.');
      // Optional: Queue message or throw error
    }
  }, []);

  return { isConnected, lastMessage, error, sendMessage, connect, disconnect };
};

export default useWebSocket;

