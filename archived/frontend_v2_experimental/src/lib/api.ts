export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

type RequestMethod = 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';

interface ApiRequestOptions extends RequestInit {
    token?: string;
}

export class ApiError extends Error {
    constructor(public status: number, public message: string, public data?: any) {
        super(message);
        this.name = 'ApiError';
    }
}

async function request<T>(endpoint: string, method: RequestMethod, body?: any, options?: ApiRequestOptions): Promise<T> {
    const headers: Record<string, string> = {
        ...(options?.headers as Record<string, string>),
    };

    // If body is NOT FormData, set default Content-Type to application/json
    if (!(body instanceof FormData) && !headers['Content-Type']) {
        headers['Content-Type'] = 'application/json';
    }

    // Auto-inject token from localStorage if not explicitly provided
    const token = options?.token || (typeof window !== 'undefined' ? localStorage.getItem('token') : null);
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const config: RequestInit = {
        method,
        headers,
        body: body instanceof FormData ? body : (body ? JSON.stringify(body) : undefined),
        ...options,
    };

    try {
        const response = await fetch(`${API_URL}${endpoint}`, config);

        if (!response.ok) {
            // Handle 401 Unauthorized - Session Expired
            if (response.status === 401) {
                // Dispatch custom event for session expiration
                if (typeof window !== 'undefined') {
                    window.dispatchEvent(new CustomEvent('unauthorized'));
                }
            }

            let errorMessage = 'An error occurred';
            let errorData = null;
            try {
                const errorBody = await response.json();
                errorMessage = errorBody.detail || errorBody.message || errorMessage;
                errorData = errorBody;
            } catch (e) {
                // Ignore JSON parse error for error responses
            }
            throw new ApiError(response.status, errorMessage, errorData);
        }

        // Handle 204 No Content
        if (response.status === 204) {
            return {} as T;
        }

        return await response.json();
    } catch (error) {
        if (error instanceof ApiError) {
            throw error;
        }
        throw new Error('Network error or invalid JSON response');
    }
}

// Assuming RegenerateReportResponse is defined elsewhere or can be `any` for this context
type RegenerateReportResponse = any;

export const api = {
    get: <T>(endpoint: string, options?: ApiRequestOptions) => request<T>(endpoint, 'GET', undefined, options),
    async regenerateReport(campaignId: string, template: string = 'default'): Promise<RegenerateReportResponse> {
        return request<RegenerateReportResponse>(`/campaigns/${campaignId}/report/regenerate`, 'POST', { template });
    },
    async chatWithCampaign(campaignId: string, question: string): Promise<any> {
        return request<any>(`/campaigns/${campaignId}/chat`, 'POST', { question });
    },
    async getCampaignInsights(campaignId: string): Promise<any> {
        return request<any>(`/campaigns/${campaignId}/insights`, 'GET');
    },
    async getCampaignVisualizations(campaignId: string): Promise<any> {
        return request<any>(`/campaigns/${campaignId}/visualizations`, 'GET');
    },
    async getGlobalVisualizations(): Promise<any> {
        return request<any>(`/campaigns/visualizations`, 'GET');
    },
    async chatGlobal(question: string, options?: { knowledge_mode?: boolean; use_rag_context?: boolean }): Promise<any> {
        return request<any>(`/campaigns/chat`, 'POST', {
            question,
            knowledge_mode: options?.knowledge_mode ?? false,
            use_rag_context: options?.use_rag_context ?? true
        });
    },
    async analyzeGlobal(): Promise<any> {
        return request<any>('/campaigns/analyze', 'POST');
    },
    async uploadData(file: File, sheetName?: string): Promise<any> {
        const formData = new FormData();
        formData.append('file', file);
        if (sheetName) {
            formData.append('sheet_name', sheetName);
        }
        return request<any>('/campaigns/upload', 'POST', formData);
    },
    async uploadCampaigns(file: File): Promise<any> {
        const formData = new FormData();
        formData.append('file', file);

        const token = localStorage.getItem('token');
        const headers: HeadersInit = {};
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        // Note: Content-Type is set automatically by fetch when using FormData

        const response = await fetch(`${API_URL}/campaigns/upload`, {
            method: 'POST',
            headers,
            body: formData,
        });

        if (!response.ok) {
            // Handle 401 Unauthorized
            if (response.status === 401 && typeof window !== 'undefined') {
                window.dispatchEvent(new CustomEvent('unauthorized'));
            }

            const error = await response.json().catch(() => ({ detail: 'Upload failed' }));
            throw new Error(error.detail || 'Upload failed');
        }

        return response.json();
    },
    post: <T>(endpoint: string, body: any, options?: ApiRequestOptions) => request<T>(endpoint, 'POST', body, options),
    put: <T>(endpoint: string, body: any, options?: ApiRequestOptions) => request<T>(endpoint, 'PUT', body, options),
    delete: <T>(endpoint: string, options?: ApiRequestOptions) => request<T>(endpoint, 'DELETE', undefined, options),
    patch: <T>(endpoint: string, body: any, options?: ApiRequestOptions) => request<T>(endpoint, 'PATCH', body, options),
    async login(data: any): Promise<any> {
        return request<any>('/auth/login', 'POST', data);
    },
    async register(data: any): Promise<any> {
        return request<any>('/auth/register', 'POST', data);
    },
};

// ============================================================================
// INTELLIGENCE STUDIO API
// ============================================================================

export const intelligenceApi = {
    /**
     * Process a natural language query
     */
    query: async (query: string, context?: any) => {
        return request<any>('/intelligence/query', 'POST', { query, context });
    },

    /**
     * Get categorized query suggestions
     */
    getSuggestions: async () => {
        return request<any>('/intelligence/suggestions', 'GET');
    },

    /**
     * Refine an existing query
     */
    refineQuery: async (originalQuery: string, refinement: string) => {
        return request<any>('/intelligence/refine-query', 'POST', {
            original_query: originalQuery,
            refinement
        });
    }
};

// ============================================================================
// ANOMALY DETECTIVE API
// ============================================================================

export const anomalyApi = {
    /**
     * Detect anomalies using specified method
     */
    detect: async (params?: {
        days?: number;
        severity?: string;
        method?: 'zscore' | 'iqr';
    }) => {
        const queryParams = new URLSearchParams();
        if (params?.days) queryParams.append('days', params.days.toString());
        if (params?.severity) queryParams.append('severity', params.severity);
        if (params?.method) queryParams.append('method', params.method);

        const endpoint = `/anomaly-detective/detect${queryParams.toString() ? `?${queryParams}` : ''}`;
        return request<any>(endpoint, 'GET');
    },

    /**
     * Get all anomalies with optional filtering
     */
    getAnomalies: async (filters?: {
        metric?: string;
        severity?: string;
        status?: string;
        days?: number;
    }) => {
        const queryParams = new URLSearchParams();
        if (filters?.metric) queryParams.append('metric', filters.metric);
        if (filters?.severity) queryParams.append('severity', filters.severity);
        if (filters?.status) queryParams.append('status', filters.status);
        if (filters?.days) queryParams.append('days', filters.days.toString());

        const endpoint = `/anomaly-detective/anomalies${queryParams.toString() ? `?${queryParams}` : ''}`;
        return request<any>(endpoint, 'GET');
    },

    /**
     * Get detailed information about a specific anomaly
     */
    getAnomalyDetail: async (anomalyId: string) => {
        return request<any>(`/anomaly-detective/anomalies/${anomalyId}`, 'GET');
    },

    /**
     * Resolve an anomaly
     */
    resolveAnomaly: async (anomalyId: string, data?: {
        resolution_note?: string;
        action_taken?: string;
    }) => {
        return request<any>(`/anomaly-detective/anomalies/${anomalyId}/resolve`, 'POST', data);
    },

    /**
     * Get available metrics for monitoring
     */
    getAvailableMetrics: async () => {
        return request<any>('/anomaly-detective/metrics/available', 'GET');
    }
};

// ============================================================================
// DASHBOARD BUILDER 2.0 API
// ============================================================================

export const dashboardApi = {
    /**
     * Save a new dashboard
     */
    saveDashboard: async (dashboard: any) => {
        return request<any>('/dashboards', 'POST', dashboard);
    },

    /**
     * List all dashboards
     */
    listDashboards: async () => {
        return request<any[]>('/dashboards', 'GET');
    },

    /**
     * Get a specific dashboard
     */
    getDashboard: async (id: string) => {
        return request<any>(`/dashboards/${id}`, 'GET');
    },

    /**
     * Update a dashboard
     */
    updateDashboard: async (id: string, dashboard: any) => {
        return request<any>(`/dashboards/${id}`, 'PUT', dashboard);
    },

    /**
     * Delete a dashboard
     */
    deleteDashboard: async (id: string) => {
        return request<any>(`/dashboards/${id}`, 'DELETE');
    },

    /**
     * Get AI dashboard templates
     */
    getTemplates: async () => {
        return request<any[]>('/dashboards/templates', 'GET');
    },

    /**
     * Get dynamic data for a widget
     */
    getWidgetData: async (type: string, config: any) => {
        return request<any>(`/dashboards/widgets/${type}/data`, 'POST', config);
    }
};

// ============================================================================
// COMPARISON 2.0 API
// ============================================================================

export const comparisonApi = {
    /**
     * Multi-period comparison
     */
    multiPeriodCompare: async (data: any) => {
        return request<any>('/comparison/multi-period', 'POST', data);
    },

    /**
     * Statistical significance testing
     */
    runStatisticalTest: async (data: any) => {
        return request<any>('/comparison/statistical-test', 'POST', data);
    },

    /**
     * A/B test analysis
     */
    analyzeABTest: async (data: any) => {
        return request<any>('/comparison/ab-test', 'POST', data);
    },

    /**
     * Cohort analysis
     */
    runCohortAnalysis: async (data: any) => {
        return request<any>('/comparison/cohort', 'POST', data);
    },

    /**
     * Variance waterfall data
     */
    getVarianceWaterfall: async (metric: string) => {
        return request<any>(`/comparison/variance?metric=${metric}`, 'GET');
    }
};

// ============================================================================
// VISUALIZATIONS 2.0 API
// ============================================================================

export const visualizationApi = {
    /**
     * Recommend best chart type
     */
    recommendChart: async (dataSummary: any, intent?: string) => {
        return request<any>('/visualizations/recommend', 'POST', { data_summary: dataSummary, intent });
    },

    /**
     * Get processed visualization data
     */
    getVisualizationData: async (data: any) => {
        return request<any>('/visualizations/data', 'POST', data);
    },

    /**
     * Get system color palettes
     */
    getPalettes: async () => {
        return request<any[]>('/visualizations/palettes', 'GET');
    },

    /**
     * Get Sankey flow data
     */
    getSankeyData: async (data: any) => {
        return request<any>('/visualizations/sankey', 'POST', data);
    }
};
