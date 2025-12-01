'use client';

import React from 'react';
import { Search, Bell, HelpCircle } from 'lucide-react';

export function Header() {
    return (
        <header className="h-16 bg-surface border-b border-neutral-200 sticky top-0 z-20 px-8 flex items-center justify-between">
            {/* Search Bar */}
            <div className="w-96 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-neutral-400 w-4 h-4" />
                <input
                    type="text"
                    placeholder="Search resources, identities, or policies..."
                    className="w-full pl-10 pr-4 py-2 bg-neutral-50 border border-neutral-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-google-blue/20 focus:border-google-blue transition-all"
                />
            </div>

            {/* Right Actions */}
            <div className="flex items-center space-x-4">
                <button className="p-2 text-neutral-500 hover:bg-neutral-50 rounded-full transition-colors">
                    <HelpCircle className="w-5 h-5" />
                </button>
                <button className="p-2 text-neutral-500 hover:bg-neutral-50 rounded-full transition-colors relative">
                    <Bell className="w-5 h-5" />
                    <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-risk-high rounded-full border-2 border-surface"></span>
                </button>

                <div className="h-8 w-px bg-neutral-200 mx-2"></div>

                <button className="flex items-center space-x-3 hover:bg-neutral-50 p-1.5 rounded-lg transition-colors">
                    <div className="w-8 h-8 rounded-full bg-secondary text-white flex items-center justify-center text-sm font-medium">
                        JD
                    </div>
                    <div className="text-left hidden md:block">
                        <p className="text-sm font-medium text-surface-dark">Jane Doe</p>
                        <p className="text-xs text-neutral-500">Cloud Architect</p>
                    </div>
                </button>
            </div>
        </header>
    );
}
