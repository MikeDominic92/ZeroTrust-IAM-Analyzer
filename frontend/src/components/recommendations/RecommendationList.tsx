'use client';

import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Check, X, ArrowRight } from 'lucide-react';

const recommendations = [
    {
        id: 1,
        identity: 'svc-data-processor',
        description: 'Remove unused S3 write permissions',
        impact: 'Low',
        confidence: 'High',
        diff: [
            { type: 'keep', text: 's3:GetObject' },
            { type: 'keep', text: 's3:ListBucket' },
            { type: 'remove', text: 's3:PutObject' },
            { type: 'remove', text: 's3:DeleteObject' },
        ]
    },
    {
        id: 2,
        identity: 'dev-team-role',
        description: 'Restrict EC2 full access to specific regions',
        impact: 'Medium',
        confidence: 'Medium',
        diff: [
            { type: 'add', text: 'Condition: { "aws:RequestedRegion": "us-east-1" }' },
            { type: 'keep', text: 'ec2:RunInstances' },
            { type: 'keep', text: 'ec2:TerminateInstances' },
        ]
    }
];

export function RecommendationList() {
    return (
        <div className="space-y-6">
            {recommendations.map((rec) => (
                <Card key={rec.id} className="overflow-hidden">
                    <CardHeader className="bg-neutral-50/50 border-b border-neutral-100 flex flex-row items-center justify-between">
                        <div>
                            <div className="flex items-center space-x-3 mb-1">
                                <CardTitle className="text-base">{rec.identity}</CardTitle>
                                <Badge variant={rec.impact === 'High' ? 'danger' : rec.impact === 'Medium' ? 'warning' : 'success'}>
                                    {rec.impact} Impact
                                </Badge>
                            </div>
                            <p className="text-sm text-neutral-500">{rec.description}</p>
                        </div>
                        <Button size="sm">
                            Apply Fix <ArrowRight className="w-4 h-4 ml-2" />
                        </Button>
                    </CardHeader>
                    <CardContent className="p-0">
                        <div className="bg-surface-dark text-neutral-300 font-mono text-sm p-4 overflow-x-auto">
                            {rec.diff.map((line, i) => (
                                <div key={i} className={`flex items-center ${line.type === 'remove' ? 'bg-red-900/20 text-red-400' : line.type === 'add' ? 'bg-green-900/20 text-green-400' : ''}`}>
                                    <span className="w-6 text-center select-none opacity-50">
                                        {line.type === 'remove' ? '-' : line.type === 'add' ? '+' : ' '}
                                    </span>
                                    <span>{line.text}</span>
                                </div>
                            ))}
                        </div>
                    </CardContent>
                </Card>
            ))}
        </div>
    );
}
