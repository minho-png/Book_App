'use client'

import type { SourceData } from '@/types/book'

const storeConfig: Record<string, { label: string; color: string }> = {
    kyobo: { label: '교보문고', color: '#C4956A' },
    millie: { label: '밀리의서재', color: '#7BA08A' },
    aladdin: { label: '알라딘', color: '#5B8FA8' },
}

export function SourceCitation({ sources }: { sources: SourceData[] }) {
    return (
        <div className="flex flex-wrap gap-1.5">
            {sources.map((s, i) => {
                const cfg = storeConfig[s.store] ?? { label: s.store, color: '#888' }
                return (
                    <div key={i} className="flex items-center gap-1.5 rounded-full border border-border bg-card px-3 py-1">
                        <div className="h-2 w-2 rounded-full" style={{ backgroundColor: cfg.color }} />
                        <span className="text-[11px] text-muted-foreground">{cfg.label}</span>
                        <span className="text-[10px] text-muted-foreground/70">·</span>
                        <span className="text-[11px] text-muted-foreground">{s.category}</span>
                        <span className="text-[10px] font-medium text-accent">{s.confidence}%</span>
                    </div>
                )
            })}
        </div>
    )
}
