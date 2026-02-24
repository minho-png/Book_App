'use client'

import { motion } from 'framer-motion'
import { Loader2 } from 'lucide-react'
import { cn } from '@/lib/utils'

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: 'primary' | 'secondary' | 'ghost'
    size?: 'sm' | 'md' | 'lg'
    isLoading?: boolean
    children: React.ReactNode
}

export function Button({
    variant = 'primary',
    size = 'md',
    isLoading = false,
    disabled,
    className,
    children,
    ...props
}: ButtonProps) {
    const base = 'inline-flex items-center justify-center gap-2 rounded-xl font-medium transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent disabled:opacity-50 disabled:cursor-not-allowed'

    const variants = {
        primary: 'bg-primary text-primary-foreground hover:opacity-90 active:scale-95',
        secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
        ghost: 'hover:bg-muted text-foreground',
    }

    const sizes = {
        sm: 'h-8 px-3 text-xs',
        md: 'h-10 px-4 text-sm',
        lg: 'h-12 px-6 text-base',
    }

    return (
        <motion.button
            whileTap={!disabled && !isLoading ? { scale: 0.97 } : undefined}
            className={cn(base, variants[variant], sizes[size], className)}
            disabled={disabled || isLoading}
            {...(props as any)}
        >
            {isLoading && <Loader2 className="h-4 w-4 animate-spin" />}
            {children}
        </motion.button>
    )
}
