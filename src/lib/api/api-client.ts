export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export class ApiError extends Error {
  constructor(public status: number, public data: any) {
    super(data?.message || 'An API error occurred');
    this.name = 'ApiError';
  }
}

interface FetchOptions extends RequestInit {
  params?: Record<string, string>;
  skipAuth?: boolean;
}

export const apiClient = async <T>(endpoint: string, options: FetchOptions = {}): Promise<T> => {
  const { params, skipAuth, ...customConfig } = options;

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...customConfig.headers,
  };

  if (!skipAuth) {
    // For client components, access local storage directly or via Zustand
    if (typeof window !== 'undefined') {
      const authState = localStorage.getItem('auth-storage');
      if (authState) {
        try {
          const parsed = JSON.parse(authState);
          const token = parsed?.state?.accessToken;
          if (token) {
            headers['Authorization'] = `Bearer ${token}`;
          }
        } catch (e) {
          console.error('Failed to parse auth storage', e);
        }
      }
    }
  }

  const config: RequestInit = {
    ...customConfig,
    headers,
  };

  const url = new URL(`${API_BASE_URL}${endpoint}`);
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      url.searchParams.append(key, value);
    });
  }

  try {
    const response = await fetch(url.toString(), config);
    const data = await response.json().catch(() => ({}));

    if (response.ok) {
      // The backend wraps responses in { success, data, message }
      return data.data as T;
    }

    if (response.status === 401 && !skipAuth && typeof window !== 'undefined') {
      // Attempt refresh or logout
      // For now, let the calling hook handle the mutation/error
      console.warn("Unauthorized API call");
    }

    throw new ApiError(response.status, data);
  } catch (error) {
    if (error instanceof ApiError) throw error;
    throw new ApiError(500, { message: 'Network error or unable to parse response' });
  }
};
