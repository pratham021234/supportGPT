import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from './client';
import { toast } from 'sonner';

export interface ApiKey {
  id: string;
  name: string;
  scopes: string[];
  last_used?: string;
  created_at: string;
  key_preview?: string; // e.g. "sk_live_...1a2b"
}

export interface Webhook {
  id: string;
  url: string;
  events: string[];
  status: 'active' | 'failing';
  created_at: string;
}

export interface AIProvider {
  id: string;
  name: string;
  is_enabled: boolean;
  priority: number;
}

export interface SystemHealth {
  status: 'healthy' | 'degraded' | 'down';
  database: string;
  redis: string;
  vector_db: string;
  api: string;
  version: string;
}

export interface UsageStats {
  conversations_count: number;
  conversations_limit: number;
  documents_count: number;
  documents_limit: number;
  agents_count: number;
  agents_limit: number;
  api_calls_count: number;
  api_calls_limit: number;
}

export const settingsService = {
  // API Keys (mapped to actual backend)
  getApiKeys: async (): Promise<ApiKey[]> => {
    const res = await apiClient.get('/security/api-keys');
    return res.data;
  },
  createApiKey: async (data: { name: string; scopes: string[] }): Promise<{ key_id: string; raw_key: string; name: string }> => {
    const res = await apiClient.post('/security/api-keys', data);
    return res.data;
  },
  revokeApiKey: async (id: string): Promise<void> => {
    await apiClient.delete(`/security/api-keys/${id}`);
  },

  // System Health (mapped to actual backend)
  getSystemStatus: async (): Promise<SystemHealth> => {
    const res = await apiClient.get('/health');
    return res.data;
  },

  // Export Data (mapped to actual backend)
  exportData: async (): Promise<any> => {
    const res = await apiClient.post('/security/compliance/export');
    return res.data;
  },

  // --- MOCKED ENDPOINTS (Since backend missing tables for these) ---

  // Webhooks
  getWebhooks: async (): Promise<Webhook[]> => {
    return [
      { id: "wh_1", url: "https://api.example.com/webhooks/supportgpt", events: ["ticket.created", "conversation.created"], status: 'active', created_at: new Date().toISOString() }
    ];
  },
  createWebhook: async (data: { url: string; events: string[] }): Promise<Webhook> => {
    return { id: `wh_${Math.floor(Math.random()*1000)}`, url: data.url, events: data.events, status: 'active', created_at: new Date().toISOString() };
  },
  deleteWebhook: async (id: string): Promise<void> => {
    // Mock delete
  },

  // AI Providers
  getAiProviders: async (): Promise<AIProvider[]> => {
    return [
      { id: "gpt-4o", name: "OpenAI GPT-4o", is_enabled: true, priority: 1 },
      { id: "claude-3-5", name: "Anthropic Claude 3.5", is_enabled: true, priority: 2 },
      { id: "gemini-1-5", name: "Google Gemini 1.5", is_enabled: false, priority: 3 }
    ];
  },
  updateAiProvider: async (id: string, data: Partial<AIProvider>): Promise<void> => {
    // Mock update
  },

  // Usage Analytics (Detailed)
  getUsage: async (): Promise<UsageStats> => {
    return {
      conversations_count: 8234, conversations_limit: 10000,
      documents_count: 142, documents_limit: 500,
      agents_count: 3, agents_limit: 10,
      api_calls_count: 45012, api_calls_limit: 100000
    };
  }
};

// --- Hooks ---

export const useApiKeys = () => useQuery({ queryKey: ['settings-api-keys'], queryFn: settingsService.getApiKeys });
export const useSystemStatus = () => useQuery({ queryKey: ['settings-system-status'], queryFn: settingsService.getSystemStatus });
export const useWebhooks = () => useQuery({ queryKey: ['settings-webhooks'], queryFn: settingsService.getWebhooks });
export const useAiProviders = () => useQuery({ queryKey: ['settings-ai-providers'], queryFn: settingsService.getAiProviders });
export const useDetailedUsage = () => useQuery({ queryKey: ['settings-usage'], queryFn: settingsService.getUsage });

export const useCreateApiKey = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: settingsService.createApiKey,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings-api-keys'] });
      toast.success('API Key created successfully');
    },
    onError: () => toast.error('Failed to create API key')
  });
};

export const useRevokeApiKey = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: settingsService.revokeApiKey,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings-api-keys'] });
      toast.success('API Key revoked');
    },
    onError: () => toast.error('Failed to revoke API key')
  });
};

export const useCreateWebhook = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: settingsService.createWebhook,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings-webhooks'] });
      toast.success('Webhook created successfully');
    },
    onError: () => toast.error('Failed to create webhook')
  });
};
