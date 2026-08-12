import { toast } from 'sonner';
import { AxiosError } from 'axios';

export const handleApiError = (error: unknown) => {
  if (error instanceof AxiosError) {
    const status = error.response?.status;
    const data = error.response?.data as { detail?: string; message?: string } | undefined;
    
    // Default message
    const message = data?.detail || data?.message || error.message || 'An unexpected error occurred.';

    switch (status) {
      case 400:
        toast.error('Bad Request', { description: message });
        break;
      case 401:
        toast.error('Session Expired', { description: 'Please log in again.' });
        // The client.ts interceptor should handle redirecting/logging out if refresh fails.
        break;
      case 403:
        toast.error('Access Denied', { description: 'You do not have permission to perform this action.' });
        break;
      case 404:
        toast.error('Not Found', { description: 'The requested resource could not be found.' });
        break;
      case 422:
        toast.error('Validation Error', { description: message });
        break;
      case 429:
        toast.error('Rate Limit Exceeded', { description: 'Please wait a moment before trying again.' });
        break;
      case 500:
      case 502:
      case 503:
      case 504:
        toast.error('Server Error', { description: 'We are experiencing internal issues. Please try again later.' });
        break;
      default:
        if (error.code === 'ECONNABORTED') {
          toast.error('Request Timeout', { description: 'The request took too long to complete.' });
        } else if (!error.response) {
          toast.error('Network Error', { description: 'Please check your internet connection.' });
        } else {
          toast.error('Error', { description: message });
        }
        break;
    }
  } else if (error instanceof Error) {
    toast.error('Error', { description: error.message });
  } else {
    toast.error('Unknown Error', { description: 'An unexpected error occurred.' });
  }
};
