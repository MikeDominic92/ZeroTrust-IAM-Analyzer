'use client';

import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { ResponsiveContainer, ScatterChart, Scatter, XAxis, YAxis, ZAxis, Tooltip, Cell } from 'recharts';

const data = [
    { x: 1, y: 1, z: 10, risk: 'Low' },
    { x: 1, y: 2, z: 20, risk: 'Medium' },
    { x: 1, y: 3, z: 5, risk: 'Low' },
    { x: 2, y: 1, z: 30, risk: 'High' },
    { x: 2, y: 2, z: 40, risk: 'Critical' },
    { x: 2, y: 3, z: 15, risk: 'Medium' },
    { x: 3, y: 1, z: 5, risk: 'Low' },
    { x: 3, y: 2, z: 25, risk: 'High' },
    { x: 3, y: 3, z: 10, risk: 'Low' },
];

const COLORS = {
    'Low': '#10B981',
    'Medium': '#F59E0B',
    'High': '#DC2626',
    'Critical': '#7F1D1D'
};

export function MultiCloudRiskHeatmap() {
    return (
        <Card className="h-full">
            <CardHeader>
                <CardTitle>Risk Heatmap (Region vs Service)</CardTitle>
            </CardHeader>
            <CardContent className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                    <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                        <XAxis type="number" dataKey="x" name="Region" tickFormatter={(val) => ['US-East', 'EU-West', 'AP-South'][val - 1]} />
                        <YAxis type="number" dataKey="y" name="Service" tickFormatter={(val) => ['Compute', 'Storage', 'DB'][val - 1]} />
                        <ZAxis type="number" dataKey="z" range={[100, 500]} name="Risk Score" />
                        <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                        <Scatter name="Risks" data={data}>
                            {data.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={COLORS[entry.risk as keyof typeof COLORS]} />
                            ))}
                        </Scatter>
                    </ScatterChart>
                </ResponsiveContainer>
            </CardContent>
        </Card>
    );
}
