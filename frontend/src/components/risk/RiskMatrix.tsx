'use client';

import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { ResponsiveContainer, ScatterChart, Scatter, XAxis, YAxis, ZAxis, Tooltip, Cell } from 'recharts';

const data = [
    { x: 10, y: 30, z: 200, name: 'Low Risk', fill: '#10B981' },
    { x: 30, y: 200, z: 200, name: 'Medium Risk', fill: '#F59E0B' },
    { x: 45, y: 100, z: 200, name: 'Medium Risk', fill: '#F59E0B' },
    { x: 50, y: 400, z: 200, name: 'High Risk', fill: '#DC2626' },
    { x: 70, y: 280, z: 200, name: 'High Risk', fill: '#DC2626' },
    { x: 100, y: 500, z: 200, name: 'Critical', fill: '#DC2626' },
    { x: 80, y: 300, z: 200, name: 'High Risk', fill: '#DC2626' },
    { x: 20, y: 50, z: 200, name: 'Low Risk', fill: '#10B981' },
];

export function RiskMatrix() {
    return (
        <Card className="h-full">
            <CardHeader>
                <CardTitle>Risk Matrix (Severity vs Likelihood)</CardTitle>
            </CardHeader>
            <CardContent className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                    <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                        <XAxis type="number" dataKey="x" name="Likelihood" unit="%" />
                        <YAxis type="number" dataKey="y" name="Impact" unit="pts" />
                        <ZAxis type="number" dataKey="z" range={[60, 400]} />
                        <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                        <Scatter name="Risks" data={data} fill="#8884d8">
                            {data.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={entry.fill} />
                            ))}
                        </Scatter>
                    </ScatterChart>
                </ResponsiveContainer>
            </CardContent>
        </Card>
    );
}
