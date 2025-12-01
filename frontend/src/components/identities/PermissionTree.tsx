'use client';

import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { ChevronRight, ChevronDown, Folder, FileKey, Shield } from 'lucide-react';

const permissions = [
    {
        id: 'aws', name: 'AWS Production', type: 'folder', children: [
            {
                id: 's3', name: 'S3 Buckets', type: 'folder', children: [
                    { id: 's3-read', name: 's3:GetObject', type: 'permission', resource: 'arn:aws:s3:::prod-data/*' },
                    { id: 's3-list', name: 's3:ListBucket', type: 'permission', resource: 'arn:aws:s3:::prod-data' },
                ]
            },
            {
                id: 'ec2', name: 'EC2 Instances', type: 'folder', children: [
                    { id: 'ec2-desc', name: 'ec2:DescribeInstances', type: 'permission', resource: '*' },
                ]
            }
        ]
    },
    {
        id: 'gcp', name: 'GCP Analytics', type: 'folder', children: [
            {
                id: 'bq', name: 'BigQuery', type: 'folder', children: [
                    { id: 'bq-job', name: 'bigquery.jobs.create', type: 'permission', resource: 'projects/analytics-prod' },
                ]
            }
        ]
    }
];

const TreeNode = ({ node, level = 0 }: { node: any, level?: number }) => {
    const [isOpen, setIsOpen] = useState(true);
    const hasChildren = node.children && node.children.length > 0;

    return (
        <div className="select-none">
            <div
                className={`flex items-center py-1.5 px-2 hover:bg-neutral-50 rounded cursor-pointer ${level === 0 ? 'font-medium text-surface-dark' : 'text-neutral-600'}`}
                style={{ paddingLeft: `${level * 16 + 8}px` }}
                onClick={() => hasChildren && setIsOpen(!isOpen)}
            >
                <span className="mr-1 text-neutral-400 w-4 h-4 flex items-center justify-center">
                    {hasChildren && (isOpen ? <ChevronDown size={14} /> : <ChevronRight size={14} />)}
                </span>
                <span className={`mr-2 ${node.type === 'folder' ? 'text-blue-500' : 'text-purple-500'}`}>
                    {node.type === 'folder' ? <Folder size={16} /> : <FileKey size={16} />}
                </span>
                <span className="text-sm truncate">{node.name}</span>
                {node.resource && <span className="ml-2 text-xs text-neutral-400 font-mono truncate max-w-[200px]">{node.resource}</span>}
            </div>
            {hasChildren && isOpen && (
                <div>
                    {node.children.map((child: any) => (
                        <TreeNode key={child.id} node={child} level={level + 1} />
                    ))}
                </div>
            )}
        </div>
    );
};

export function PermissionTree() {
    return (
        <Card className="h-full flex flex-col">
            <CardHeader>
                <CardTitle>Entitlement Hierarchy</CardTitle>
            </CardHeader>
            <CardContent className="flex-1 overflow-y-auto p-2">
                {permissions.map((node) => (
                    <TreeNode key={node.id} node={node} />
                ))}
            </CardContent>
        </Card>
    );
}
