'use client';

import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { ResponsiveContainer, AreaChart, Area, Tooltip } from 'recharts';

const data = [
    { time: '00:00', calls: 120 },
    { time: '04:00', calls: 80 },
    { time: '08:00', calls: 450 },
    { time: '12:00', calls: 980 },
    { time: '16:00', calls: 850 },
    { time: '20:00', calls: 300 },
    { time: '23:59', calls: 150 },
];

export function UsageAnalytics() {
    return (
        <Card className="h-full">
            <CardHeader>
                <CardTitle>Activity Pattern (24h)</CardTitle>
            </CardHeader>
            <CardContent className="h-[150px]">
                <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={data} margin={{ top: 5, right: 0, left: 0, bottom: 0 }}>
                        <defs>
                            <linearGradient id="colorCalls" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#4285F4" stopOpacity={0.3} />
                                <stop offset="95%" stopColor="#4285F4" stopOpacity={0} />
                            </linearGradient>
                        </defs>
                        <Tooltip
                            contentStyle={{ backgroundColor: '#fff', border: '1px solid #E2E8F0', borderRadius: '8px' }}
                        />
                        <Area
                            type="monotone"
                            dataKey="calls"
                            stroke="#4285F4"
                            fillOpacity={1}
                            fill="url(#colorCalls)"
                        />
                    </AreaChart>
                </ResponsiveContainer>
            </CardContent>
        </Card>
    );
}
