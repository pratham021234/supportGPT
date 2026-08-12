import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from './client';
import { Agent } from './agents';
import { toast } from 'sonner';

export interface PromptUpdate {
  system_prompt?: string;
  welcome_message?: string;
  fallback_message?: string;
  tone?: string;
  behavior_rules?: string; // used for safety/citations JSON strings
}

export interface ModelConfigUpdate {
  provider?: string;
  model?: string;
  temperature?: number;
  max_tokens?: number;
  top_p?: number;
}

export interface EscalationRuleUpdate {
  confidence_threshold?: number;
  auto_create_ticket?: boolean;
  auto_handoff?: boolean;
  escalation_message?: string;
}

export interface TestAgentResponse {
  answer: string;
  sources: any[];
  confidence: number;
  latency_ms: number;
  requires_escalation: boolean;
}

export interface PromptVersion {
  version_number: number;
  created_by: string;
  created_at: string;
  changes: string;
  status: "ACTIVE" | "ARCHIVED";
}

export const promptStudioService = {
  // Using the agents API since prompt-studio logic is attached to agents in backend
  getAgents: async () => {
    const res = await apiClient.get<Agent[]>('/agents');
    return res.data;
  },

  updatePrompt: async (agentId: string, data: PromptUpdate) => {
    const res = await apiClient.patch(`/agents/${agentId}/prompt`, data);
    return res.data;
  },

  updateModelSettings: async (agentId: string, data: ModelConfigUpdate) => {
    const res = await apiClient.patch(`/agents/${agentId}/model`, data);
    return res.data;
  },

  updateEscalationRules: async (agentId: string, data: EscalationRuleUpdate) => {
    const res = await apiClient.patch(`/agents/${agentId}/escalation`, data);
    return res.data;
  },

  testAgent: async (agentId: string, query: string) => {
    const res = await apiClient.post<TestAgentResponse>(`/agents/${agentId}/test`, { query });
    return res.data;
  },

  publishVersion: async (agentId: string) => {
    const res = await apiClient.post(`/agents/${agentId}/publish`);
    return res.data;
  },

  rollbackVersion: async (agentId: string, versionNumber: number) => {
    const res = await apiClient.post(`/agents/${agentId}/rollback`, { version_number: versionNumber });
    return res.data;
  },

  // Mocked for missing backend features
  getVersions: async (agentId: string): Promise<PromptVersion[]> => {
    return [
      { version_number: 3, created_by: "Admin", created_at: new Date().toISOString(), changes: "Updated escalation threshold to 75%", status: "ACTIVE" },
      { version_number: 2, created_by: "Admin", created_at: new Date(Date.now() - 86400000).toISOString(), changes: "Added empathy instruction to prompt", status: "ARCHIVED" },
      { version_number: 1, created_by: "System", created_at: new Date(Date.now() - 172800000).toISOString(), changes: "Initial creation", status: "ARCHIVED" },
    ];
  },

  getAnalytics: async (agentId: string) => {
    const res = await apiClient.get(`/agents/${agentId}/analytics`);
    return res.data;
  }
};

// React Query Hooks
export const usePromptStudioAgents = () => {
  return useQuery({
    queryKey: ['prompt-studio-agents'],
    queryFn: promptStudioService.getAgents,
  });
};

export const useUpdatePrompt = (agentId: string) => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: PromptUpdate) => promptStudioService.updatePrompt(agentId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['prompt-studio-agents'] });
      toast.success("System prompt saved successfully");
    },
    onError: () => toast.error("Failed to save system prompt")
  });
};

export const useUpdateModelSettings = (agentId: string) => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: ModelConfigUpdate) => promptStudioService.updateModelSettings(agentId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['prompt-studio-agents'] });
      toast.success("Model settings saved successfully");
    },
    onError: () => toast.error("Failed to save model settings")
  });
};

export const useUpdateEscalation = (agentId: string) => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: EscalationRuleUpdate) => promptStudioService.updateEscalationRules(agentId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['prompt-studio-agents'] });
      toast.success("Escalation rules saved successfully");
    },
    onError: () => toast.error("Failed to save escalation rules")
  });
};

export const useTestAgent = (agentId: string) => {
  return useMutation({
    mutationFn: (query: string) => promptStudioService.testAgent(agentId, query),
    onError: () => toast.error("Test execution failed")
  });
};

export const usePublishVersion = (agentId: string) => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => promptStudioService.publishVersion(agentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['prompt-versions', agentId] });
      toast.success("New prompt version published successfully");
    },
    onError: () => toast.error("Failed to publish version")
  });
};

export const useRollbackVersion = (agentId: string) => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (version: number) => promptStudioService.rollbackVersion(agentId, version),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['prompt-studio-agents'] });
      toast.success("Successfully rolled back version");
    },
    onError: () => toast.error("Failed to rollback version")
  });
};

export const usePromptVersions = (agentId: string) => {
  return useQuery({
    queryKey: ['prompt-versions', agentId],
    queryFn: () => promptStudioService.getVersions(agentId),
    enabled: !!agentId
  });
};
