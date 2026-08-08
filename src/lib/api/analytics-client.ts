import { apiClient } from './api-client';

export interface DashboardStats {
  total_conversations: number;
  conversations_trend: string;
  ai_resolution_rate: number;
  resolution_trend: string;
  knowledge_sources: number;
  knowledge_trend: string;
  active_tickets: number;
  tickets_trend: string;
}

export interface ConversationMetric {
  name: string; // e.g., "Mon", "Tue"
  total: number;
}

export interface ResolutionMetric {
  name: string; // e.g., "Week 1"
  ai: number;
  human: number;
}

export interface RecentConversation {
  id: string;
  name: string;
  email: string;
  query: string;
  status: string;
  time: string;
}

export interface SystemStatus {
  vector_db_uptime: string;
  llm_latency: string;
  document_queue: number;
}

export interface TopicMetric {
  topic: string;
  count: number;
}

export interface DocumentReference {
  name: string;
  uses: number;
}

export const analyticsClient = {
  getStats: () => 
    apiClient<DashboardStats>('/analytics/stats'),
    
  getVolumeMetrics: () =>
    apiClient<ConversationMetric[]>('/analytics/volume'),
    
  getResolutionMetrics: () =>
    apiClient<ResolutionMetric[]>('/analytics/resolution'),

  getRecentConversations: () =>
    apiClient<RecentConversation[]>('/analytics/recent-conversations'),

  getSystemStatus: () =>
    apiClient<SystemStatus>('/analytics/system-status'),

  getTopQuestions: () =>
    apiClient<TopicMetric[]>('/analytics/top-questions'),

  getKnowledgeGaps: () =>
    apiClient<TopicMetric[]>('/analytics/knowledge-gaps'),

  getMostReferencedDocuments: () =>
    apiClient<DocumentReference[]>('/analytics/document-references'),
};
