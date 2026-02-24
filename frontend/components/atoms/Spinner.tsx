'use client'

import { motion } from 'framer-motion'

export function Spinner({ size = 'md' }: { size?: 'sm' | 'md' | 'lg' }) {
    const sizeMap = { sm: 'h-4 w-4', md: 'h-6 w-6', lg: 'h-8 w-8' }
    return (
        <motion.div
            className={`${sizeMap[size]} rounded-full border-2 border-accent/30 border-t-accent`}
            animate={{ rotate: 360 }}
            transition={{ duration: 0.8, repeat: Infinity, ease: 'linear' }}
        />
    )
}
