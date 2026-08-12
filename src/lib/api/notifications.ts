import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from './client';
import { toast } from 'sonner';

export interface Notification {
  id: string;
  user_id: string;
  title: string;
  message: string;
  type: string;
  is_read: boolean;
  action_url?: string;
  created_at: string;
}

export interface NotificationPreferences {
  email_enabled: boolean;
  in_app_enabled: boolean;
  digest_enabled: boolean;
}

export const notificationsService = {
  getNotifications: async (): Promise<Notification[]> => {
    // Backend only returns unread right now, but for UI sake we assume it returns all or we can fetch unread
    const res = await apiClient.get('/notifications');
    return res.data;
  },
  
  markAsRead: async (id: string): Promise<void> => {
    await apiClient.patch(`/notifications/${id}/read`);
  },
  
  getPreferences: async (): Promise<NotificationPreferences> => {
    const res = await apiClient.get('/notifications/preferences');
    return res.data;
  },
  
  updatePreferences: async (data: Partial<NotificationPreferences>): Promise<NotificationPreferences> => {
    const res = await apiClient.patch('/notifications/preferences', data);
    return res.data;
  }
};

export const useNotifications = () => {
  return useQuery({
    queryKey: ['notifications'],
    queryFn: notificationsService.getNotifications,
  });
};

export const useNotificationPreferences = () => {
  return useQuery({
    queryKey: ['notification-preferences'],
    queryFn: notificationsService.getPreferences,
  });
};

export const useMarkNotificationRead = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: notificationsService.markAsRead,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    }
  });
};

export const useUpdateNotificationPreferences = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: notificationsService.updatePreferences,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notification-preferences'] });
      toast.success('Notification preferences updated');
    },
    onError: () => toast.error('Failed to update preferences')
  });
};
