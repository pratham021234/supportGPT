import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { handleApiError } from './error-handler';
// Note: We need a way to get and set tokens. We assume the auth logic relies on localStorage for the Zustand store.
// In a real implementation, we would access the store directly, but since we are outside React, 
// we read from localStorage (zustand persist).

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Helper to get tokens from Zustand persist store
const getTokens = () => {
  if (typeof window === 'undefined') return null;
  try {
    const authStorage = localStorage.getItem('auth-storage');
    if (!authStorage) return null;
    const { state } = JSON.parse(authStorage);
    return {
      accessToken: state?.accessToken as string | undefined,
      refreshToken: state?.refreshToken as string | undefined,
    };
  } catch {
    return null;
  }
};

const setTokens = (accessToken: string, refreshToken: string) => {
  if (typeof window === 'undefined') return;
  try {
    const authStorage = localStorage.getItem('auth-storage');
    if (!authStorage) return;
    const parsed = JSON.parse(authStorage);
    parsed.state.accessToken = accessToken;
    parsed.state.refreshToken = refreshToken;
    localStorage.setItem('auth-storage', JSON.stringify(parsed));
  } catch (e) {
    console.error('Failed to save tokens', e);
  }
};

const clearTokens = () => {
  if (typeof window === 'undefined') return;
  try {
    const authStorage = localStorage.getItem('auth-storage');
    if (!authStorage) return;
    const parsed = JSON.parse(authStorage);
    parsed.state.accessToken = null;
    parsed.state.refreshToken = null;
    parsed.state.user = null;
    parsed.state.workspace = null;
    parsed.state.isAuthenticated = false;
    localStorage.setItem('auth-storage', JSON.stringify(parsed));
    window.location.href = '/login';
  } catch (e) {
    console.error('Failed to clear tokens', e);
  }
};

let isRefreshing = false;
let failedQueue: Array<{
  resolve: (value?: unknown) => void;
  reject: (reason?: any) => void;
}> = [];

const processQueue = (error: AxiosError | null, token: string | null = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

// Request Interceptor
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const tokens = getTokens();
    if (tokens?.accessToken) {
      config.headers['Authorization'] = `Bearer ${tokens.accessToken}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor
apiClient.interceptors.response.use(
  (response) => {
    // If backend returns data wrapped in { data: ... }, extract it. 
    // We'll return response.data directly for simplicity, components should access data.data if needed, 
    // or we can unwrap it here. Assuming standard REST, we return response.data.
    return response.data;
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    // Handle 401 and Token Refresh
    if (error.response?.status === 401 && !originalRequest._retry && originalRequest.url !== '/auth/refresh') {
      if (isRefreshing) {
        // Queue the request
        return new Promise(function(resolve, reject) {
          failedQueue.push({ resolve, reject });
        }).then(token => {
          originalRequest.headers['Authorization'] = 'Bearer ' + token;
          return apiClient(originalRequest);
        }).catch(err => {
          return Promise.reject(err);
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      const tokens = getTokens();
      if (!tokens?.refreshToken) {
        clearTokens();
        handleApiError(error);
        return Promise.reject(error);
      }

      try {
        const { data } = await axios.post(`${API_BASE_URL}/auth/refresh`, {
          refresh_token: tokens.refreshToken,
        });

        // Save new tokens
        setTokens(data.accessToken, data.refreshToken);
        
        // Update original request
        originalRequest.headers['Authorization'] = `Bearer ${data.accessToken}`;
        
        // Process queue
        processQueue(null, data.accessToken);
        
        return apiClient(originalRequest);
      } catch (err) {
        processQueue(err as AxiosError, null);
        clearTokens();
        handleApiError(err);
        return Promise.reject(err);
      } finally {
        isRefreshing = false;
      }
    }

    // Handle other errors globally
    handleApiError(error);
    return Promise.reject(error);
  }
);
