'use client';

import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { ResponsiveContainer, Treemap } from 'recharts';

const data = [
    { name: 'Compute', size: 400, fill: '#4285F4' },
    { name: 'Storage', size: 300, fill: '#34A853' },
    { name: 'Database', size: 300, fill: '#FBBC05' },
    { name: 'Network', size: 200, fill: '#EA4335' },
    { name: 'IAM', size: 150, fill: '#7C3AED' },
    { name: 'Analytics', size: 100, fill: '#F59E0B' },
];

const CustomContent = (props: any) => {
    const { x, y, width, height, index, name } = props;
    return (
        <g>
            <rect
                x={x}
                y={y}
                width={width}
                height={height}
                style={{
                    fill: data[index % data.length].fill,
                    stroke: '#fff',
                    strokeWidth: 2,
                    strokeOpacity: 1,
                }}
            />
            {width > 50 && height > 30 && (
                <text
                    x={x + width / 2}
                    y={y + height / 2}
                    textAnchor="middle"
                    fill="#fff"
                    fontSize={12}
                    fontWeight="bold"
                >
                    {name}
                </text>
            )}
        </g>
    );
};

export function PermissionDistribution() {
    return (
        <Card className="h-full">
            <CardHeader>
                <CardTitle>Permission Distribution</CardTitle>
            </CardHeader>
            <CardContent className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                    <Treemap
                        data={data}
                        dataKey="size"
                        stroke="#fff"
                        fill="#8884d8"
                        content={<CustomContent />}
                    />
                </ResponsiveContainer>
            </CardContent>
        </Card>
    );
}
