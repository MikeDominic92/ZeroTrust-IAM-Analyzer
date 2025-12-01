'use client';

import React from 'react';
import { Card, CardContent } from '@/components/ui/Card';
import { Cloud } from 'lucide-react';

const providers = [
    { name: 'AWS', score: 82, color: 'bg-[#FF9900]', trend: '+2%' },
    { name: 'GCP', score: 94, color: 'bg-[#4285F4]', trend: '+5%' },
    { name: 'Azure', score: 68, color: 'bg-[#0078D4]', trend: '-3%' },
];

export function CloudProviderBreakdown() {
    return (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {providers.map((provider) => (
                <Card key={provider.name} variant="elevated" className="border-l-4" style={{ borderLeftColor: provider.color.replace('bg-[', '').replace(']', '') }}>
                    <CardContent className="flex items-center justify-between p-4">
                        <div className="flex items-center space-x-3">
                            <div className={`p-2 rounded-lg ${provider.color} bg-opacity-10`}>
                                <Cloud className={`w-5 h-5 ${provider.color.replace('bg-', 'text-')}`} />
                            </div>
                            <div>
                                <p className="text-sm font-medium text-neutral-500">{provider.name}</p>
                                <h4 className="text-xl font-bold text-surface-dark">{provider.score}%</h4>
                            </div>
                        </div>
                        <span className={`text-xs font-medium px-2 py-1 rounded-full ${provider.trend.startsWith('+') ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                            {provider.trend}
                        </span>
                    </CardContent>
                </Card>
            ))}
        </div>
    );
}
