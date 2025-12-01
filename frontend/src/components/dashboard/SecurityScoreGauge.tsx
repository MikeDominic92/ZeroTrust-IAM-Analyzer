'use client';

import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip } from 'recharts';

const data = [
    { name: 'Score', value: 78 },
    { name: 'Remaining', value: 22 },
];

const COLORS = ['#4285F4', '#E2E8F0'];

export function SecurityScoreGauge() {
    return (
        <Card className="h-full flex flex-col">
            <CardHeader>
                <CardTitle>Organization Security Score</CardTitle>
            </CardHeader>
            <CardContent className="flex-1 flex flex-col items-center justify-center relative">
                <div className="w-full h-[200px]">
                    <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                            <Pie
                                data={data}
                                cx="50%"
                                cy="70%"
                                startAngle={180}
                                endAngle={0}
                                innerRadius={60}
                                outerRadius={80}
                                paddingAngle={0}
                                dataKey="value"
                                stroke="none"
                            >
                                {data.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                ))}
                            </Pie>
                        </PieChart>
                    </ResponsiveContainer>
                </div>
                <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 translate-y-4 text-center">
                    <span className="text-4xl font-bold text-surface-dark block">78</span>
                    <span className="text-sm text-neutral-500 font-medium">GOOD</span>
                </div>
                <p className="text-center text-sm text-neutral-500 mt-[-40px]">
                    +4% from last week
                </p>
            </CardContent>
        </Card>
    );
}
