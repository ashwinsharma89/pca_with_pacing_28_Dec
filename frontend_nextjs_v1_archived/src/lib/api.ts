import axios, { AxiosInstance, AxiosResponse } from 'axios';

// Base API Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const apiClient: AxiosInstance = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Response Types (Generic)
export interface ApiResponse<T> {
    data: T;
    message?: string;
    status: string;
}

// Auth Types (Placeholder for now, based on your API)
export interface AuthResponse {
    access_token: string;
    token_type: string;
}

export const api = {
    // Health Check
    checkHealth: async (): Promise<any> => {
        const response = await apiClient.get('/health');
        return response.data;
    },

    // Example: Generic GET
    get: async <T>(url: string, params?: any): Promise<T> => {
        const response: AxiosResponse<T> = await apiClient.get(url, { params });
        return response.data;
    },

    // Example: Generic POST
    post: async <T>(url: string, data: any): Promise<T> => {
        const response: AxiosResponse<T> = await apiClient.post(url, data);
        return response.data;
    },
};

export default apiClient;
