'use client';

import React from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { PermissionMatrix } from '@/components/crosscloud/PermissionMatrix';
import { MultiCloudRiskHeatmap } from '@/components/crosscloud/MultiCloudRiskHeatmap';
import { UnifiedIdentityView } from '@/components/crosscloud/UnifiedIdentityView';
import { Button } from '@/components/ui/Button';
import { Globe } from 'lucide-react';

export default function CrossCloud() {
    return (
        <DashboardLayout>
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="text-2xl font-bold text-surface-dark">Cross-Cloud Visibility</h1>
                    <p className="text-neutral-500">Unified view of identities across AWS, GCP, and Azure</p>
                </div>
                <Button variant="outline">
                    <Globe className="w-4 h-4 mr-2" />
                    Map External IdP
                </Button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                <div className="h-[400px]">
                    <UnifiedIdentityView />
                </div>
                <div className="h-[400px]">
                    <PermissionMatrix />
                </div>
            </div>

            <div className="h-[400px]">
                <MultiCloudRiskHeatmap />
            </div>
        </DashboardLayout>
    );
}
