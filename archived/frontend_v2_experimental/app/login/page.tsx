"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Brain, Lock, User, Mail, ShieldCheck, ArrowRight } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useAuth } from "@/context/AuthContext";
import { api } from "@/lib/api";
import { toast } from "sonner";

export default function LoginPage() {
    const [isLoading, setIsLoading] = useState(false);
    const { login } = useAuth();
    const router = useRouter();

    const handleLogin = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setIsLoading(true);

        const formData = new FormData(e.currentTarget);
        const username = formData.get("username") as string;
        const password = formData.get("password") as string;

        try {
            const response = await api.login({ username, password });
            login(response.access_token, response.user);
            toast.success("Welcome back!", {
                description: `Logged in as ${response.user.username}`
            });
            router.push("/");
        } catch (error: any) {
            toast.error("Login failed", {
                description: error.message || "Invalid credentials"
            });
        } finally {
            setIsLoading(false);
        }
    };

    const handleRegister = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setIsLoading(true);

        const formData = new FormData(e.currentTarget);
        const username = formData.get("username") as string;
        const email = formData.get("email") as string;
        const password = formData.get("password") as string;

        try {
            await api.register({ username, email, password });
            toast.success("Account created successfully!", {
                description: "You can now log in with your credentials."
            });
            // Switch to login tab - in a real app we might auto-login or set state
        } catch (error: any) {
            toast.error("Registration failed", {
                description: error.message || "Could not create account"
            });
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center p-6 bg-[grid-slate-200] dark:bg-slate-950">
            {/* Animated Background Gradients */}
            <div className="absolute inset-0 overflow-hidden -z-10">
                <div className="absolute -top-[10%] -left-[10%] w-[40%] h-[40%] bg-purple-500/20 blur-[120px] rounded-full animate-pulse" />
                <div className="absolute -bottom-[10%] -right-[10%] w-[40%] h-[40%] bg-indigo-500/20 blur-[120px] rounded-full animate-pulse [animation-delay:2s]" />
            </div>

            <div className="w-full max-w-md space-y-8">
                {/* Logo & Header */}
                <div className="text-center space-y-2">
                    <div className="inline-flex p-3 bg-gradient-to-br from-purple-600 to-indigo-600 rounded-2xl shadow-xl shadow-indigo-500/20 border border-white/10 mb-4 animate-bounce-slow">
                        <Brain className="h-8 w-8 text-white" />
                    </div>
                    <h1 className="text-4xl font-extrabold tracking-tight bg-gradient-to-r from-slate-900 to-slate-700 dark:from-white dark:to-slate-400 bg-clip-text text-transparent">
                        PCA Agent V2
                    </h1>
                    <p className="text-slate-500 dark:text-slate-400">
                        Advanced Marketing Analytics Intelligence
                    </p>
                </div>

                <Card className="border-white/10 bg-white/70 dark:bg-slate-900/70 backdrop-blur-xl shadow-2xl">
                    <CardHeader className="space-y-1">
                        <CardTitle className="text-2xl font-bold text-center">Authentication</CardTitle>
                        <CardDescription className="text-center">
                            Enter your credentials to access the platform
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <Tabs defaultValue="login" className="space-y-6">
                            <TabsList className="grid w-full grid-cols-2 bg-slate-200/50 dark:bg-slate-800/50">
                                <TabsTrigger value="login">Login</TabsTrigger>
                                <TabsTrigger value="register">Register</TabsTrigger>
                            </TabsList>

                            <TabsContent value="login">
                                <form onSubmit={handleLogin} className="space-y-4">
                                    <div className="space-y-2">
                                        <Label htmlFor="login-username">Username</Label>
                                        <div className="relative">
                                            <User className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
                                            <Input
                                                id="login-username"
                                                name="username"
                                                placeholder="admin"
                                                className="pl-10 bg-white/50 dark:bg-slate-800/50 border-white/10"
                                                required
                                            />
                                        </div>
                                    </div>
                                    <div className="space-y-2">
                                        <Label htmlFor="login-password">Password</Label>
                                        <div className="relative">
                                            <Lock className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
                                            <Input
                                                id="login-password"
                                                name="password"
                                                type="password"
                                                placeholder="••••••••"
                                                className="pl-10 bg-white/50 dark:bg-slate-800/50 border-white/10"
                                                required
                                            />
                                        </div>
                                    </div>
                                    <Button className="w-full bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white transition-all duration-300" disabled={isLoading}>
                                        {isLoading ? "Signing in..." : "Sign In"}
                                        {!isLoading && <ArrowRight className="ml-2 h-4 w-4" />}
                                    </Button>
                                </form>
                            </TabsContent>

                            <TabsContent value="register">
                                <form onSubmit={handleRegister} className="space-y-4">
                                    <div className="space-y-2">
                                        <Label htmlFor="reg-username">Username</Label>
                                        <div className="relative">
                                            <User className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
                                            <Input
                                                id="reg-username"
                                                name="username"
                                                placeholder="yourname"
                                                className="pl-10 bg-white/50 dark:bg-slate-800/50 border-white/10"
                                                required
                                            />
                                        </div>
                                    </div>
                                    <div className="space-y-2">
                                        <Label htmlFor="reg-email">Email</Label>
                                        <div className="relative">
                                            <Mail className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
                                            <Input
                                                id="reg-email"
                                                name="email"
                                                type="email"
                                                placeholder="name@example.com"
                                                className="pl-10 bg-white/50 dark:bg-slate-800/50 border-white/10"
                                                required
                                            />
                                        </div>
                                    </div>
                                    <div className="space-y-2">
                                        <Label htmlFor="reg-password">Password</Label>
                                        <div className="relative">
                                            <Lock className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
                                            <Input
                                                id="reg-password"
                                                name="password"
                                                type="password"
                                                placeholder="••••••••"
                                                className="pl-10 bg-white/50 dark:bg-slate-800/50 border-white/10"
                                                required
                                            />
                                        </div>
                                    </div>
                                    <Button className="w-full bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white transition-all duration-300" variant="outline" disabled={isLoading}>
                                        {isLoading ? "Creating Account..." : "Create Account"}
                                        {!isLoading && <ArrowRight className="ml-2 h-4 w-4" />}
                                    </Button>
                                </form>
                            </TabsContent>
                        </Tabs>

                        <div className="mt-8 pt-6 border-t border-slate-100 dark:border-slate-800 flex items-center justify-center gap-2 text-xs text-slate-500">
                            <ShieldCheck className="h-3 w-3" />
                            <span>Enterprise Grade Security</span>
                        </div>
                    </CardContent>
                </Card>

                <p className="text-center text-xs text-slate-500">
                    &copy; 2025 PCA Agent Platform. All rights reserved.
                </p>
            </div>

            <style jsx global>{`
                @keyframes bounce-slow {
                    0%, 100% { transform: translateY(-5%); animation-timing-function: cubic-bezier(0.8,0,1,1); }
                    50% { transform: none; animation-timing-function: cubic-bezier(0,0,0.2,1); }
                }
                .animate-bounce-slow {
                    animation: bounce-slow 3s infinite;
                }
            `}</style>
        </div>
    );
}
