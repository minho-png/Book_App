'use client'

import { motion } from 'framer-motion'
import { Star, ExternalLink } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import type { BookData } from '@/types/book'

const storeLabels: Record<string, string> = {
    kyobo: '교보문고', millie: '밀리의서재', aladdin: '알라딘',
}
const storeColors: Record<string, string> = {
    kyobo: 'bg-[#C4956A] text-white',
    millie: 'bg-[#7BA08A] text-white',
    aladdin: 'bg-[#5B8FA8] text-white',
}

export function BookCard({ book }: { book: BookData }) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, ease: 'easeOut' }}
            className="flex-shrink-0 w-[200px] sm:w-[220px] rounded-xl bg-card border border-border p-4 flex flex-col gap-3 shadow-sm hover:shadow-md transition-all hover:-translate-y-0.5"
        >
            {/* Cover */}
            <div
                className="w-full h-[130px] sm:h-[140px] rounded-lg flex items-end p-3 relative overflow-hidden"
                style={{ backgroundColor: book.cover_color ?? '#5B8FA8' }}
            >
                {book.image_url && (
                    <img
                        src={book.image_url}
                        alt={book.title}
                        className="absolute inset-0 w-full h-full object-cover opacity-80"
                    />
                )}
                <div className="relative z-10 flex flex-col gap-0.5">
                    <span className="text-[10px] font-medium text-white/80">{book.author}</span>
                    <h4 className="text-sm font-bold text-white leading-tight line-clamp-2">{book.title}</h4>
                </div>
            </div>

            {/* Genre */}
            {book.genre && (
                <Badge variant="secondary" className="w-fit text-[10px]">{book.genre}</Badge>
            )}

            {/* Rating */}
            {book.rating != null && (
                <div className="flex items-center gap-1">
                    {Array.from({ length: 5 }).map((_, i) => (
                        <Star key={i} className={`h-3 w-3 ${i < Math.floor(book.rating!) ? 'fill-[#C4956A] text-[#C4956A]' : 'fill-border text-border'}`} />
                    ))}
                    <span className="text-[11px] text-muted-foreground ml-1">{book.rating}</span>
                </div>
            )}

            {/* Description */}
            {book.description && (
                <p className="text-[11px] text-muted-foreground leading-relaxed line-clamp-2">{book.description}</p>
            )}

            {/* Rankings */}
            <div className="flex flex-wrap gap-1.5">
                {Object.entries(book.rankings ?? {}).map(([store, rank]) => (
                    <span key={store} className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-medium ${storeColors[store] ?? 'bg-muted text-muted-foreground'}`}>
                        {storeLabels[store] ?? store} {rank}위
                    </span>
                ))}
            </div>

            {/* CTA */}
            <button className="mt-auto flex items-center justify-center gap-1.5 w-full rounded-lg bg-primary text-primary-foreground py-2 text-xs font-medium hover:opacity-90 transition-opacity">
                <ExternalLink className="h-3 w-3" />
                구매 / 읽기
            </button>
        </motion.div>
    )
}

export function BookCardCarousel({ books }: { books: BookData[] }) {
    return (
        <div className="flex gap-3 overflow-x-auto pb-2 -mx-1 px-1" style={{ scrollbarWidth: 'thin' }}>
            {books.map((book, i) => (
                <motion.div key={book.id} initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.4, delay: i * 0.08 }}>
                    <BookCard book={book} />
                </motion.div>
            ))}
        </div>
    )
}
