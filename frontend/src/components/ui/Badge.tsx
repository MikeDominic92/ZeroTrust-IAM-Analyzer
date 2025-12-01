import React from 'react';
import { cn } from '@/lib/utils';

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
    variant?: 'default' | 'success' | 'warning' | 'danger' | 'info' | 'neutral';
}

export function Badge({ className, variant = 'default', children, ...props }: BadgeProps) {
    const variants = {
        default: 'bg-google-blue/10 text-google-blue border-google-blue/20',
        success: 'bg-risk-low/10 text-risk-low border-risk-low/20',
        warning: 'bg-risk-medium/10 text-risk-medium border-risk-medium/20',
        danger: 'bg-risk-high/10 text-risk-high border-risk-high/20',
        info: 'bg-blue-50 text-blue-700 border-blue-200',
        neutral: 'bg-neutral-100 text-neutral-600 border-neutral-200',
    };

    return (
        <span
            className={cn(
                'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border',
                variants[variant],
                className
            )}
            {...props}
        >
            {children}
        </span>
    );
}
