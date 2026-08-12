import { useQuery, useMutation } from '@tanstack/react-query';
import { apiClient } from './client';

const useWorkspaceContext = () => {
  return {
    workspaceId: "00000000-0000-0000-0000-000000000000",
    enabled: true
  };
};

export type TimeRange = "today" | "7d" | "30d" | "90d";

export interface AnalyticsOverview {
  total_conversations: number;
  ai_resolution_rate: number; // percentage
  total_escalations: number;
  knowledge_coverage: number; // percentage
  customer_satisfaction?: number; // out of 5
  avg_response_time?: string;
  agent_performance_score?: number;
}

export interface TrendDataPoint {
  date: string;
  value: number;
  secondary_value?: number;
}

export interface VolumeTrends {
  trends: TrendDataPoint[];
}

export interface AiPerformance {
  avg_confidence: number;
  answer_accuracy: number;
  citation_usage: number;
  hallucination_risk: number;
  latency_ms: number;
}

export interface CSATData {
  csat_score: number;
  helpful_votes: number;
  unhelpful_votes: number;
  sentiment_trends: TrendDataPoint[];
}

export interface AgentSummary {
  agents: {
    id: string;
    name: string;
    resolution_rate: number;
    response_time_mins: number;
    workload: number;
    escalations: number;
    csat: number;
  }[];
}

export interface KnowledgeGaps {
  gaps: {
    query: string;
    escalation_count: number;
    confidence_average: number;
  }[];
}

export interface TopQuestion {
  query: string;
  frequency: number;
  confidence: number;
  resolution_rate: number;
}

export interface ExecutiveInsight {
  title: string;
  description: string;
  action: string;
  impact: "HIGH" | "MEDIUM" | "LOW";
}

export const analyticsService = {
  getOverview: async (timeRange: TimeRange) => {
    const res = await apiClient.get<AnalyticsOverview>(`/analytics/dashboard?time_range=${timeRange}`);
    return res.data;
  },

  getVolumeTrends: async (timeRange: TimeRange) => {
    const res = await apiClient.get<VolumeTrends>(`/analytics/volume?time_range=${timeRange}`);
    return res.data;
  },

  getResolutionTrends: async (timeRange: TimeRange) => {
    const res = await apiClient.get<VolumeTrends>(`/analytics/resolution?time_range=${timeRange}`);
    return res.data;
  },

  getAgentSummary: async () => {
    const res = await apiClient.get<AgentSummary>(`/analytics/agents/summary`);
    return res.data;
  },

  getKnowledgeGaps: async () => {
    const res = await apiClient.get<KnowledgeGaps>(`/analytics/knowledge-gaps`);
    return res.data;
  },

  getTopQuestions: async (timeRange: TimeRange) => {
    const res = await apiClient.get<{questions: TopQuestion[]}>(`/analytics/top-questions?time_range=${timeRange}`);
    return res.data;
  },

  getInsights: async () => {
    const res = await apiClient.get<ExecutiveInsight[]>(`/analytics/insights`);
    return res.data;
  },

  exportReport: async (reportType: string, format: string = "CSV") => {
    const res = await apiClient.post(`/analytics/reports/export`, { report_type: reportType, format }, { responseType: 'blob' });
    return res.data;
  },

  getAiPerformance: async (timeRange: TimeRange) => {
    const res = await apiClient.get<AiPerformance>(`/analytics/ai-performance?time_range=${timeRange}`);
    return res.data;
  },

  getCSAT: async (timeRange: TimeRange) => {
    const res = await apiClient.get<CSATData>(`/analytics/csat?time_range=${timeRange}`);
    return res.data;
  },

  getTicketAnalytics: async (timeRange: TimeRange) => {
    const res = await apiClient.get<any>(`/analytics/tickets?time_range=${timeRange}`);
    return res.data;
  }
};

// React Query Hooks
export const useAnalyticsOverview = (timeRange: TimeRange) => {
  const { workspaceId } = useWorkspaceContext();
  return useQuery({
    queryKey: ['analytics-overview', workspaceId, timeRange],
    queryFn: () => analyticsService.getOverview(timeRange),
  });
};

export const useVolumeTrends = (timeRange: TimeRange) => {
  const { workspaceId } = useWorkspaceContext();
  return useQuery({
    queryKey: ['analytics-volume', workspaceId, timeRange],
    queryFn: () => analyticsService.getVolumeTrends(timeRange),
  });
};

export const useResolutionTrends = (timeRange: TimeRange) => {
  const { workspaceId } = useWorkspaceContext();
  return useQuery({
    queryKey: ['analytics-resolution', workspaceId, timeRange],
    queryFn: () => analyticsService.getResolutionTrends(timeRange),
  });
};

export const useAgentSummary = () => {
  const { workspaceId } = useWorkspaceContext();
  return useQuery({
    queryKey: ['analytics-agents', workspaceId],
    queryFn: () => analyticsService.getAgentSummary(),
  });
};

export const useKnowledgeGaps = () => {
  const { workspaceId } = useWorkspaceContext();
  return useQuery({
    queryKey: ['analytics-knowledge-gaps', workspaceId],
    queryFn: () => analyticsService.getKnowledgeGaps(),
  });
};

export const useTopQuestions = (timeRange: TimeRange) => {
  const { workspaceId } = useWorkspaceContext();
  return useQuery({
    queryKey: ['analytics-top-questions', workspaceId, timeRange],
    queryFn: () => analyticsService.getTopQuestions(timeRange),
  });
};

export const useExecutiveInsights = () => {
  const { workspaceId } = useWorkspaceContext();
  return useQuery({
    queryKey: ['analytics-insights', workspaceId],
    queryFn: () => analyticsService.getInsights(),
  });
};

export const useAiPerformance = (timeRange: TimeRange) => {
  const { workspaceId } = useWorkspaceContext();
  return useQuery({
    queryKey: ['analytics-ai-performance', workspaceId, timeRange],
    queryFn: () => analyticsService.getAiPerformance(timeRange),
  });
};

export const useCSAT = (timeRange: TimeRange) => {
  const { workspaceId } = useWorkspaceContext();
  return useQuery({
    queryKey: ['analytics-csat', workspaceId, timeRange],
    queryFn: () => analyticsService.getCSAT(timeRange),
  });
};

export const useTicketAnalytics = (timeRange: TimeRange) => {
  const { workspaceId } = useWorkspaceContext();
  return useQuery({
    queryKey: ['analytics-ticket-metrics', workspaceId, timeRange],
    queryFn: () => analyticsService.getTicketAnalytics(timeRange),
  });
};
