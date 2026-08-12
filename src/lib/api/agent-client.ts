import { apiClient } from './client';

export interface Agent {
  id: string;
  name: string;
  description: string;
  model: string;
  sources: number;
  status: string;
  conversations: number;
}

export const agentClient = {
  getAgents: () => 
    apiClient<Agent[]>('/agents'),
};
