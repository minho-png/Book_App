"use client"

import { motion } from "framer-motion"
import {
  MessageSquare,
  Clock,
  BookOpen,
  Plus,
  Trash2,
  X,
  Settings,
  Key,
} from "lucide-react"
import { ScrollArea } from "@/components/ui/scroll-area"
import { useState, useEffect, useCallback } from "react"

interface ChatSession {
  id: string
  title: string
  date: string
}

interface ChatSidebarProps {
  isOpen: boolean
  onClose: () => void
  onSelectSession: (sessionId: string) => void
  onNewChat: () => void
  currentSessionId: string | null
}

export function ChatSidebar({
  isOpen,
  onClose,
  onSelectSession,
  onNewChat,
  currentSessionId
}: ChatSidebarProps) {
  const [apiKey, setApiKey] = useState("")
  const [history, setHistory] = useState<ChatSession[]>([])

  const loadHistory = useCallback(() => {
    const saved = localStorage.getItem("book_curator_history")
    if (saved) {
      try {
        setHistory(JSON.parse(saved))
      } catch (e) {
        console.error("Failed to parse history", e)
      }
    }
  }, [])

  useEffect(() => {
    loadHistory()
    const savedKey = localStorage.getItem("google_api_key") || ""
    setApiKey(savedKey)
  }, [loadHistory])

  // Listen for history updates from other components
  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === "book_curator_history") {
        loadHistory()
      }
    }
    window.addEventListener("storage", handleStorageChange)
    return () => window.removeEventListener("storage", handleStorageChange)
  }, [loadHistory])

  const handleApiKeyChange = (val: string) => {
    setApiKey(val)
    localStorage.setItem("google_api_key", val)
  }

  const deleteSession = (e: React.MouseEvent, id: string) => {
    e.stopPropagation()
    const updated = history.filter(s => s.id !== id)
    localStorage.setItem("book_curator_history", JSON.stringify(updated))
    localStorage.removeItem(`book_curator_session_${id}`)
    setHistory(updated)
    if (currentSessionId === id) {
      onNewChat()
    }
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
            className="h-7 w-7 flex items-center justify-center rounded-lg hover:bg-muted transition-colors transition-opacity"
            aria-label="사이드바 닫기"
          >
            <X className="h-4 w-4 text-muted-foreground" />
          </button>
        </div>

        <ScrollArea className="flex-1">
          <div className="flex flex-col gap-6 p-5">
            {/* New Chat Button */}
            <button
              onClick={() => {
                onNewChat()
                onClose()
              }}
              className="flex items-center gap-2 w-full px-4 py-3 rounded-xl bg-accent text-accent-foreground font-medium text-sm hover:opacity-90 transition-all shadow-sm group"
            >
              <Plus className="h-4 w-4 group-hover:rotate-90 transition-transform duration-300" />
              <span>새 대화 시작</span>
            </button>

            {/* Chat History */}
            <section>
              <div className="flex items-center gap-2 mb-3 px-1">
                <MessageSquare className="h-3.5 w-3.5 text-muted-foreground" />
                <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  대화 기록
                </h3>
              </div>
              <div className="flex flex-col gap-1">
                {history.length === 0 ? (
                  <div className="px-3 py-8 text-center border-2 border-dashed border-border/30 rounded-xl">
                    <p className="text-[11px] text-muted-foreground">저장된 대화가 없습니다.</p>
                  </div>
                ) : (
                  history.map((chat) => (
                    <button
                      key={chat.id}
                      onClick={() => {
                        onSelectSession(chat.id)
                        onClose()
                      }}
                      className={`flex items-center justify-between px-3 py-2.5 rounded-lg text-left transition-all group ${currentSessionId === chat.id
                          ? "bg-accent/15 text-accent"
                          : "hover:bg-muted/60 text-foreground"
                        }`}
                    >
                      <div className="flex flex-col min-w-0 flex-1 mr-2">
                        <span className="text-[13px] truncate font-medium">
                          {chat.title}
                        </span>
                        <span className="flex items-center gap-1 text-[10px] text-muted-foreground">
                          <Clock className="h-2.5 w-2.5" />
                          {chat.date}
                        </span>
                      </div>
                      <button
                        onClick={(e) => deleteSession(e, chat.id)}
                        className="opacity-0 group-hover:opacity-100 h-6 w-6 flex items-center justify-center rounded-md hover:bg-destructive/10 hover:text-destructive transition-all"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </button>
                    </button>
                  ))
                )}
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
            <label className="text-[11px] text-muted-foreground flex items-center gap-1.5 font-medium">
              <Key className="h-3 w-3" />
              Google Gemini API Key
            </label>
            <input
              type="password"
              value={apiKey}
              onChange={(e) => handleApiKeyChange(e.target.value)}
              placeholder="API Key 입력"
              className="w-full px-3 py-2 rounded-xl bg-background border border-border/80 text-[12px] focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent transition-all placeholder:text-muted-foreground/50"
            />
            <p className="text-[10px] text-muted-foreground/70 leading-relaxed px-1">
              * API Key는 브라우저 로컬 저장소에만 안전하게 보관됩니다.
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="px-5 py-4 border-t border-border/50">
          <p className="text-[10px] text-muted-foreground text-center font-medium">
            BookCurator AI &copy; 2026
          </p>
        </div>
      </motion.aside>
    </>
  )
}
