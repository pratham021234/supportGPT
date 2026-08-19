import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from './client';

const useWorkspaceContext = () => {
  return {
    workspaceId: "00000000-0000-0000-0000-000000000000",
    enabled: true
  };
};

export type ConversationStatus = "OPEN" | "ACTIVE" | "WAITING" | "ESCALATED" | "HANDOFF" | "RESOLVED" | "CLOSED";
export type ConversationChannel = "WEB_CHAT" | "EMAIL" | "WHATSAPP" | "SLACK" | "API";
export type SenderType = "CUSTOMER" | "AI" | "AGENT" | "SYSTEM";
export type MessageType = "TEXT" | "SYSTEM_EVENT" | "ESCALATION" | "CITATION" | "ATTACHMENT";

export interface Customer {
  id: string;
  name: string | null;
  email: string | null;
  phone: string | null;
  first_seen_at: string;
  last_seen_at: string;
}

export interface Conversation {
  id: string;
  workspace_id: string;
  customer_id: string;
  agent_id: string | null;
  assigned_user_id: string | null;
  status: ConversationStatus;
  channel: ConversationChannel;
  is_human_active: boolean;
  started_at: string;
  last_message_at: string;
  resolved_at: string | null;
  customer?: Customer;
}

export interface Message {
  id: string;
  conversation_id: string;
  sender_type: SenderType;
  sender_id: string | null;
  content: string;
  message_type: MessageType;
  metadata_?: any;
  created_at: string;
}

// API Services
export const conversationsService = {
  getConversations: async (status?: ConversationStatus) => {
    const params = new URLSearchParams();
    if (status) params.append("status", status);
    const res = await apiClient.get<Conversation[]>(`/conversations?${params.toString()}`);
    return res.data;
  },

  getConversation: async (id: string) => {
    const res = await apiClient.get<Conversation>(`/conversations/${id}`);
    return res.data;
  },

  getMessages: async (id: string) => {
    const res = await apiClient.get<Message[]>(`/conversations/${id}/messages`);
    return res.data;
  },

  sendMessage: async (id: string, content: string, is_internal: boolean = false, message_type: MessageType = "TEXT") => {
    const res = await apiClient.post<Message>(`/conversations/${id}/message`, {
      content,
      is_internal,
      message_type
    });
    return res.data;
  },

  assignConversation: async (id: string, user_id: string) => {
    const res = await apiClient.post<Conversation>(`/conversations/${id}/assign`, { assigned_user_id: user_id });
    return res.data;
  },

  escalateConversation: async (id: string, reason: string) => {
    const res = await apiClient.post<any>(`/conversations/${id}/escalate`, { reason });
    return res.data;
  },

  resolveConversation: async (id: string) => {
    const res = await apiClient.post<Conversation>(`/conversations/${id}/resolve`);
    return res.data;
  },

  closeConversation: async (id: string) => {
    const res = await apiClient.post<Conversation>(`/conversations/${id}/close`);
    return res.data;
  }
};

// React Query Hooks
export const useConversations = (status?: ConversationStatus) => {
  const { workspaceId } = useWorkspaceContext();
  return useQuery({
    queryKey: ['conversations', workspaceId, status],
    queryFn: () => conversationsService.getConversations(status),
    refetchInterval: 10000, // Poll every 10s for the inbox list
  });
};

export const useConversation = (id: string | null) => {
  const { workspaceId } = useWorkspaceContext();
  return useQuery({
    queryKey: ['conversation', workspaceId, id],
    queryFn: () => id ? conversationsService.getConversation(id) : null,
    enabled: !!id,
  });
};

export const useMessages = (id: string | null) => {
  const { workspaceId } = useWorkspaceContext();
  return useQuery({
    queryKey: ['messages', workspaceId, id],
    queryFn: () => id ? conversationsService.getMessages(id) : null,
    enabled: !!id,
  });
};

export const useSendMessage = (id: string) => {
  const queryClient = useQueryClient();
  const { workspaceId } = useWorkspaceContext();
  
  return useMutation({
    mutationFn: (params: { content: string, is_internal?: boolean, message_type?: MessageType }) => 
      conversationsService.sendMessage(id, params.content, params.is_internal, params.message_type),
    onSuccess: () => {
      // Optimistically update or just invalidate
      queryClient.invalidateQueries({ queryKey: ['messages', workspaceId, id] });
      queryClient.invalidateQueries({ queryKey: ['conversations', workspaceId] });
    }
  });
};

export const useAssignConversation = (id: string) => {
  const queryClient = useQueryClient();
  const { workspaceId } = useWorkspaceContext();
  return useMutation({
    mutationFn: (userId: string) => conversationsService.assignConversation(id, userId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['conversation', workspaceId, id] });
      queryClient.invalidateQueries({ queryKey: ['conversations', workspaceId] });
    }
  });
};

export const useEscalateConversation = (id: string) => {
  const queryClient = useQueryClient();
  const { workspaceId } = useWorkspaceContext();
  return useMutation({
    mutationFn: (reason: string) => conversationsService.escalateConversation(id, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['conversation', workspaceId, id] });
      queryClient.invalidateQueries({ queryKey: ['conversations', workspaceId] });
    }
  });
};

export const useResolveConversation = (id: string) => {
  const queryClient = useQueryClient();
  const { workspaceId } = useWorkspaceContext();
  return useMutation({
    mutationFn: () => conversationsService.resolveConversation(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['conversation', workspaceId, id] });
      queryClient.invalidateQueries({ queryKey: ['conversations', workspaceId] });
    }
  });
};
