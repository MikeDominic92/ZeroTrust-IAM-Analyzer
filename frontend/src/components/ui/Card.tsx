import React from 'react';
import { cn } from '@/lib/utils';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
    variant?: 'default' | 'outlined' | 'elevated';
}

export function Card({ className, variant = 'default', children, ...props }: CardProps) {
    const variants = {
        default: 'bg-surface border border-neutral-200 shadow-card',
        outlined: 'bg-surface border border-neutral-200',
        elevated: 'bg-surface shadow-elevation-1 hover:shadow-elevation-2 transition-shadow duration-200',
    };

    return (
        <div className={cn('rounded-2xl overflow-hidden', variants[variant], className)} {...props}>
            {children}
        </div>
    );
}

export function CardHeader({ className, children, ...props }: React.HTMLAttributes<HTMLDivElement>) {
    return <div className={cn('px-6 py-4 border-b border-neutral-100', className)} {...props}>{children}</div>;
}

export function CardTitle({ className, children, ...props }: React.HTMLAttributes<HTMLHeadingElement>) {
    return <h3 className={cn('text-lg font-semibold text-surface-dark font-poppins', className)} {...props}>{children}</h3>;
}

export function CardContent({ className, children, ...props }: React.HTMLAttributes<HTMLDivElement>) {
    return <div className={cn('p-6', className)} {...props}>{children}</div>;
}
