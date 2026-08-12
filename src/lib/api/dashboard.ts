import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "./client";
import { useAuthStore } from "@/store/authStore";

export interface DashboardStats {
  total_conversations: number;
  conversations_trend: string;
  total_tickets: number;
  tickets_trend: string;
  ai_resolution_rate: number;
  resolution_trend: string;
  active_tickets: number;
  knowledge_sources: number;
  knowledge_trend: string;
  customer_satisfaction: number;
  knowledge_coverage: number;
}

export interface ChartMetric {
  name: string;
  [key: string]: string | number;
}

export interface RecentConversation {
  id: string;
  name: string;
  query: string;
  status: string;
  time: string;
}

export interface SystemStatus {
  vector_db_uptime: string;
  llm_latency: string;
  document_queue: number;
}

export interface AgentSummary {
  name: string;
  resolution_rate: number;
  confidence: number;
  conversations: number;
  satisfaction: number;
}

export interface TopicMetric {
  topic: string;
  count?: number;
  trend?: string;
  confidence?: number;
  suggested_action?: string;
}

export interface DocumentReference {
  id: string;
  name: string;
  uses: number;
  confidence_impact: string;
}

// Helper to get workspace ID and conditionally fetch
const useWorkspaceContext = () => {
  const workspaceId = useAuthStore(state => state.workspace?.id);
  return { workspaceId, enabled: !!workspaceId };
};

export const dashboardService = {
  getStats: (timeRange: string) => 
    apiClient.get<DashboardStats>('/analytics/dashboard', { params: { time_range: timeRange } }),
    
  getVolumeMetrics: (timeRange: string) => 
    apiClient.get<ChartMetric[]>('/analytics/volume', { params: { time_range: timeRange } }),
    
  getResolutionMetrics: (timeRange: string) => 
    apiClient.get<ChartMetric[]>('/analytics/resolution', { params: { time_range: timeRange } }),
    
  getEscalationMetrics: (timeRange: string) => 
    apiClient.get<ChartMetric[]>('/analytics/escalations', { params: { time_range: timeRange } }),
    
  getSystemStatus: () => 
    apiClient.get<SystemStatus>('/analytics/system-status'),
    
  getRecentConversations: () => 
    apiClient.get<any[]>('/conversations?limit=5'),
    
  getAgentSummary: () => 
    apiClient.get<AgentSummary[]>('/analytics/agents/summary'),
    
  getTopQuestions: (timeRange: string) => 
    apiClient.get<TopicMetric[]>('/analytics/top-questions', { params: { time_range: timeRange } }),
    
  getConfidenceAlerts: () => 
    apiClient.get<TopicMetric[]>('/analytics/confidence-alerts'),
    
  getMostReferencedDocs: () => 
    apiClient.get<DocumentReference[]>('/analytics/knowledge/most-referenced'),
    
  getInsights: () => 
    apiClient.get<any>('/analytics/insights'),
};

// Hooks
export const useDashboardStats = (timeRange: string) => {
  const { workspaceId, enabled } = useWorkspaceContext();
  return useQuery({
    queryKey: ["dashboard-stats", workspaceId, timeRange],
    queryFn: () => dashboardService.getStats(timeRange).then(res => res.data),
    enabled,
    staleTime: 1000 * 60 * 5, // 5 minutes
    refetchInterval: 1000 * 60 * 15, // 15 mins background refresh
  });
};

export const useVolumeTrends = (timeRange: string) => {
  const { workspaceId, enabled } = useWorkspaceContext();
  return useQuery({
    queryKey: ["dashboard-volume", workspaceId, timeRange],
    queryFn: () => dashboardService.getVolumeMetrics(timeRange).then(res => res.data),
    enabled,
    staleTime: 1000 * 60 * 5,
  });
};

export const useResolutionTrends = (timeRange: string) => {
  const { workspaceId, enabled } = useWorkspaceContext();
  return useQuery({
    queryKey: ["dashboard-resolution", workspaceId, timeRange],
    queryFn: () => dashboardService.getResolutionMetrics(timeRange).then(res => res.data),
    enabled,
    staleTime: 1000 * 60 * 5,
  });
};

export const useEscalationTrends = (timeRange: string) => {
  const { workspaceId, enabled } = useWorkspaceContext();
  return useQuery({
    queryKey: ["dashboard-escalations", workspaceId, timeRange],
    queryFn: () => dashboardService.getEscalationMetrics(timeRange).then(res => res.data),
    enabled,
    staleTime: 1000 * 60 * 5,
  });
};

export const useSystemHealth = () => {
  const { workspaceId, enabled } = useWorkspaceContext();
  return useQuery({
    queryKey: ["dashboard-system-health", workspaceId],
    queryFn: () => dashboardService.getSystemStatus().then(res => res.data),
    enabled,
    staleTime: 1000 * 30, // 30 seconds
    refetchInterval: 1000 * 60, // 1 minute background refresh
  });
};

export const useRecentConversations = () => {
  const { workspaceId, enabled } = useWorkspaceContext();
  return useQuery({
    queryKey: ["dashboard-recent-conversations", workspaceId],
    queryFn: async () => {
      // Temporary mock mapping if backend endpoint structure differs
      // A real app would format directly from /conversations
      const res = await dashboardService.getRecentConversations();
      // map backend conversations to frontend expected structure
      return res.data.slice(0, 5).map((c: any) => ({
        id: c.id,
        name: c.customer?.name || "Unknown Customer",
        query: c.messages?.[0]?.content || "No message",
        status: c.status,
        time: "Just now" // mock time for MVP
      })) as RecentConversation[];
    },
    enabled,
    staleTime: 1000 * 30,
    refetchInterval: 1000 * 60,
  });
};

export const useAgentSummary = () => {
  const { workspaceId, enabled } = useWorkspaceContext();
  return useQuery({
    queryKey: ["dashboard-agents", workspaceId],
    queryFn: () => dashboardService.getAgentSummary().then(res => res.data),
    enabled,
    staleTime: 1000 * 60 * 5,
  });
};

export const useTopQuestions = (timeRange: string) => {
  const { workspaceId, enabled } = useWorkspaceContext();
  return useQuery({
    queryKey: ["dashboard-top-questions", workspaceId, timeRange],
    queryFn: () => dashboardService.getTopQuestions(timeRange).then(res => res.data),
    enabled,
    staleTime: 1000 * 60 * 5,
  });
};

export const useConfidenceAlerts = () => {
  const { workspaceId, enabled } = useWorkspaceContext();
  return useQuery({
    queryKey: ["dashboard-confidence-alerts", workspaceId],
    queryFn: () => dashboardService.getConfidenceAlerts().then(res => res.data),
    enabled,
    staleTime: 1000 * 60 * 5,
  });
};

export const useMostReferencedDocs = () => {
  const { workspaceId, enabled } = useWorkspaceContext();
  return useQuery({
    queryKey: ["dashboard-top-docs", workspaceId],
    queryFn: () => dashboardService.getMostReferencedDocs().then(res => res.data),
    enabled,
    staleTime: 1000 * 60 * 5,
  });
};

export const useExecutiveInsights = () => {
  const { workspaceId, enabled } = useWorkspaceContext();
  return useQuery({
    queryKey: ["dashboard-insights", workspaceId],
    queryFn: () => dashboardService.getInsights().then(res => res.data),
    enabled,
    staleTime: 1000 * 60 * 15,
  });
};
