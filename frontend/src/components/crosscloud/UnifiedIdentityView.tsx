'use client';

import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { User, Link as LinkIcon } from 'lucide-react';

const identities = [
    {
        id: 1,
        name: 'jane.doe@company.com',
        role: 'Cloud Architect',
        accounts: [
            { provider: 'AWS', id: 'arn:aws:iam::123:user/jane', active: true },
            { provider: 'GCP', id: 'jane@company.com', active: true },
            { provider: 'Azure', id: 'jane.doe@company.onmicrosoft.com', active: true },
        ]
    },
    {
        id: 2,
        name: 'svc-terraform-runner',
        role: 'CI/CD Service',
        accounts: [
            { provider: 'AWS', id: 'arn:aws:iam::123:role/tf-runner', active: true },
            { provider: 'GCP', id: 'tf-sa@project.iam.gserviceaccount.com', active: true },
            { provider: 'Azure', id: 'app-reg-tf-runner', active: false },
        ]
    }
];

export function UnifiedIdentityView() {
    return (
        <Card className="h-full">
            <CardHeader>
                <CardTitle>Unified Identity Map</CardTitle>
            </CardHeader>
            <CardContent className="p-0">
                <div className="divide-y divide-neutral-100">
                    {identities.map((identity) => (
                        <div key={identity.id} className="p-6">
                            <div className="flex items-center space-x-3 mb-4">
                                <div className="w-10 h-10 rounded-full bg-google-blue/10 flex items-center justify-center text-google-blue">
                                    <User size={20} />
                                </div>
                                <div>
                                    <h4 className="text-sm font-bold text-surface-dark">{identity.name}</h4>
                                    <p className="text-xs text-neutral-500">{identity.role}</p>
                                </div>
                            </div>

                            <div className="space-y-3 pl-13">
                                {identity.accounts.map((acc) => (
                                    <div key={acc.provider} className="flex items-center justify-between p-3 bg-neutral-50 rounded-lg border border-neutral-100">
                                        <div className="flex items-center space-x-3">
                                            <Badge variant="neutral" className="w-16 justify-center">{acc.provider}</Badge>
                                            <span className="text-xs font-mono text-neutral-600 truncate max-w-[200px]">{acc.id}</span>
                                        </div>
                                        <div className="flex items-center space-x-2">
                                            <LinkIcon size={14} className="text-neutral-400" />
                                            <span className={`w-2 h-2 rounded-full ${acc.active ? 'bg-green-500' : 'bg-neutral-300'}`}></span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    ))}
                </div>
            </CardContent>
        </Card>
    );
}
