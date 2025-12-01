'use client';

import React from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { RecommendationList } from '@/components/recommendations/RecommendationList';
import { ImpactAnalysis } from '@/components/recommendations/ImpactAnalysis';
import { ApprovalWorkflow } from '@/components/recommendations/ApprovalWorkflow';
import { Button } from '@/components/ui/Button';
import { Zap } from 'lucide-react';

export default function Recommendations() {
    return (
        <DashboardLayout>
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="text-2xl font-bold text-surface-dark">Least Privilege Recommendations</h1>
                    <p className="text-neutral-500">Automated policy rightsizing and cleanup</p>
                </div>
                <Button>
                    <Zap className="w-4 h-4 mr-2" />
                    Auto-Remediate Low Risk
                </Button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                {/* Left Column: List */}
                <div className="lg:col-span-8">
                    <RecommendationList />
                </div>

                {/* Right Column: Context */}
                <div className="lg:col-span-4 space-y-6">
                    <div className="h-[250px]">
                        <ImpactAnalysis />
                    </div>
                    <div className="h-[400px]">
                        <ApprovalWorkflow />
                    </div>
                </div>
            </div>
        </DashboardLayout>
    );
}
