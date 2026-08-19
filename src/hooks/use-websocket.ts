import { useEffect, useRef, useState, useCallback } from 'react';
import { useQueryClient } from '@tanstack/react-query';

const useWorkspaceContext = () => {
  return {
    workspaceId: "00000000-0000-0000-0000-000000000000",
    enabled: true
  };
};
import { Message } from '@/lib/api/conversations';

interface WebSocketMessage {
  type: string;
  content?: string;
  sender?: string;
  is_internal?: boolean;
  metadata_?: any;
  message_type?: string;
}

export function useConversationWebSocket(conversationId: string | null) {
  const [isConnected, setIsConnected] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [streamingMessage, setStreamingMessage] = useState("");
  const wsRef = useRef<WebSocket | null>(null);
  const queryClient = useQueryClient();
  const { workspaceId } = useWorkspaceContext();

  const connect = useCallback(() => {
    if (!conversationId) return;

    // Use ws:// for localhost and wss:// for https
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    // Get host from apiClient or assume same host if proxied, 
    // for this setup we'll assume the backend is at NEXT_PUBLIC_API_URL or localhost:8000
    const baseUrl = process.env.NEXT_PUBLIC_API_URL?.replace('http://', 'ws://').replace('https://', 'wss://') || 'ws://localhost:8000/api/v1';
    
    const wsUrl = `${baseUrl}/conversations/${conversationId}/ws`;
    
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      setIsConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as WebSocketMessage;
        
        if (data.type === 'agent_typing') {
          setIsTyping(data.status as any as boolean);
        } else if (data.type === 'token') {
          setStreamingMessage(prev => prev + (data.content || ""));
        } else if (data.type === 'message_complete' || data.type === 'message') {
          setStreamingMessage("");
          setIsTyping(false);
          queryClient.invalidateQueries({ queryKey: ['messages', workspaceId, conversationId] });
        } else if (data.type === 'system_event') {
          queryClient.invalidateQueries({ queryKey: ['conversation', workspaceId, conversationId] });
          queryClient.invalidateQueries({ queryKey: ['conversations', workspaceId] });
          queryClient.invalidateQueries({ queryKey: ['messages', workspaceId, conversationId] });
        } else {
          queryClient.invalidateQueries({ queryKey: ['messages', workspaceId, conversationId] });
        }
      } catch (err) {
        queryClient.invalidateQueries({ queryKey: ['messages', workspaceId, conversationId] });
      }
    };

    ws.onclose = () => {
      setIsConnected(false);
      // Optional: implement reconnect logic with exponential backoff
      setTimeout(connect, 3000); 
    };

    ws.onerror = (error) => {
      console.error('WebSocket Error:', error);
      ws.close();
    };

    wsRef.current = ws;
  }, [conversationId, workspaceId, queryClient]);

  useEffect(() => {
    connect();

    return () => {
      if (wsRef.current) {
        // Prevent reconnect loop on unmount
        wsRef.current.onclose = null; 
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [connect]);

  // Expose a send function if we ever want to send over WS instead of REST
  const sendMessage = useCallback((text: string) => {
    if (wsRef.current && isConnected) {
      wsRef.current.send(text);
    }
  }, [isConnected]);

  return { isConnected, isTyping, streamingMessage, sendMessage };
}
