'use client';

import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Check, X } from 'lucide-react';

const effectivePermissions = [
    { action: 'Read Data', status: 'allowed', source: 'Direct Policy' },
    { action: 'Write Data', status: 'denied', source: 'SCP Restriction' },
    { action: 'Delete Data', status: 'denied', source: 'Implicit Deny' },
    { action: 'Manage Access', status: 'allowed', source: 'Group Membership' },
];

export function EffectivePermissions() {
    return (
        <Card className="h-full">
            <CardHeader>
                <CardTitle>Effective Permissions</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="space-y-3">
                    {effectivePermissions.map((perm) => (
                        <div key={perm.action} className="flex items-center justify-between p-3 rounded-lg border border-neutral-100 bg-neutral-50/50">
                            <div className="flex items-center space-x-3">
                                <div className={`w-6 h-6 rounded-full flex items-center justify-center ${perm.status === 'allowed' ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'}`}>
                                    {perm.status === 'allowed' ? <Check size={14} /> : <X size={14} />}
                                </div>
                                <span className="text-sm font-medium text-surface-dark">{perm.action}</span>
                            </div>
                            <span className="text-xs text-neutral-500 bg-white px-2 py-1 rounded border border-neutral-200">
                                {perm.source}
                            </span>
                        </div>
                    ))}
                </div>
            </CardContent>
        </Card>
    );
}
