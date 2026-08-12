import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from './client';
import { toast } from 'sonner';

export interface WidgetConfig {
  theme?: string;
  primary_color?: string;
  logo_url?: string;
  launcher_text?: string;
  welcome_message?: string;
  position?: string;
  assigned_agent_id?: string;
}

export interface WidgetAnalytics {
  total_opens: number;
  total_messages: number;
  resolution_rate: number;
  escalations: number;
}

export const widgetClient = {
  // Public Endpoint for the embed
  getPublicConfig: async (agentId: string): Promise<WidgetConfig> => {
    const res = await apiClient.get(`/widget/config/${agentId}`);
    return res.data;
  },

  // Admin Endpoints
  getAdminSettings: async (): Promise<WidgetConfig> => {
    const res = await apiClient.get('/widget/settings');
    return res.data;
  },

  updateAdminSettings: async (data: Partial<WidgetConfig>): Promise<WidgetConfig> => {
    const res = await apiClient.patch('/widget/settings', data);
    return res.data;
  },

  // Session Initiation (Public)
  initSession: async (data: { workspace_id: string; agent_id: string; customer_email?: string; customer_name?: string }): Promise<{ session_token: string }> => {
    const res = await apiClient.post('/widget/session', data);
    return res.data;
  },
  
  startConversation: async (session_token: string): Promise<{ conversation_id: string }> => {
    const res = await apiClient.post('/widget/conversations', { session_token });
    return res.data;
  },

  // Mocked Analytics
  getAnalytics: async (): Promise<WidgetAnalytics> => {
    return {
      total_opens: 12450,
      total_messages: 45210,
      resolution_rate: 82.4,
      escalations: 142
    };
  }
};

export const useAdminWidgetSettings = () => useQuery({ 
  queryKey: ['widget-admin-settings'], 
  queryFn: widgetClient.getAdminSettings 
});

export const useWidgetAnalytics = () => useQuery({ 
  queryKey: ['widget-analytics'], 
  queryFn: widgetClient.getAnalytics 
});

export const useUpdateWidgetSettings = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: widgetClient.updateAdminSettings,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['widget-admin-settings'] });
      toast.success('Widget settings updated successfully');
    },
    onError: () => toast.error('Failed to update widget settings')
  });
};
