'use client';

import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { AlertTriangle, User } from 'lucide-react';

const riskyIdentities = [
    { id: 1, name: 'svc-jenkins-build', type: 'Service', risk: 92, issues: 14 },
    { id: 2, name: 'david.miller@corp', type: 'User', risk: 88, issues: 8 },
    { id: 3, name: 'lambda-processor-prod', type: 'Service', risk: 85, issues: 11 },
    { id: 4, name: 'sarah.connor@corp', type: 'User', risk: 76, issues: 5 },
    { id: 5, name: 'backup-admin-role', type: 'Role', risk: 72, issues: 3 },
];

export function TopRiskyIdentities() {
    return (
        <Card className="h-full">
            <CardHeader>
                <CardTitle className="flex items-center justify-between">
                    <span>Top 5 Riskiest Identities</span>
                    <Badge variant="danger">Critical Attention</Badge>
                </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
                <div className="divide-y divide-neutral-100">
                    {riskyIdentities.map((identity) => (
                        <div key={identity.id} className="p-4 flex items-center justify-between hover:bg-neutral-50 transition-colors cursor-pointer group">
                            <div className="flex items-center space-x-3">
                                <div className="w-10 h-10 rounded-full bg-neutral-100 flex items-center justify-center text-neutral-500 group-hover:bg-white group-hover:shadow-sm transition-all">
                                    <User size={20} />
                                </div>
                                <div>
                                    <p className="text-sm font-medium text-surface-dark">{identity.name}</p>
                                    <p className="text-xs text-neutral-500">{identity.type} • {identity.issues} Issues</p>
                                </div>
                            </div>
                            <div className="flex flex-col items-end">
                                <span className="text-sm font-bold text-risk-high">{identity.risk}</span>
                                <div className="w-24 h-1.5 bg-neutral-100 rounded-full mt-1 overflow-hidden">
                                    <div className="h-full bg-risk-high rounded-full" style={{ width: `${identity.risk}%` }}></div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </CardContent>
        </Card>
    );
}
