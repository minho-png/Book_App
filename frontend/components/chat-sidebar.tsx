"use client"

import { motion } from "framer-motion"
import {
  MessageSquare,
  TrendingUp,
  Clock,
  BookOpen,
  Flame,
  X,
} from "lucide-react"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Settings, Key } from "lucide-react"
import { useState, useEffect } from "react"

interface ChatHistory {
  id: string
  title: string
  date: string
}

interface TrendingBook {
  rank: number
  title: string
  author: string
  store: string
}

const chatHistory: ChatHistory[] = []

const trendingBooks: TrendingBook[] = []

const storeTagColor: Record<string, string> = {
  "교보문고": "text-[#C4956A]",
  "밀리의서재": "text-[#7BA08A]",
  "알라딘": "text-[#5B8FA8]",
}

interface ChatSidebarProps {
  isOpen: boolean
  onClose: () => void
}

export function ChatSidebar({ isOpen, onClose }: ChatSidebarProps) {
  const [apiKey, setApiKey] = useState("")

  useEffect(() => {
    const savedKey = localStorage.getItem("google_api_key") || ""
    setApiKey(savedKey)
  }, [])

  const handleApiKeyChange = (val: string) => {
    setApiKey(val)
    localStorage.setItem("google_api_key", val)
  }

  return (
    <>
      {/* Backdrop for mobile */}
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
          className="fixed inset-0 bg-foreground/20 z-40 lg:hidden"
        />
      )}

      <motion.aside
        initial={false}
        animate={{
          x: isOpen ? 0 : -320,
          opacity: isOpen ? 1 : 0,
        }}
        transition={{ type: "spring", damping: 25, stiffness: 200 }}
        className="fixed left-0 top-0 bottom-0 z-50 w-[300px] flex flex-col backdrop-blur-xl bg-[rgba(255,255,255,0.65)] border-r border-border/50 shadow-xl"
      >
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-border/50">
          <div className="flex items-center gap-2">
            <BookOpen className="h-5 w-5 text-accent" />
            <h2 className="text-sm font-bold text-foreground font-serif">BookCurator AI</h2>
          </div>
          <button
            onClick={onClose}
            className="lg:hidden h-7 w-7 flex items-center justify-center rounded-lg hover:bg-muted transition-colors"
          >
            <X className="h-4 w-4 text-muted-foreground" />
            <span className="sr-only">닫기</span>
          </button>
        </div>

        <ScrollArea className="flex-1">
          <div className="flex flex-col gap-6 p-5">
            {/* Chat History */}
            <section>
              <div className="flex items-center gap-2 mb-3">
                <MessageSquare className="h-3.5 w-3.5 text-muted-foreground" />
                <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  대화 기록
                </h3>
              </div>
              <div className="flex flex-col gap-1">
                {chatHistory.map((chat) => (
                  <button
                    key={chat.id}
                    className="flex items-center justify-between px-3 py-2.5 rounded-lg text-left hover:bg-muted/60 transition-colors group"
                  >
                    <span className="text-[13px] text-foreground truncate flex-1 mr-2 group-hover:text-accent transition-colors">
                      {chat.title}
                    </span>
                    <span className="flex items-center gap-1 text-[10px] text-muted-foreground flex-shrink-0">
                      <Clock className="h-2.5 w-2.5" />
                      {chat.date}
                    </span>
                  </button>
                ))}
              </div>
            </section>

            {/* Hot Trends */}
            <section>
              <div className="flex items-center gap-2 mb-3">
                <Flame className="h-3.5 w-3.5 text-accent" />
                <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  실시간 인기 도서
                </h3>
              </div>
              <div className="flex flex-col gap-1">
                {trendingBooks.map((book) => (
                  <div
                    key={book.rank}
                    className="flex items-start gap-3 px-3 py-2.5 rounded-lg hover:bg-muted/60 transition-colors cursor-pointer"
                  >
                    <span
                      className={`text-sm font-bold flex-shrink-0 w-5 text-center ${book.rank <= 3 ? "text-accent" : "text-muted-foreground"
                        }`}
                    >
                      {book.rank}
                    </span>
                    <div className="flex flex-col gap-0.5 min-w-0">
                      <span className="text-[13px] text-foreground truncate font-medium">
                        {book.title}
                      </span>
                      <div className="flex items-center gap-2">
                        <span className="text-[11px] text-muted-foreground">
                          {book.author}
                        </span>
                        <span className={`text-[10px] font-medium ${storeTagColor[book.store] || "text-muted-foreground"}`}>
                          {book.store}
                        </span>
                      </div>
                    </div>
                    <TrendingUp className="h-3 w-3 text-[#7BA08A] flex-shrink-0 mt-1" />
                  </div>
                ))}
              </div>
            </section>
          </div>
        </ScrollArea>

        {/* Settings / API Key */}
        <div className="px-5 py-5 border-t border-border/50 bg-muted/20">
          <div className="flex items-center gap-2 mb-3">
            <Settings className="h-3.5 w-3.5 text-muted-foreground" />
            <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
              설정
            </h3>
          </div>
          <div className="flex flex-col gap-2">
            <label className="text-[11px] text-muted-foreground flex items-center gap-1.5">
              <Key className="h-3 w-3" />
              Google Gemini API Key
            </label>
            <input
              type="password"
              value={apiKey}
              onChange={(e) => handleApiKeyChange(e.target.value)}
              placeholder="API Key 입력"
              className="w-full px-3 py-2 rounded-md bg-background border border-border/80 text-[12px] focus:outline-none focus:ring-1 focus:ring-accent/50 transition-all placeholder:text-muted-foreground/50"
            />
            <p className="text-[10px] text-muted-foreground/70 leading-relaxed">
              * API Key는 브라우저 로컬 저장소에만 안전하게 보관됩니다.
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="px-5 py-3 border-t border-border/50">
          <p className="text-[10px] text-muted-foreground text-center">
            교보문고 / 밀리의서재 / 알라딘 데이터 기반
          </p>
        </div>
      </motion.aside>
    </>
  )
}
