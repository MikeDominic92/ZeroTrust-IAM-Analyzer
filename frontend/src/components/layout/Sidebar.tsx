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
        <aside className="w-64 h-screen bg-surface border-r border-neutral-200 fixed left-0 top-0 flex flex-col z-30">
            {/* Logo */}
            <div className="h-16 flex items-center px-6 border-b border-neutral-100">
                <div className="w-8 h-8 bg-google-blue rounded-lg flex items-center justify-center mr-3">
                    <ShieldAlert className="text-white w-5 h-5" />
                </div>
                <span className="font-poppins font-semibold text-surface-dark text-lg tracking-tight">
                    IAM Analyzer
                </span>
            </div>

            {/* Navigation */}
            <nav className="flex-1 py-6 px-3 space-y-1">
                {navItems.map((item) => {
                    const isActive = pathname === item.href;
                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={cn(
                                "flex items-center px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
                                isActive
                                    ? "bg-google-blue/10 text-google-blue"
                                    : "text-neutral-600 hover:bg-neutral-50 hover:text-surface-dark"
                            )}
                        >
                            <item.icon className={cn("w-5 h-5 mr-3", isActive ? "text-google-blue" : "text-neutral-400")} />
                            {item.name}
                        </Link>
                    );
                })}
            </nav>

            {/* Footer */}
            <div className="p-4 border-t border-neutral-100">
                <button className="flex items-center w-full px-3 py-2 text-sm font-medium text-neutral-600 hover:text-surface-dark hover:bg-neutral-50 rounded-lg transition-colors">
                    <Settings className="w-5 h-5 mr-3 text-neutral-400" />
                    Settings
                </button>
                <button className="flex items-center w-full px-3 py-2 mt-1 text-sm font-medium text-risk-high hover:bg-risk-high/5 rounded-lg transition-colors">
                    <LogOut className="w-5 h-5 mr-3" />
                    Sign Out
                </button>
            </div>
        </aside>
    );
}
