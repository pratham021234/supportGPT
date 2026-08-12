import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "./client";
import { useAuthStore } from "@/store/authStore";

export interface Agent {
  id: string;
  workspace_id: string;
  name: string;
  description?: string;
  agent_type: string;
  status: string;
  model: string;
  temperature: number;
  sources: number;
  conversations: number;
  created_at: string;
  updated_at: string;
}

export interface AgentAnalytics {
  questions_answered: number;
  resolution_rate: number;
  escalation_rate: number;
  average_confidence: number;
  avg_response_time_ms: number;
  customer_satisfaction: number;
}

export interface AgentActivity {
  id: string;
  action: string;
  details: string;
  created_at: string;
}

export interface AgentTestResponse {
  answer: string;
  sources: any[];
  confidence: number;
  latency_ms: number;
}

const useWorkspaceContext = () => {
  const workspaceId = useAuthStore(state => state.workspace?.id);
  return { workspaceId, enabled: !!workspaceId };
};

export const agentsService = {
  getAgents: () => 
    apiClient.get<Agent[]>('/agents'),
    
  getAgent: (id: string) => 
    apiClient.get<Agent>(`/agents/${id}`),
    
  createAgent: (payload: { name: string; description?: string; agent_type: string }) => 
    apiClient.post<Agent>('/agents', payload),
    
  publishAgent: (id: string) => 
    apiClient.post(`/agents/${id}/publish`),
    
  updatePrompt: (id: string, payload: any) => 
    apiClient.patch(`/agents/${id}/prompt`, payload),
    
  updateModelConfig: (id: string, payload: any) => 
    apiClient.patch(`/agents/${id}/model`, payload),
    
  updateEscalationRules: (id: string, payload: any) => 
    apiClient.patch(`/agents/${id}/escalation`, payload),
    
  assignKnowledge: (id: string, payload: any) => 
    apiClient.post(`/agents/${id}/knowledge`, payload),
    
  testAgent: (id: string, query: string) => 
    apiClient.post<AgentTestResponse>(`/agents/${id}/test`, { query }),
    
  cloneAgent: (id: string) => 
    apiClient.post<Agent>(`/agents/${id}/clone`),
    
  archiveAgent: (id: string) => 
    apiClient.post(`/agents/${id}/archive`),
    
  deleteAgent: (id: string) => 
    apiClient.delete(`/agents/${id}`),
    
  getAnalytics: (id: string) => 
    apiClient.get<AgentAnalytics>(`/agents/${id}/analytics`),
    
  getActivity: (id: string) => 
    apiClient.get<AgentActivity[]>(`/agents/${id}/activity`),
    
  getModels: () => 
    apiClient.get<any[]>('/models')
};

// --- Hooks ---

export const useAgents = () => {
  const { workspaceId, enabled } = useWorkspaceContext();
  return useQuery({
    queryKey: ["agents", workspaceId],
    queryFn: () => agentsService.getAgents().then(res => res.data),
    enabled,
  });
};

export const useAgent = (id: string) => {
  const { workspaceId, enabled } = useWorkspaceContext();
  return useQuery({
    queryKey: ["agent", workspaceId, id],
    queryFn: () => agentsService.getAgent(id).then(res => res.data),
    enabled: enabled && !!id,
  });
};

export const useAgentAnalytics = (id: string) => {
  const { workspaceId, enabled } = useWorkspaceContext();
  return useQuery({
    queryKey: ["agent-analytics", workspaceId, id],
    queryFn: () => agentsService.getAnalytics(id).then(res => res.data),
    enabled: enabled && !!id,
  });
};

export const useAgentActivity = (id: string) => {
  const { workspaceId, enabled } = useWorkspaceContext();
  return useQuery({
    queryKey: ["agent-activity", workspaceId, id],
    queryFn: () => agentsService.getActivity(id).then(res => res.data),
    enabled: enabled && !!id,
  });
};

export const useModels = () => {
  return useQuery({
    queryKey: ["models"],
    queryFn: () => agentsService.getModels().then(res => res.data),
    staleTime: 1000 * 60 * 60, // 1 hour
  });
};

// --- Mutations ---

export const useCreateAgent = () => {
  const queryClient = useQueryClient();
  const { workspaceId } = useWorkspaceContext();
  return useMutation({
    mutationFn: (payload: { name: string; description?: string; agent_type: string }) => 
      agentsService.createAgent(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["agents", workspaceId] });
    },
  });
};

export const useUpdateAgentPrompt = (id: string) => {
  const queryClient = useQueryClient();
  const { workspaceId } = useWorkspaceContext();
  return useMutation({
    mutationFn: (payload: any) => agentsService.updatePrompt(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["agent", workspaceId, id] });
    },
  });
};

export const useUpdateModelConfig = (id: string) => {
  const queryClient = useQueryClient();
  const { workspaceId } = useWorkspaceContext();
  return useMutation({
    mutationFn: (payload: any) => agentsService.updateModelConfig(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["agent", workspaceId, id] });
    },
  });
};

export const useUpdateEscalation = (id: string) => {
  const queryClient = useQueryClient();
  const { workspaceId } = useWorkspaceContext();
  return useMutation({
    mutationFn: (payload: any) => agentsService.updateEscalationRules(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["agent", workspaceId, id] });
    },
  });
};

export const useAssignKnowledge = (id: string) => {
  const queryClient = useQueryClient();
  const { workspaceId } = useWorkspaceContext();
  return useMutation({
    mutationFn: (payload: any) => agentsService.assignKnowledge(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["agent", workspaceId, id] });
    },
  });
};

export const usePublishAgent = (id: string) => {
  const queryClient = useQueryClient();
  const { workspaceId } = useWorkspaceContext();
  return useMutation({
    mutationFn: () => agentsService.publishAgent(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["agent", workspaceId, id] });
      queryClient.invalidateQueries({ queryKey: ["agent-activity", workspaceId, id] });
    },
  });
};

export const useTestAgent = (id: string) => {
  return useMutation({
    mutationFn: (query: string) => agentsService.testAgent(id, query).then(res => res.data),
  });
};

export const useCloneAgent = () => {
  const queryClient = useQueryClient();
  const { workspaceId } = useWorkspaceContext();
  return useMutation({
    mutationFn: (id: string) => agentsService.cloneAgent(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["agents", workspaceId] });
    },
  });
};

export const useArchiveAgent = () => {
  const queryClient = useQueryClient();
  const { workspaceId } = useWorkspaceContext();
  return useMutation({
    mutationFn: (id: string) => agentsService.archiveAgent(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ["agents", workspaceId] });
      queryClient.invalidateQueries({ queryKey: ["agent", workspaceId, id] });
    },
  });
};
