"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
    Brain, AlertTriangle, Zap, LayoutDashboard,
    Scale, BarChart3, Upload, Home, LogOut, User as UserIcon
} from "lucide-react";
import { useAuth } from "@/context/AuthContext";

const navigation = [
    { name: "Home", href: "/", icon: Home },
    { name: "Intelligence Studio", href: "/intelligence-studio", icon: Brain },
    { name: "Anomaly Detective", href: "/anomaly-detective", icon: AlertTriangle },
    { name: "Real-Time Command", href: "/real-time-command", icon: Zap },
    { name: "Dashboard Builder 2", href: "/dashboard-builder-2", icon: LayoutDashboard },
    { name: "Comparison 2", href: "/comparison-2", icon: Scale },
    { name: "Visualizations 2", href: "/visualizations-2", icon: BarChart3 },
    { name: "Upload Data", href: "/upload", icon: Upload },
];

export function Navigation() {
    const pathname = usePathname();
    const { user, logout } = useAuth();

    return (
        <nav className="w-64 bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 h-screen fixed left-0 top-0 overflow-y-auto flex flex-col">
            <div className="p-6">
                <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent">
                    PCA Agent V2
                </h1>
                <p className="text-sm text-muted-foreground mt-1">Analytics Platform</p>
            </div>

            <div className="px-3 space-y-1 flex-1">
                {navigation.map((item) => {
                    const isActive = pathname === item.href;
                    const Icon = item.icon;

                    return (
                        <Link
                            key={item.name}
                            href={item.href}
                            className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${isActive
                                ? "bg-purple-100 dark:bg-purple-950 text-purple-900 dark:text-purple-100"
                                : "text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800"
                                }`}
                        >
                            <Icon className="h-5 w-5" />
                            <span className="text-sm font-medium">{item.name}</span>
                        </Link>
                    );
                })}
            </div>

            <div className="p-4 border-t border-slate-200 dark:border-slate-800 space-y-4">
                {user && (
                    <div className="flex items-center gap-3 px-3 py-2 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
                        <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-full">
                            <UserIcon className="h-4 w-4 text-purple-600" />
                        </div>
                        <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium truncate">{user.username}</p>
                            <p className="text-xs text-muted-foreground truncate uppercase">{user.role}</p>
                        </div>
                    </div>
                )}

                <button
                    onClick={logout}
                    className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-red-600 hover:bg-red-50 dark:hover:bg-red-950/30 transition-colors"
                >
                    <LogOut className="h-5 w-5" />
                    <span className="text-sm font-medium">Logout</span>
                </button>

                <p className="text-[10px] text-muted-foreground text-center">
                    V2.0.0 • 7 Pages
                </p>
            </div>
        </nav>
    );
}
