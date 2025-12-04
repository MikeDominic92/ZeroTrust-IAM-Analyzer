'use client';

import React from 'react';
import { Search, Bell, HelpCircle } from 'lucide-react';
import { IdentityBadge } from '../ui/IdentityBadge';

export function Header() {
    return (
        <header className="h-20 glass-panel border-b-0 sticky top-0 z-20 px-8 flex items-center justify-between m-4 rounded-2xl">
            {/* Search Bar */}
            <div className="w-96 relative group">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-cyber-cyan/50 w-4 h-4 group-focus-within:text-cyber-cyan transition-colors" />
                <input
                    type="text"
                    placeholder="Search resources, identities, or policies..."
                    className="w-full pl-10 pr-4 py-2 bg-black/20 border border-white/10 rounded-xl text-sm text-white placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-cyber-cyan/50 focus:border-cyber-cyan/50 transition-all backdrop-blur-sm"
                />
            </div>

            {/* Right Actions */}
            <div className="flex items-center space-x-6">
                <button className="p-2 text-gray-400 hover:text-cyber-cyan hover:bg-white/5 rounded-full transition-all duration-300">
                    <HelpCircle className="w-5 h-5" />
                </button>
                <button className="p-2 text-gray-400 hover:text-cyber-cyan hover:bg-white/5 rounded-full transition-all duration-300 relative group">
                    <Bell className="w-5 h-5 group-hover:animate-pulse" />
                    <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-cyber-purple rounded-full shadow-[0_0_8px_#7c3aed]"></span>
                </button>

                <div className="h-8 w-px bg-white/10 mx-2"></div>

                <IdentityBadge />
            </div>
        </header>
    );
}

