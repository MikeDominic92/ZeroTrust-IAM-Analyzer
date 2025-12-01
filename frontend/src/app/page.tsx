'use client';

import React from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { SecurityScoreGauge } from '@/components/dashboard/SecurityScoreGauge';
import { CloudProviderBreakdown } from '@/components/dashboard/CloudProviderBreakdown';
import { TopRiskyIdentities } from '@/components/dashboard/TopRiskyIdentities';
import { PermissionDistribution } from '@/components/dashboard/PermissionDistribution';
import { DriftDetectionTimeline } from '@/components/dashboard/DriftDetectionTimeline';
import { Button } from '@/components/ui/Button';
import { Download } from 'lucide-react';

export default function Dashboard() {
  return (
    <DashboardLayout>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-surface-dark">Security Posture Dashboard</h1>
          <p className="text-neutral-500">Overview of your multi-cloud permission landscape</p>
        </div>
        <Button variant="outline">
          <Download className="w-4 h-4 mr-2" />
          Export Report
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        {/* Left Column: Score & Providers */}
        <div className="lg:col-span-2 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 h-[300px]">
            <SecurityScoreGauge />
            <div className="h-full">
              <CloudProviderBreakdown />
            </div>
          </div>
          <div className="h-[300px]">
            <DriftDetectionTimeline />
          </div>
        </div>

        {/* Right Column: Risky Identities */}
        <div className="lg:col-span-1 h-full">
          <TopRiskyIdentities />
        </div>
      </div>

      {/* Bottom Row: Treemap */}
      <div className="h-[400px]">
        <PermissionDistribution />
      </div>
    </DashboardLayout>
  );
}
