'use client';

import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { AlertOctagon, ArrowRight } from 'lucide-react';

const remediations = [
    { id: 1, title: 'Revoke Admin Access', resource: 'dev-user-1', risk: 'Critical', time: '2h ago' },
    { id: 2, title: 'Fix S3 Public Access', resource: 'prod-logs-bucket', risk: 'High', time: '5h ago' },
    { id: 3, title: 'Rotate Access Keys', resource: 'svc-backup', risk: 'Medium', time: '1d ago' },
    { id: 4, title: 'Remove Unused Role', resource: 'legacy-deployer', risk: 'Low', time: '2d ago' },
];

export function RemediationQueue() {
    return (
        <Card className="h-full">
            <CardHeader>
                <CardTitle className="flex items-center justify-between">
                    <span>Remediation Queue</span>
                    <Badge variant="neutral">4 Pending</Badge>
                </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
                <div className="divide-y divide-neutral-100">
                    {remediations.map((item) => (
                        <div key={item.id} className="p-4 flex items-center justify-between hover:bg-neutral-50 transition-colors">
                            <div className="flex items-center space-x-3">
                                <AlertOctagon className={`w-5 h-5 ${item.risk === 'Critical' || item.risk === 'High' ? 'text-risk-high' : 'text-risk-medium'}`} />
                                <div>
                                    <p className="text-sm font-medium text-surface-dark">{item.title}</p>
                                    <p className="text-xs text-neutral-500">{item.resource} • {item.time}</p>
                                </div>
                            </div>
                            <Button size="sm" variant="outline" className="h-8">
                                Fix <ArrowRight className="w-3 h-3 ml-1" />
                            </Button>
                        </div>
                    ))}
                </div>
            </CardContent>
        </Card>
    );
}
