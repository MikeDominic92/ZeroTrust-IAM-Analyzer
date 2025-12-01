'use client';

import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Check, Clock, User } from 'lucide-react';

const steps = [
    { id: 1, title: 'Request Generated', status: 'completed', time: '10:00 AM', user: 'System' },
    { id: 2, title: 'Security Review', status: 'completed', time: '10:15 AM', user: 'Jane Doe' },
    { id: 3, title: 'Owner Approval', status: 'current', time: 'Pending', user: 'DevOps Lead' },
    { id: 4, title: 'Implementation', status: 'pending', time: '-', user: 'Terraform' },
];

export function ApprovalWorkflow() {
    return (
        <Card className="h-full">
            <CardHeader>
                <CardTitle>Approval Pipeline</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="relative pl-6 border-l-2 border-neutral-200 space-y-8">
                    {steps.map((step) => (
                        <div key={step.id} className="relative">
                            <div className={`absolute -left-[31px] w-8 h-8 rounded-full border-4 border-white flex items-center justify-center ${step.status === 'completed' ? 'bg-green-500 text-white' : step.status === 'current' ? 'bg-blue-500 text-white' : 'bg-neutral-200 text-neutral-400'}`}>
                                {step.status === 'completed' ? <Check size={14} /> : step.status === 'current' ? <Clock size={14} /> : <span className="w-2 h-2 bg-neutral-400 rounded-full" />}
                            </div>
                            <div>
                                <p className={`text-sm font-bold ${step.status === 'pending' ? 'text-neutral-400' : 'text-surface-dark'}`}>{step.title}</p>
                                <div className="flex items-center space-x-2 mt-1">
                                    <User size={12} className="text-neutral-400" />
                                    <span className="text-xs text-neutral-500">{step.user}</span>
                                    <span className="text-xs text-neutral-300">•</span>
                                    <span className="text-xs text-neutral-500">{step.time}</span>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </CardContent>
        </Card>
    );
}
