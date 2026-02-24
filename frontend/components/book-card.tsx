"use client"

import { motion } from "framer-motion"
import { Star, ExternalLink } from "lucide-react"
import { Badge } from "@/components/ui/badge"

export interface BookData {
  id: string
  title: string
  author: string
  coverColor: string
  rating: number
  description: string
  rankings: {
    kyobo?: number
    millie?: number
    aladdin?: number
  }
  genre: string
}

const storeLabels: Record<string, string> = {
  kyobo: "교보문고",
  millie: "밀리의서재",
  aladdin: "알라딘",
}

const storeColors: Record<string, string> = {
  kyobo: "bg-[#C4956A] text-[#FFFFFF]",
  millie: "bg-[#7BA08A] text-[#FFFFFF]",
  aladdin: "bg-[#5B8FA8] text-[#FFFFFF]",
}

export function BookCard({ book }: { book: BookData }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
      className="flex-shrink-0 w-[220px] rounded-xl bg-card border border-border p-4 flex flex-col gap-3 shadow-sm hover:shadow-md transition-shadow"
    >
      {/* Book Cover */}
      <div
        className="w-full h-[140px] rounded-lg flex items-end p-3"
        style={{ backgroundColor: book.coverColor }}
      >
        <div className="flex flex-col gap-1">
          <span className="text-[10px] font-medium text-white/70">{book.author}</span>
          <h4 className="text-sm font-bold text-white leading-tight line-clamp-2 text-balance">
            {book.title}
          </h4>
        </div>
      </div>

      {/* Genre Badge */}
      <Badge variant="secondary" className="w-fit text-[10px] bg-secondary text-secondary-foreground">
        {book.genre}
      </Badge>

      {/* Rating */}
      <div className="flex items-center gap-1">
        {Array.from({ length: 5 }).map((_, i) => (
          <Star
            key={i}
            className={`h-3 w-3 ${
              i < Math.floor(book.rating)
                ? "fill-[#C4956A] text-[#C4956A]"
                : "fill-border text-border"
            }`}
          />
        ))}
        <span className="text-[11px] text-muted-foreground ml-1">{book.rating}</span>
      </div>

      {/* Description */}
      <p className="text-[11px] text-muted-foreground leading-relaxed line-clamp-2">
        {book.description}
      </p>

      {/* Store Rankings */}
      <div className="flex flex-wrap gap-1.5">
        {Object.entries(book.rankings).map(([store, rank]) => (
          <span
            key={store}
            className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-medium ${storeColors[store] || "bg-muted text-muted-foreground"}`}
          >
            {storeLabels[store]} {rank}위
          </span>
        ))}
      </div>

      {/* Action */}
      <button className="mt-auto flex items-center justify-center gap-1.5 w-full rounded-lg bg-primary text-primary-foreground py-2 text-xs font-medium hover:opacity-90 transition-opacity">
        <ExternalLink className="h-3 w-3" />
        구매 / 읽기
      </button>
    </motion.div>
  )
}

export function BookCardCarousel({ books }: { books: BookData[] }) {
  return (
    <div className="flex gap-3 overflow-x-auto pb-2 scrollbar-hide -mx-1 px-1">
      {books.map((book, i) => (
        <motion.div
          key={book.id}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.4, delay: i * 0.1 }}
        >
          <BookCard book={book} />
        </motion.div>
      ))}
    </div>
  )
}
