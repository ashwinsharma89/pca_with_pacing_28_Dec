'use client';

import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { User } from '@/types';
import { api } from '@/lib/api';

interface AuthContextType {
    user: User | null;
    token: string | null;
    isLoading: boolean;
    sessionExpired: boolean;
    login: (token: string, user: User) => void;
    logout: () => void;
    clearSessionExpired: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Decode JWT to get expiration time
function decodeToken(token: string): { exp?: number } | null {
    try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(
            atob(base64)
                .split('')
                .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
                .join('')
        );
        return JSON.parse(jsonPayload);
    } catch (error) {
        console.error('Failed to decode token:', error);
        return null;
    }
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [token, setToken] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [sessionExpired, setSessionExpired] = useState(false);
    const router = useRouter();

    const logout = useCallback(() => {
        setToken(null);
        setUser(null);
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        localStorage.removeItem('tokenExpiry');
    }, []);

    const login = useCallback((newToken: string, newUser: User) => {
        setToken(newToken);
        setUser(newUser);
        setSessionExpired(false);
        localStorage.setItem('token', newToken);
        localStorage.setItem('user', JSON.stringify(newUser));

        // Store token expiry time
        const decoded = decodeToken(newToken);
        if (decoded?.exp) {
            localStorage.setItem('tokenExpiry', decoded.exp.toString());
        }
    }, []);

    const clearSessionExpired = useCallback(() => {
        setSessionExpired(false);
    }, []);

    // Check token expiration on mount and periodically
    useEffect(() => {
        const checkTokenExpiration = () => {
            const storedToken = localStorage.getItem('token');
            const storedExpiry = localStorage.getItem('tokenExpiry');

            if (storedToken && storedExpiry) {
                const expiryTime = parseInt(storedExpiry, 10) * 1000; // Convert to milliseconds
                const now = Date.now();
                const timeUntilExpiry = expiryTime - now;

                // If token expires in less than 5 minutes or already expired
                if (timeUntilExpiry < 5 * 60 * 1000) {
                    if (timeUntilExpiry < 0) {
                        // Token already expired
                        console.log('Token expired, logging out...');
                        setSessionExpired(true);
                        logout();
                        router.push('/login');
                    } else {
                        // Token expiring soon - could implement refresh here
                        console.log(`Token expiring in ${Math.floor(timeUntilExpiry / 1000 / 60)} minutes`);
                    }
                }
            }
        };

        // Check on mount
        const storedToken = localStorage.getItem('token');
        const storedUser = localStorage.getItem('user');

        if (storedToken && storedUser) {
            const decoded = decodeToken(storedToken);
            if (decoded?.exp) {
                const expiryTime = decoded.exp * 1000;
                const now = Date.now();

                if (expiryTime > now) {
                    // Token still valid
                    setToken(storedToken);
                    setUser(JSON.parse(storedUser));
                    localStorage.setItem('tokenExpiry', decoded.exp.toString());
                } else {
                    // Token expired
                    setSessionExpired(true);
                    logout();
                }
            } else {
                setToken(storedToken);
                setUser(JSON.parse(storedUser));
            }
        }
        setIsLoading(false);

        // Check every minute
        const interval = setInterval(checkTokenExpiration, 60 * 1000);

        return () => clearInterval(interval);
    }, [logout, router]);

    // Intercept API errors for 401 Unauthorized
    useEffect(() => {
        const handleUnauthorized = (event: CustomEvent) => {
            console.log('Unauthorized access detected');
            setSessionExpired(true);
            logout();
            router.push('/login');
        };

        window.addEventListener('unauthorized' as any, handleUnauthorized);

        // Redirect if not logged in and not on login page
        const handleInitialRedirect = () => {
            if (!isLoading && !token && window.location.pathname !== '/login') {
                router.push('/login');
            }
        };

        handleInitialRedirect();

        return () => {
            window.removeEventListener('unauthorized' as any, handleUnauthorized);
        };
    }, [logout, router, isLoading, token]);

    return (
        <AuthContext.Provider value={{ user, token, isLoading, sessionExpired, login, logout, clearSessionExpired }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}
