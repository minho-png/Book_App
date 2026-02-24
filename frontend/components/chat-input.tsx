"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { Send, BookOpen } from "lucide-react"

interface ChatInputProps {
  onSend: (message: string) => void
  isLoading: boolean
}

export function ChatInput({ onSend, isLoading }: ChatInputProps) {
  const [input, setInput] = useState("")
  const [libraryMode, setLibraryMode] = useState(true)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return
    onSend(input.trim())
    setInput("")
  }

  return (
    <div className="sticky bottom-0 w-full bg-gradient-to-t from-background via-background to-background/0 pt-6 pb-4 px-4">
      <form
        onSubmit={handleSubmit}
        className="mx-auto max-w-3xl flex flex-col gap-2"
      >
        {/* Library Toggle */}
        <div className="flex items-center gap-2 px-1">
          <button
            type="button"
            onClick={() => setLibraryMode(!libraryMode)}
            className={`flex items-center gap-1.5 rounded-full px-3 py-1.5 text-[11px] font-medium transition-colors ${
              libraryMode
                ? "bg-accent text-accent-foreground"
                : "bg-muted text-muted-foreground hover:text-foreground"
            }`}
          >
            <BookOpen className="h-3 w-3" />
            도서관 검색
          </button>
          <span className="text-[10px] text-muted-foreground">
            {libraryMode
              ? "교보문고, 밀리의서재, 알라딘 랭킹을 분석합니다"
              : "일반 대화 모드입니다"}
          </span>
        </div>

        {/* Input Field */}
        <div className="relative flex items-center">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="어떤 책을 찾고 계신가요? 예: 올해 베스트셀러 추천해줘"
            className="w-full rounded-2xl border border-border bg-card text-card-foreground px-5 py-3.5 pr-14 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring/50 focus:border-accent shadow-sm transition-all"
            disabled={isLoading}
          />
          <motion.button
            type="submit"
            disabled={!input.trim() || isLoading}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="absolute right-2 flex h-9 w-9 items-center justify-center rounded-xl bg-primary text-primary-foreground disabled:opacity-40 transition-opacity"
          >
            <Send className="h-4 w-4" />
            <span className="sr-only">전송</span>
          </motion.button>
        </div>

        <p className="text-center text-[10px] text-muted-foreground">
          AI가 추천한 결과는 참고용입니다. 실제 랭킹은 각 서점에서 확인해 주세요.
        </p>
      </form>
    </div>
  )
}
