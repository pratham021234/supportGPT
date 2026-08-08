import { apiClient } from './api-client';
import { User } from '@/store/authStore';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  full_name: string;
  password: string;
  confirm_password: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export const authClient = {
  login: (data: LoginRequest) => 
    apiClient<AuthResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
      skipAuth: true
    }),

  register: (data: RegisterRequest) => 
    apiClient<{ email: string }>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
      skipAuth: true
    }),

  logoutAll: () => 
    apiClient<{ success: boolean }>('/auth/logout-all', {
      method: 'POST'
    }),

  refresh: (refreshToken: string) => 
    apiClient<AuthResponse>('/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: refreshToken }),
      skipAuth: true
    })
};
