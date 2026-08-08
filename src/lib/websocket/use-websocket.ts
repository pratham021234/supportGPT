import { useEffect, useState, useCallback, useRef } from 'react';
import { useAuthStore } from '@/store/authStore';

export const WS_BASE_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws/v1';

type WebSocketMessage = {
  type: string;
  payload: any;
};

export function useWebSocket(path: string = '/notifications') {
  const [messages, setMessages] = useState<WebSocketMessage[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  
  // Use a ref to access the latest token without adding it to the dependency array of useEffect
  const token = useAuthStore((state) => state.accessToken);
  const tokenRef = useRef(token);
  
  useEffect(() => {
    tokenRef.current = token;
  }, [token]);

  const connect = useCallback(() => {
    if (!tokenRef.current) return;
    
    // Some backend architectures accept token in query string for WS
    const url = new URL(`${WS_BASE_URL}${path}`);
    url.searchParams.append('token', tokenRef.current);
    
    const ws = new WebSocket(url.toString());
    
    ws.onopen = () => {
      console.log(`WebSocket connected to ${path}`);
      setIsConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setMessages((prev) => [...prev, data]);
      } catch (e) {
        console.error("Failed to parse websocket message", e);
      }
    };

    ws.onclose = () => {
      console.log(`WebSocket disconnected from ${path}`);
      setIsConnected(false);
      // Auto-reconnect after 3s
      setTimeout(() => connect(), 3000);
    };

    ws.onerror = (error) => {
      console.error(`WebSocket error on ${path}`, error);
      ws.close();
    };

    wsRef.current = ws;

    return () => {
      ws.close();
    };
  }, [path]);

  useEffect(() => {
    const cleanup = connect();
    return () => {
      if (cleanup) cleanup();
    };
  }, [connect]);

  const sendMessage = useCallback((type: string, payload: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type, payload }));
    }
  }, []);

  return { isConnected, messages, sendMessage };
}
