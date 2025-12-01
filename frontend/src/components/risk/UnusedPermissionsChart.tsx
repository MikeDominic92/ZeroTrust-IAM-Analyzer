'use client';

import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Legend } from 'recharts';

const data = [
    { name: 'Admin', used: 40, unused: 60 },
    { name: 'Dev', used: 70, unused: 30 },
    { name: 'Ops', used: 50, unused: 50 },
    { name: 'Audit', used: 20, unused: 80 },
    { name: 'Svc', used: 85, unused: 15 },
];

export function UnusedPermissionsChart() {
    return (
        <Card className="h-full">
            <CardHeader>
                <CardTitle>Permission Usage Efficiency</CardTitle>
            </CardHeader>
            <CardContent className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                        <XAxis dataKey="name" />
                        <YAxis />
                        <Tooltip cursor={{ fill: 'transparent' }} />
                        <Legend />
                        <Bar dataKey="used" stackId="a" fill="#10B981" name="Used" />
                        <Bar dataKey="unused" stackId="a" fill="#E2E8F0" name="Unused" />
                    </BarChart>
                </ResponsiveContainer>
            </CardContent>
        </Card>
    );
}
