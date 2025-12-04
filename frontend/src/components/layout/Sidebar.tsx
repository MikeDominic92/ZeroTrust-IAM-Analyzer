'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import {
    LayoutDashboard,
    Search,
    ShieldAlert,
    CheckSquare,
    Globe,
    Settings,
    LogOut
} from 'lucide-react';

const navItems = [
    { name: 'Dashboard', href: '/', icon: LayoutDashboard },
    { name: 'Identity Explorer', href: '/identities', icon: Search },
    { name: 'Risk Analysis', href: '/risk', icon: ShieldAlert },
    { name: 'Recommendations', href: '/recommendations', icon: CheckSquare },
    { name: 'Cross-Cloud', href: '/cross-cloud', icon: Globe },
];

export function Sidebar() {
    const pathname = usePathname();

    return (
        <aside className="w-64 h-[calc(100vh-2rem)] glass-panel fixed left-4 top-4 flex flex-col z-30 rounded-2xl border-r-0">
            {/* Logo */}
            <div className="h-20 flex items-center px-6 border-b border-white/10">
                <div className="w-10 h-10 bg-gradient-to-tr from-cyber-cyan to-cyber-purple rounded-lg flex items-center justify-center mr-3 shadow-[0_0_10px_rgba(6,182,212,0.5)]">
                    <ShieldAlert className="text-white w-6 h-6" />
                </div>
                <span className="font-orbitron font-bold text-white text-lg tracking-wider neon-text-cyan">
                    IAM ANALYZER
                </span>
            </div>

            {/* Navigation */}
            <nav className="flex-1 py-6 px-3 space-y-2">
                {navItems.map((item) => {
                    const isActive = pathname === item.href;
                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={cn(
                                "flex items-center px-3 py-3 rounded-xl text-sm font-medium transition-all duration-300",
                                isActive
                                    ? "bg-cyber-cyan/10 text-cyber-cyan border border-cyber-cyan/20 shadow-[0_0_10px_rgba(6,182,212,0.1)]"
                                    : "text-gray-400 hover:bg-white/5 hover:text-white hover:pl-4"
                            )}
                        >
                            <item.icon className={cn("w-5 h-5 mr-3 transition-colors", isActive ? "text-cyber-cyan" : "text-gray-500 group-hover:text-white")} />
                            {item.name}
                        </Link>
                    );
                })}
            </nav>

            {/* Footer */}
            <div className="p-4 border-t border-white/10">
                <button className="flex items-center w-full px-3 py-2 text-sm font-medium text-gray-400 hover:text-white hover:bg-white/5 rounded-lg transition-colors">
                    <Settings className="w-5 h-5 mr-3 text-gray-500" />
                    Settings
                </button>
                <button className="flex items-center w-full px-3 py-2 mt-1 text-sm font-medium text-red-400 hover:bg-red-500/10 hover:text-red-300 rounded-lg transition-colors">
                    <LogOut className="w-5 h-5 mr-3" />
                    Sign Out
                </button>
            </div>
        </aside>
    );
}

