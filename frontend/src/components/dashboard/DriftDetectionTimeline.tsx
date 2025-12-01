'use client';

import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

const data = [
    { day: 'Mon', score: 12 },
    { day: 'Tue', score: 15 },
    { day: 'Wed', score: 8 },
    { day: 'Thu', score: 24 },
    { day: 'Fri', score: 18 },
    { day: 'Sat', score: 10 },
    { day: 'Sun', score: 14 },
];

export function DriftDetectionTimeline() {
    return (
        <Card className="h-full">
            <CardHeader>
                <CardTitle>Policy Drift Timeline</CardTitle>
            </CardHeader>
            <CardContent className="h-[250px]">
                <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                        <XAxis
                            dataKey="day"
                            tick={{ fill: '#64748B', fontSize: 12 }}
                            axisLine={false}
                            tickLine={false}
                        />
                        <YAxis
                            tick={{ fill: '#64748B', fontSize: 12 }}
                            axisLine={false}
                            tickLine={false}
                        />
                        <Tooltip
                            contentStyle={{ backgroundColor: '#fff', border: '1px solid #E2E8F0', borderRadius: '8px', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                        />
                        <Line
                            type="monotone"
                            dataKey="score"
                            stroke="#7C3AED"
                            strokeWidth={3}
                            dot={{ fill: '#7C3AED', r: 4 }}
                            activeDot={{ r: 6, stroke: '#fff', strokeWidth: 2 }}
                        />
                    </LineChart>
                </ResponsiveContainer>
            </CardContent>
        </Card>
    );
}
