'use client';

import React from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { IdentityList } from '@/components/identities/IdentityList';
import { PermissionTree } from '@/components/identities/PermissionTree';
import { EffectivePermissions } from '@/components/identities/EffectivePermissions';
import { UsageAnalytics } from '@/components/identities/UsageAnalytics';
import { Button } from '@/components/ui/Button';
import { Download, Shield } from 'lucide-react';

export default function IdentityExplorer() {
    return (
        <DashboardLayout>
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="text-2xl font-bold text-surface-dark">Identity Explorer</h1>
                    <p className="text-neutral-500">Deep dive into user and service account entitlements</p>
                </div>
                <div className="flex space-x-3">
                    <Button variant="outline">
                        <Download className="w-4 h-4 mr-2" />
                        Export
                    </Button>
                    <Button>
                        <Shield className="w-4 h-4 mr-2" />
                        Run Access Review
                    </Button>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 h-[calc(100vh-180px)]">
                {/* Left Column: List */}
                <div className="lg:col-span-4 h-full">
                    <IdentityList />
                </div>

                {/* Middle Column: Hierarchy */}
                <div className="lg:col-span-5 h-full flex flex-col gap-6">
                    <div className="flex-1">
                        <PermissionTree />
                    </div>
                    <div className="h-[250px]">
                        <UsageAnalytics />
                    </div>
                </div>

                {/* Right Column: Effective Perms */}
                <div className="lg:col-span-3 h-full">
                    <EffectivePermissions />
                </div>
            </div>
        </DashboardLayout>
    );
}
