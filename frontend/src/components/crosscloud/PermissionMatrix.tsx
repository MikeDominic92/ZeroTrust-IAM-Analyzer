'use client';

import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Check, X, Minus } from 'lucide-react';

const matrix = [
    { service: 'Compute', aws: true, gcp: true, azure: true },
    { service: 'Storage', aws: true, gcp: true, azure: true },
    { service: 'Database', aws: true, gcp: false, azure: true },
    { service: 'AI/ML', aws: true, gcp: true, azure: false },
    { service: 'Serverless', aws: true, gcp: true, azure: true },
    { service: 'Containers', aws: true, gcp: true, azure: true },
];

export function PermissionMatrix() {
    return (
        <Card className="h-full">
            <CardHeader>
                <CardTitle>Cross-Cloud Capabilities</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="overflow-x-auto">
                    <table className="w-full text-sm text-left">
                        <thead className="text-xs text-neutral-500 uppercase bg-neutral-50">
                            <tr>
                                <th className="px-6 py-3">Service Domain</th>
                                <th className="px-6 py-3 text-center">AWS</th>
                                <th className="px-6 py-3 text-center">GCP</th>
                                <th className="px-6 py-3 text-center">Azure</th>
                            </tr>
                        </thead>
                        <tbody>
                            {matrix.map((row) => (
                                <tr key={row.service} className="bg-white border-b hover:bg-neutral-50">
                                    <td className="px-6 py-4 font-medium text-surface-dark">{row.service}</td>
                                    <td className="px-6 py-4 text-center">
                                        <div className="flex justify-center">
                                            {row.aws ? <Check className="text-green-500 w-5 h-5" /> : <X className="text-red-500 w-5 h-5" />}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 text-center">
                                        <div className="flex justify-center">
                                            {row.gcp ? <Check className="text-green-500 w-5 h-5" /> : <X className="text-red-500 w-5 h-5" />}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 text-center">
                                        <div className="flex justify-center">
                                            {row.azure ? <Check className="text-green-500 w-5 h-5" /> : <X className="text-red-500 w-5 h-5" />}
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </CardContent>
        </Card>
    );
}
