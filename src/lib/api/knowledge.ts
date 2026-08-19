import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "./client";
import { useAuthStore } from "@/store/authStore";

export interface KnowledgeDocument {
  id: string;
  workspace_id: string;
  source_id?: string;
  title: string;
  file_name?: string;
  file_type?: string;
  file_size?: number;
  status: 'QUEUED' | 'PROCESSING' | 'READY' | 'FAILED';
  version: number;
  is_current_version: boolean;
  created_by?: string;
  created_at: string;
  updated_at: string;
  tags: any[];
  metadata?: any;
}

export interface WebsiteUpload {
  url: string;
  source_id?: string;
}

export interface FAQ {
  id: string;
  question: string;
  answer: string;
  category?: string;
}

export interface KnowledgeHealth {
  status: string;
  documents_count: number;
  chunks_count: number;
  vector_storage: any;
}

export interface SearchResult {
  id: string;
  score: number;
  content: string;
  metadata: any;
}

export interface KnowledgeAnalytics {
  most_used: any[];
  least_used: any[];
  top_sources: any[];
  growth: any[];
  coverage_trend: number;
}

const useWorkspaceContext = () => {
  const workspaceId = useAuthStore(state => state.workspace?.id);
  return { workspaceId, enabled: !!workspaceId };
};

export const knowledgeService = {
  getDocuments: () => 
    apiClient.get<KnowledgeDocument[]>('/knowledge/documents'),
    
  getDocument: (id: string) => 
    apiClient.get<KnowledgeDocument>(`/knowledge/documents/${id}`),
    
  uploadDocument: (file: File, sourceId?: string) => {
    const formData = new FormData();
    formData.append('file', file);
    if (sourceId) formData.append('source_id', sourceId);
    
    return apiClient.post<KnowledgeDocument>('/knowledge/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },

  crawlWebsite: (payload: WebsiteUpload) => 
    apiClient.post<KnowledgeDocument>('/knowledge/documents/website', payload),
    
  deleteDocument: (id: string) => 
    apiClient.delete(`/knowledge/documents/${id}`),
    
  reprocessDocument: (id: string) => 
    apiClient.post(`/knowledge/documents/${id}/reprocess`),
    
  getFaqs: () => 
    apiClient.get<FAQ[]>('/knowledge/faqs'),
    
  createFaq: (faq: Omit<FAQ, 'id'>) => 
    apiClient.post<FAQ>('/knowledge/faqs', faq),
    
  search: (query: string, limit = 10) => 
    apiClient.get<{results: SearchResult[]}>('/knowledge/search', { params: { query, limit } }),
    
  getHealth: () => 
    apiClient.get<KnowledgeHealth>('/knowledge/health'),
    
  getAnalytics: () => 
    apiClient.get<KnowledgeAnalytics>('/analytics/knowledge'),
    
  getDocumentChunks: (id: string) => 
    apiClient.get<{chunks: any[], total: number}>(`/knowledge/documents/${id}/chunks`),
    
  rechunkDocument: (id: string, payload: { chunk_strategy: string, chunk_size: number, chunk_overlap: number }) => 
    apiClient.post(`/knowledge/documents/${id}/rechunk`, payload),
    
  reembedDocument: (id: string) => 
    apiClient.post(`/knowledge/documents/${id}/reembed`),
    
  getEmbeddingAnalytics: () => 
    apiClient.get<any>('/analytics/embeddings'),
};

// --- Hooks ---

export const useDocuments = () => {
  const { workspaceId, enabled } = useWorkspaceContext();
  return useQuery({
    queryKey: ["knowledge-documents", workspaceId],
    queryFn: () => knowledgeService.getDocuments().then(res => res.data),
    enabled,
    staleTime: 1000 * 30,
  });
};

export const useDocument = (id: string) => {
  const { workspaceId, enabled } = useWorkspaceContext();
  return useQuery({
    queryKey: ["knowledge-document", workspaceId, id],
    queryFn: () => knowledgeService.getDocument(id).then(res => res.data),
    enabled: enabled && !!id,
    staleTime: 1000 * 30,
  });
};

export const useKnowledgeHealth = () => {
  const { workspaceId, enabled } = useWorkspaceContext();
  return useQuery({
    queryKey: ["knowledge-health", workspaceId],
    queryFn: () => knowledgeService.getHealth().then(res => res.data),
    enabled,
    staleTime: 1000 * 60,
  });
};

export const useDocumentChunks = (id: string) => {
  const { workspaceId, enabled } = useWorkspaceContext();
  return useQuery({
    queryKey: ["knowledge-document-chunks", workspaceId, id],
    queryFn: () => knowledgeService.getDocumentChunks(id).then(res => res.data),
    enabled: enabled && !!id,
    staleTime: 1000 * 30,
  });
};

export const useKnowledgeSearch = (query: string, limit = 10) => {
  const { workspaceId, enabled } = useWorkspaceContext();
  return useQuery({
    queryKey: ["knowledge-search", workspaceId, query, limit],
    queryFn: () => knowledgeService.search(query, limit).then(res => res.data.results),
    enabled: enabled && query.length > 2,
    staleTime: 1000 * 60,
  });
};

export const useFaqs = () => {
  const { workspaceId, enabled } = useWorkspaceContext();
  return useQuery({
    queryKey: ["knowledge-faqs", workspaceId],
    queryFn: () => knowledgeService.getFaqs().then(res => res.data),
    enabled,
    staleTime: 1000 * 60,
  });
};

export const useKnowledgeAnalytics = () => {
  const { workspaceId, enabled } = useWorkspaceContext();
  return useQuery({
    queryKey: ["knowledge-analytics", workspaceId],
    queryFn: () => knowledgeService.getAnalytics().then(res => res.data),
    enabled,
    staleTime: 1000 * 60 * 5,
  });
};

// --- Mutations ---

export const useUploadDocument = () => {
  const queryClient = useQueryClient();
  const { workspaceId } = useWorkspaceContext();
  
  return useMutation({
    mutationFn: ({ file, sourceId }: { file: File; sourceId?: string }) => 
      knowledgeService.uploadDocument(file, sourceId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["knowledge-documents", workspaceId] });
      queryClient.invalidateQueries({ queryKey: ["knowledge-health", workspaceId] });
    },
  });
};

export const useCrawlWebsite = () => {
  const queryClient = useQueryClient();
  const { workspaceId } = useWorkspaceContext();
  
  return useMutation({
    mutationFn: (payload: WebsiteUpload) => knowledgeService.crawlWebsite(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["knowledge-documents", workspaceId] });
      queryClient.invalidateQueries({ queryKey: ["knowledge-health", workspaceId] });
    },
  });
};

export const useRechunkDocument = () => {
  const queryClient = useQueryClient();
  const { workspaceId } = useWorkspaceContext();
  
  return useMutation({
    mutationFn: ({ id, payload }: { id: string, payload: { chunk_strategy: string, chunk_size: number, chunk_overlap: number } }) => 
      knowledgeService.rechunkDocument(id, payload),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ["knowledge-document", workspaceId, id] });
      queryClient.invalidateQueries({ queryKey: ["knowledge-document-chunks", workspaceId, id] });
    },
  });
};

export const useCreateFaq = () => {
  const queryClient = useQueryClient();
  const { workspaceId } = useWorkspaceContext();
  
  return useMutation({
    mutationFn: (faq: Omit<FAQ, 'id'>) => knowledgeService.createFaq(faq),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["knowledge-faqs", workspaceId] });
    },
  });
};

export const useDeleteDocument = () => {
  const queryClient = useQueryClient();
  const { workspaceId } = useWorkspaceContext();
  
  return useMutation({
    mutationFn: (id: string) => knowledgeService.deleteDocument(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["knowledge-documents", workspaceId] });
      queryClient.invalidateQueries({ queryKey: ["knowledge-health", workspaceId] });
    },
  });
};

export const useReprocessDocument = () => {
  const queryClient = useQueryClient();
  const { workspaceId } = useWorkspaceContext();
  
  return useMutation({
    mutationFn: (id: string) => knowledgeService.reprocessDocument(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ["knowledge-documents", workspaceId] });
      queryClient.invalidateQueries({ queryKey: ["knowledge-document", workspaceId, id] });
    },
  });
};

export const useReembedDocument = () => {
  const queryClient = useQueryClient();
  const { workspaceId } = useWorkspaceContext();
  
  return useMutation({
    mutationFn: (id: string) => knowledgeService.reembedDocument(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ["knowledge-document", workspaceId, id] });
      queryClient.invalidateQueries({ queryKey: ["knowledge-document-embeddings", workspaceId, id] });
    },
  });
};

export const useEmbeddingAnalytics = () => {
  const { workspaceId, enabled } = useWorkspaceContext();
  return useQuery({
    queryKey: ["knowledge-embedding-analytics", workspaceId],
    queryFn: () => knowledgeService.getEmbeddingAnalytics().then(res => res.data),
    enabled,
    staleTime: 1000 * 60,
  });
};
