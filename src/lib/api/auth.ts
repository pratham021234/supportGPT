import { apiClient } from './client';
import { AuthResponse, User } from '@/types/api';

export const authService = {
  login: async (credentials: any): Promise<AuthResponse> => {
    return apiClient.post('/auth/login', credentials);
  },
  register: async (data: any): Promise<AuthResponse> => {
    return apiClient.post('/auth/register', data);
  },
  forgotPassword: async (email: string): Promise<{ message: string }> => {
    return apiClient.post('/auth/forgot-password', { email });
  },
  resetPassword: async (data: any): Promise<{ message: string }> => {
    return apiClient.post('/auth/reset-password', data);
  },
  verifyEmail: async (token: string): Promise<{ message: string }> => {
    return apiClient.post('/auth/verify-email', { token });
  },
  refreshToken: async (token: string): Promise<AuthResponse> => {
    return apiClient.post('/auth/refresh', { refresh_token: token });
  },
  logout: async (): Promise<{ message: string }> => {
    return apiClient.post('/auth/logout');
  },
  getCurrentUser: async (): Promise<User> => {
    return apiClient.get('/auth/me');
  },
};
