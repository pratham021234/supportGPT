import { apiClient } from './api-client';

export interface Conversation {
  id: string;
  name: string;
  query: string;
  status: string;
  ai: boolean;
  time: string;
}

export const conversationClient = {
  getConversations: () => 
    apiClient<Conversation[]>('/conversations'),
};
