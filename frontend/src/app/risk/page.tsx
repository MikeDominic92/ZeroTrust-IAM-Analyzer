'use client';

import React from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { RiskMatrix } from '@/components/risk/RiskMatrix';
import { PrivilegeEscalationPath } from '@/components/risk/PrivilegeEscalationPath';
import { UnusedPermissionsChart } from '@/components/risk/UnusedPermissionsChart';
import { RemediationQueue } from '@/components/risk/RemediationQueue';
import { Button } from '@/components/ui/Button';
import { RefreshCw } from 'lucide-react';

export default function RiskAnalysis() {
    return (
        <DashboardLayout>
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="text-2xl font-bold text-surface-dark">Entitlement Risk Analysis</h1>
                    <p className="text-neutral-500">Visualize and mitigate identity-based threats</p>
                </div>
                <Button variant="secondary">
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Re-scan Environment
                </Button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                <div className="h-[400px]">
                    <RiskMatrix />
                </div>
                <div className="h-[400px]">
                    <PrivilegeEscalationPath />
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[350px]">
                <div className="lg:col-span-2 h-full">
                    <UnusedPermissionsChart />
                </div>
                <div className="lg:col-span-1 h-full">
                    <RemediationQueue />
                </div>
            </div>
        </DashboardLayout>
    );
}
