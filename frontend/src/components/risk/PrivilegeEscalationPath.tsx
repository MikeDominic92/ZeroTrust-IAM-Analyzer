'use client';

import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { ArrowRight, User, Key, Server, ShieldAlert } from 'lucide-react';

export function PrivilegeEscalationPath() {
    return (
        <Card className="h-full">
            <CardHeader>
                <CardTitle>Attack Path Analysis</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="flex items-center justify-between p-4 bg-neutral-50 rounded-xl overflow-x-auto">
                    {/* Step 1 */}
                    <div className="flex flex-col items-center min-w-[120px]">
                        <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 mb-2">
                            <User size={24} />
                        </div>
                        <p className="text-sm font-bold text-surface-dark">Compromised User</p>
                        <p className="text-xs text-neutral-500">dev-user</p>
                    </div>

                    <ArrowRight className="text-neutral-300 w-6 h-6 mx-2" />

                    {/* Step 2 */}
                    <div className="flex flex-col items-center min-w-[120px]">
                        <div className="w-12 h-12 rounded-full bg-purple-100 flex items-center justify-center text-purple-600 mb-2">
                            <Key size={24} />
                        </div>
                        <p className="text-sm font-bold text-surface-dark">Assumes Role</p>
                        <p className="text-xs text-neutral-500">ci-cd-runner</p>
                    </div>

                    <ArrowRight className="text-neutral-300 w-6 h-6 mx-2" />

                    {/* Step 3 */}
                    <div className="flex flex-col items-center min-w-[120px]">
                        <div className="w-12 h-12 rounded-full bg-orange-100 flex items-center justify-center text-orange-600 mb-2">
                            <Server size={24} />
                        </div>
                        <p className="text-sm font-bold text-surface-dark">Access Resource</p>
                        <p className="text-xs text-neutral-500">EC2 Metadata</p>
                    </div>

                    <ArrowRight className="text-risk-high w-6 h-6 mx-2" />

                    {/* Step 4 */}
                    <div className="flex flex-col items-center min-w-[120px]">
                        <div className="w-12 h-12 rounded-full bg-risk-high/10 flex items-center justify-center text-risk-high mb-2 border-2 border-risk-high">
                            <ShieldAlert size={24} />
                        </div>
                        <p className="text-sm font-bold text-risk-high">Admin Access</p>
                        <p className="text-xs text-neutral-500">Full Control</p>
                    </div>
                </div>

                <div className="mt-4 p-3 bg-risk-high/5 border border-risk-high/20 rounded-lg flex items-start">
                    <ShieldAlert className="text-risk-high w-5 h-5 mr-2 mt-0.5" />
                    <div>
                        <h4 className="text-sm font-bold text-risk-high">Critical Escalation Risk</h4>
                        <p className="text-xs text-neutral-600 mt-1">
                            This chain allows a standard developer account to escalate to full admin privileges via the CI/CD role's overly permissive trust policy.
                        </p>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
