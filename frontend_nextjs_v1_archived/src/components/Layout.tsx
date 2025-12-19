import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
    LayoutDashboard,
    BarChart2,
    MessageSquare,
    Settings,
    LogOut
} from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import clsx from 'clsx';

interface LayoutProps {
    children: React.ReactNode;
}

const NavItem = ({ href, icon: Icon, label, active }: { href: string, icon: any, label: string, active: boolean }) => (
    <Link
        href={href}
        className={clsx(
            "flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group",
            active
                ? "bg-blue-600/10 text-blue-400 border border-blue-500/20 shadow-[0_0_20px_rgba(59,130,246,0.15)]"
                : "text-slate-400 hover:text-slate-100 hover:bg-slate-800/50"
        )}
    >
        <Icon size={20} className={clsx(active ? "text-blue-400" : "text-slate-500 group-hover:text-slate-300")} />
        <span className="font-medium text-sm tracking-wide">{label}</span>
    </Link>
);

export default function Layout({ children }: LayoutProps) {
    const pathname = usePathname();
    const { logout } = useAuth();

    return (
        <div className="flex h-screen bg-[#0f172a] text-slate-100 font-sans selection:bg-blue-500/30 overflow-hidden">
            {/* Sidebar */}
            <aside className="w-72 flex-shrink-0 border-r border-slate-800/60 bg-[#0f172a]/50 backdrop-blur-xl flex flex-col p-6 z-20 relative">
                <div className="mb-10 px-2">
                    <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent tracking-tight">
                        PCA Agent
                    </h1>
                    <p className="text-xs text-slate-500 font-medium mt-1 tracking-wider uppercase">Enterprise Analytics</p>
                </div>

                <nav className="flex-1 space-y-2">
                    <NavItem href="/" icon={LayoutDashboard} label="Overview" active={pathname === '/'} />
                    <NavItem href="/analysis" icon={BarChart2} label="Deep Dive" active={pathname === '/analysis'} />
                    <NavItem href="/chat" icon={MessageSquare} label="AI Assistant" active={pathname === '/chat'} />
                    <NavItem href="/settings" icon={Settings} label="Settings" active={pathname === '/settings'} />
                </nav>

                <div className="pt-6 border-t border-slate-800/60">
                    <button
                        onClick={logout}
                        className="flex items-center gap-3 px-4 py-3 w-full rounded-xl text-slate-400 hover:text-red-400 hover:bg-red-500/10 transition-all duration-200"
                    >
                        <LogOut size={20} />
                        <span className="font-medium text-sm">Sign Out</span>
                    </button>
                </div>

                {/* Background glow effect */}
                <div className="absolute top-0 left-0 w-full h-96 bg-blue-500/5 rounded-full blur-3xl pointer-events-none -translate-y-1/2 -translate-x-1/2"></div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 overflow-y-auto relative scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-transparent">
                <div className="max-w-7xl mx-auto p-8 lg:p-12 relative z-10">
                    {children}
                </div>

                {/* Background ambient lighting */}
                <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-purple-500/5 rounded-full blur-[100px] pointer-events-none select-none"></div>
                <div className="absolute bottom-0 left-20 w-[300px] h-[300px] bg-blue-500/5 rounded-full blur-[80px] pointer-events-none select-none"></div>
            </main>
        </div>
    );
}
