import type {
  Project,
  CreateProjectRequest,
  UpdateProjectRequest,
  SubmitBriefRequest,
  GenerateConceptRequest,
  GenerateScreenplaysRequest,
  SelectScreenplayRequest,
  GenerateStoryboardRequest,
  RegenerateSceneRequest,
  GenerateProductionPackRequest,
  UpdateProductionDocumentRequest,
  ApproveDocumentRequest,
  ExportRequest,
  ExportResponse,
  ProjectFilters,
} from './types';

// ============================================================================
// Configuration
// ============================================================================

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:2501';

// ============================================================================
// Error Handling
// ============================================================================

export class APIError extends Error {
  constructor(
    message: string,
    public status: number,
    public code?: string
  ) {
    super(message);
    this.name = 'APIError';
  }
}

/**
 * Parse error response and create user-friendly error message
 */
async function handleErrorResponse(response: Response): Promise<never> {
  let errorMessage = 'An unexpected error occurred';
  let errorCode: string | undefined;

  try {
    const errorData = await response.json();
    errorMessage = errorData.message || errorData.detail || errorMessage;
    errorCode = errorData.code;
  } catch {
    // If JSON parsing fails, use status text
    errorMessage = response.statusText || errorMessage;
  }

  throw new APIError(errorMessage, response.status, errorCode);
}

// ============================================================================
// HTTP Client
// ============================================================================

interface RequestOptions extends RequestInit {
  params?: Record<string, string | number | boolean | undefined>;
}

/**
 * Base fetch wrapper with error handling and authentication
 */
async function request<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const { params, ...fetchOptions } = options;

  // Build URL with query parameters
  const url = new URL(`${API_BASE_URL}${endpoint}`);
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        url.searchParams.append(key, String(value));
      }
    });
  }

  // Get auth token from localStorage (if available)
  const token =
    typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null;

  // Set default headers
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  // Add custom headers from options
  if (fetchOptions.headers) {
    Object.entries(fetchOptions.headers).forEach(([key, value]) => {
      if (typeof value === 'string') {
        headers[key] = value;
      }
    });
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  try {
    console.log('[API] Fetching:', url.toString());
    
    const response = await fetch(url.toString(), {
      ...fetchOptions,
      headers,
    });

    console.log('[API] Response status:', response.status);

    if (!response.ok) {
      await handleErrorResponse(response);
    }

    // Handle empty responses (204 No Content)
    if (response.status === 204) {
      return undefined as T;
    }

    const data = await response.json();
    console.log('[API] Response data:', data);
    return data;
  } catch (error) {
    console.error('[API] Error:', error);
    console.error('[API] URL was:', url.toString());
    console.error('[API] Error details:', {
      name: error instanceof Error ? error.name : 'Unknown',
      message: error instanceof Error ? error.message : 'Unknown error',
      stack: error instanceof Error ? error.stack : undefined
    });
    
    if (error instanceof APIError) {
      throw error;
    }
    // Network errors or other fetch failures
    throw new APIError(
      error instanceof Error ? error.message : 'Network error',
      0
    );
  }
}

// ============================================================================
// Projects API
// ============================================================================

export const projectsAPI = {
  /**
   * Get all projects with optional filters
   */
  async list(filters?: ProjectFilters): Promise<Project[]> {
    const params: Record<string, string | undefined> = {};

    if (filters) {
      if (filters.status) params.status = filters.status;
      if (filters.client) params.client = filters.client;
      if (filters.budgetBand) params.budget_band = filters.budgetBand;
      if (filters.search) params.search = filters.search;
      if (filters.tags) params.tags = filters.tags.join(',');
    }

    return request<Project[]>('/api/projects', { params });
  },

  /**
   * Get a single project by ID
   */
  async get(id: string): Promise<Project> {
    return request<Project>(`/api/projects/${id}`);
  },

  /**
   * Create a new project
   */
  async create(data: CreateProjectRequest): Promise<Project> {
    return request<Project>('/api/projects', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Update an existing project
   */
  async update(id: string, data: UpdateProjectRequest): Promise<Project> {
    return request<Project>(`/api/projects/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  },

  /**
   * Delete a project
   */
  async delete(id: string): Promise<void> {
    return request<void>(`/api/projects/${id}`, {
      method: 'DELETE',
    });
  },
};

// ============================================================================
// Brief API
// ============================================================================

export const briefAPI = {
  /**
   * Submit a brief for a project
   */
  async submit(projectId: string, data: SubmitBriefRequest): Promise<Project> {
    return request<Project>(`/api/projects/${projectId}/brief`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Update a brief
   */
  async update(projectId: string, data: SubmitBriefRequest): Promise<Project> {
    return request<Project>(`/api/projects/${projectId}/brief`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  },
};

// ============================================================================
// Generation API
// ============================================================================

export const generationAPI = {
  /**
   * Generate concept from brief
   */
  async generateConcept(data: GenerateConceptRequest): Promise<{
    jobId: string;
    estimatedTime: number;
    estimatedCost: number;
  }> {
    return request(`/api/projects/${data.projectId}/generate/concept`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Generate screenplay variants
   */
  async generateScreenplays(data: GenerateScreenplaysRequest): Promise<{
    jobId: string;
    estimatedTime: number;
    estimatedCost: number;
  }> {
    return request(`/api/projects/${data.projectId}/generate/screenplays`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Generate storyboard from selected screenplay
   */
  async generateStoryboard(data: GenerateStoryboardRequest): Promise<{
    jobId: string;
    estimatedTime: number;
    estimatedCost: number;
  }> {
    return request(`/api/projects/${data.projectId}/generate/storyboard`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Regenerate a single scene
   */
  async regenerateScene(data: RegenerateSceneRequest): Promise<{
    jobId: string;
    estimatedTime: number;
    estimatedCost: number;
  }> {
    return request(
      `/api/projects/${data.projectId}/regenerate/scene/${data.sceneNumber}`,
      {
        method: 'POST',
        body: JSON.stringify(data),
      }
    );
  },

  /**
   * Generate production pack
   */
  async generateProductionPack(data: GenerateProductionPackRequest): Promise<{
    jobId: string;
    estimatedTime: number;
    estimatedCost: number;
  }> {
    return request(`/api/projects/${data.projectId}/generate/production`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Cancel an ongoing generation job
   */
  async cancelJob(jobId: string): Promise<void> {
    return request(`/api/jobs/${jobId}/cancel`, {
      method: 'POST',
    });
  },

  /**
   * Get job status
   */
  async getJobStatus(jobId: string): Promise<{
    status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
    progress: number;
    result?: any;
    error?: string;
  }> {
    return request(`/api/jobs/${jobId}`);
  },
};

// ============================================================================
// Selection API
// ============================================================================

export const selectionAPI = {
  /**
   * Select winning screenplay variant
   */
  async selectScreenplay(data: SelectScreenplayRequest): Promise<Project> {
    return request(`/api/projects/${data.projectId}/select/screenplay`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
};

// ============================================================================
// Production Pack API
// ============================================================================

export const productionAPI = {
  /**
   * Update a production document
   */
  async updateDocument(
    data: UpdateProductionDocumentRequest
  ): Promise<Project> {
    return request(
      `/api/projects/${data.projectId}/production/${data.documentType}`,
      {
        method: 'PATCH',
        body: JSON.stringify({ content: data.content }),
      }
    );
  },

  /**
   * Approve a production document
   */
  async approveDocument(data: ApproveDocumentRequest): Promise<Project> {
    return request(
      `/api/projects/${data.projectId}/production/${data.documentType}/approve`,
      {
        method: 'POST',
      }
    );
  },
};

// ============================================================================
// Export API
// ============================================================================

export const exportAPI = {
  /**
   * Generate export files
   */
  async create(data: ExportRequest): Promise<ExportResponse> {
    return request(`/api/projects/${data.projectId}/export`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Get export history for a project
   */
  async list(projectId: string): Promise<ExportResponse[]> {
    return request(`/api/projects/${projectId}/exports`);
  },

  /**
   * Download an export file
   */
  getDownloadUrl(projectId: string, exportId: string): string {
    return `${API_BASE_URL}/api/projects/${projectId}/exports/${exportId}`;
  },
};

// ============================================================================
// Authentication API
// ============================================================================

export const authAPI = {
  /**
   * Store authentication token
   */
  setToken(token: string): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', token);
    }
  },

  /**
   * Get authentication token
   */
  getToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('auth_token');
    }
    return null;
  },

  /**
   * Remove authentication token
   */
  clearToken(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
    }
  },

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return this.getToken() !== null;
  },
};

// ============================================================================
// Exports
// ============================================================================

export const api = {
  projects: projectsAPI,
  brief: briefAPI,
  generation: generationAPI,
  selection: selectionAPI,
  production: productionAPI,
  export: exportAPI,
  auth: authAPI,
};

export default api;
