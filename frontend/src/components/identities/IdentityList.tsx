'use client';

import React from 'react';
import { Card, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Search, Filter, User, Bot, MoreVertical } from 'lucide-react';

const identities = [
    { id: 1, name: 'jane.doe@company.com', type: 'User', cloud: 'AWS', risk: 'Low', lastActive: '2m ago' },
    { id: 2, name: 'svc-build-deploy', type: 'Service', cloud: 'GCP', risk: 'High', lastActive: '1h ago' },
    { id: 3, name: 'admin-backup-role', type: 'Role', cloud: 'Azure', risk: 'Medium', lastActive: '5d ago' },
    { id: 4, name: 'john.smith@company.com', type: 'User', cloud: 'AWS', risk: 'Low', lastActive: '1d ago' },
    { id: 5, name: 'terraform-runner', type: 'Service', cloud: 'AWS', risk: 'Critical', lastActive: 'Just now' },
];

export function IdentityList() {
    return (
        <Card className="h-full flex flex-col">
            <div className="p-4 border-b border-neutral-100 flex items-center space-x-4">
                <div className="flex-1 relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-neutral-400 w-4 h-4" />
                    <input
                        type="text"
                        placeholder="Search identities..."
                        className="w-full pl-10 pr-4 py-2 bg-neutral-50 border border-neutral-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-google-blue/20 focus:border-google-blue"
                    />
                </div>
                <Button variant="outline" size="sm">
                    <Filter className="w-4 h-4 mr-2" />
                    Filters
                </Button>
            </div>
            <CardContent className="p-0 flex-1 overflow-y-auto">
                <div className="divide-y divide-neutral-100">
                    {identities.map((identity) => (
                        <div key={identity.id} className="p-4 flex items-center justify-between hover:bg-neutral-50 transition-colors cursor-pointer group">
                            <div className="flex items-center space-x-3">
                                <div className={`w-10 h-10 rounded-full flex items-center justify-center ${identity.type === 'User' ? 'bg-blue-50 text-blue-600' : 'bg-purple-50 text-purple-600'}`}>
                                    {identity.type === 'User' ? <User size={20} /> : <Bot size={20} />}
                                </div>
                                <div>
                                    <p className="text-sm font-medium text-surface-dark">{identity.name}</p>
                                    <div className="flex items-center space-x-2 mt-0.5">
                                        <Badge variant="neutral" className="text-[10px] px-1.5 py-0">{identity.cloud}</Badge>
                                        <span className="text-xs text-neutral-500">• {identity.lastActive}</span>
                                    </div>
                                </div>
                            </div>
                            <div className="flex items-center space-x-4">
                                <Badge variant={identity.risk === 'Critical' || identity.risk === 'High' ? 'danger' : identity.risk === 'Medium' ? 'warning' : 'success'}>
                                    {identity.risk}
                                </Badge>
                                <button className="text-neutral-400 hover:text-surface-dark">
                                    <MoreVertical size={16} />
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            </CardContent>
        </Card>
    );
}
