'use client';

import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { AlertTriangle, CheckCircle2 } from 'lucide-react';

export function ImpactAnalysis() {
    return (
        <Card className="h-full bg-neutral-50/50 border-dashed">
            <CardHeader>
                <CardTitle>Impact Analysis</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
                <div className="flex items-start space-x-3 p-3 bg-white rounded-lg border border-neutral-200 shadow-sm">
                    <CheckCircle2 className="w-5 h-5 text-green-500 mt-0.5" />
                    <div>
                        <p className="text-sm font-medium text-surface-dark">No Breaking Changes Detected</p>
                        <p className="text-xs text-neutral-500 mt-1">
                            Based on 90 days of CloudTrail logs, the permissions slated for removal have not been used.
                        </p>
                    </div>
                </div>

                <div className="flex items-start space-x-3 p-3 bg-white rounded-lg border border-neutral-200 shadow-sm">
                    <AlertTriangle className="w-5 h-5 text-orange-500 mt-0.5" />
                    <div>
                        <p className="text-sm font-medium text-surface-dark">Potential Dependency</p>
                        <p className="text-xs text-neutral-500 mt-1">
                            Service 'svc-backup' is in the same group. Verify if it relies on shared policies before applying.
                        </p>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
