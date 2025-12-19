"use client";

import { AuthProvider } from "@/context/AuthContext";
import { ThemeProvider } from "@/context/ThemeContext";

import { SessionExpiredToast } from "@/components/SessionExpiredToast";
import { Toaster } from "@/components/ui/toaster";

import { AnalysisProvider } from "@/context/AnalysisContext";

export function Providers({ children }: { children: React.ReactNode }) {
    return (
        <ThemeProvider>
            <AuthProvider>
                <AnalysisProvider>
                    <SessionExpiredToast />
                    {children}
                    <Toaster />
                </AnalysisProvider>
            </AuthProvider>
        </ThemeProvider>
    );
}
