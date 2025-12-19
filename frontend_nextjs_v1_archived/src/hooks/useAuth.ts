import { useState, useEffect } from 'react';
import { api, AuthResponse } from '../lib/api';

interface User {
    username: string;
}

export const useAuth = () => {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Check for existing token
        const token = localStorage.getItem('token');
        if (token) {
            // Validate token or just set state (simplifying for now)
            // In a real app, you'd verify the token with an endpoint like /users/me
            setUser({ username: 'User' });
        }
        setLoading(false);
    }, []);

    const login = async (formData: FormData) => {
        try {
            // The API expects form-data for OAuth2 usually, or JSON depending on implementation
            // Adapting to common FastAPI security usage (OAuth2PasswordRequestForm usually takes form data)
            const response = await api.post<AuthResponse>('/token', formData);
            const { access_token } = response;

            localStorage.setItem('token', access_token);
            setUser({ username: 'User' });
            return true;
        } catch (error) {
            console.error('Login failed', error);
            return false;
        }
    };

    const logout = () => {
        localStorage.removeItem('token');
        setUser(null);
    };

    return {
        user,
        loading,
        login,
        logout,
    };
};
