"use client"

import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { Menu, BookOpen, Sparkles } from "lucide-react"
import { ChatInput } from "@/components/chat-input"
import { ChatSidebar } from "@/components/chat-sidebar"
import { ChatWindow } from "@/components/organisms/ChatWindow"
import { useStream } from "@/hooks/useStream"

const suggestedQuestions = [
  "올해 베스트셀러 추천해줘",
  "자기계발 도서 중 인기 있는 책은?",
  "요즘 인기 있는 소설 알려줘",
  "경제/경영 분야 신간 추천",
]

export default function BookCuratorPage() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null)
  const { messages, setMessages, isLoading, sendMessage } = useStream()

  // Load session from localStorage
  const handleSelectSession = (sessionId: string) => {
    const saved = localStorage.getItem(`book_curator_session_${sessionId}`)
    if (saved) {
      try {
        setMessages(JSON.parse(saved))
        setCurrentSessionId(sessionId)
      } catch (e) {
        console.error("Failed to load session", e)
      }
    }
  }

  const handleNewChat = () => {
    setMessages([])
    setCurrentSessionId(null)
  }

  // Auto-save and history management
  useEffect(() => {
    if (messages.length === 0) return

    let sessionId = currentSessionId
    if (!sessionId) {
      // Create new session entry
      sessionId = Date.now().toString()
      const title = messages[0].role === 'user'
        ? messages[0].content.slice(0, 25) + (messages[0].content.length > 25 ? "..." : "")
        : "새로운 대화"

      const newSession = {
        id: sessionId,
        title,
        date: new Date().toLocaleDateString('ko-KR', { month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' })
      }

      const history = JSON.parse(localStorage.getItem("book_curator_history") || "[]")
      localStorage.setItem("book_curator_history", JSON.stringify([newSession, ...history]))
      setCurrentSessionId(sessionId)

      // Dispatch storage event to update sidebar in same tab
      window.dispatchEvent(new Event('storage'))
    }

    // Save current messages
    localStorage.setItem(`book_curator_session_${sessionId}`, JSON.stringify(messages))
  }, [messages, currentSessionId])

  return (
    <div className="flex h-dvh overflow-hidden bg-background">
      {/* Sidebar */}
      <ChatSidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        onSelectSession={handleSelectSession}
        onNewChat={handleNewChat}
        currentSessionId={currentSessionId}
      />

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="flex items-center justify-between px-4 py-3 border-b border-border/50 bg-background/80 backdrop-blur-sm">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSidebarOpen(true)}
              className="h-9 w-9 flex items-center justify-center rounded-xl hover:bg-muted transition-colors"
              aria-label="사이드바 열기"
            >
              <Menu className="h-5 w-5 text-foreground" />
            </button>
            <div className="flex items-center gap-2">
              <BookOpen className="h-5 w-5 text-accent" />
              <h1 className="text-base font-bold text-foreground font-serif">
                BookCurator AI
              </h1>
            </div>
          </div>
          <div className="flex items-center gap-1.5 rounded-full bg-secondary px-3 py-1.5">
            <div className="h-2 w-2 rounded-full bg-[#7BA08A] animate-pulse" />
            <span className="text-[11px] font-medium text-secondary-foreground hidden sm:block">
              RAG 연결됨
            </span>
          </div>
        </header>

        {/* Messages or Empty State */}
        {messages.length === 0 ? (
          <div className="flex-1 overflow-y-auto flex items-center justify-center px-4">
            <EmptyState onSuggestionClick={sendMessage} />
          </div>
        ) : (
          <ChatWindow messages={messages} isLoading={isLoading} />
        )}

        {/* Input */}
        <ChatInput onSend={sendMessage} isLoading={isLoading} />
      </div>
    </div>
  )
}

function EmptyState({ onSuggestionClick }: { onSuggestionClick: (msg: string) => void }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="flex flex-col items-center justify-center gap-8 w-full max-w-xl py-8"
    >
      {/* Logo */}
      <div className="flex flex-col items-center gap-3">
        <div className="h-16 w-16 rounded-2xl bg-accent/10 flex items-center justify-center">
          <BookOpen className="h-8 w-8 text-accent" />
        </div>
        <h2 className="text-2xl font-bold text-foreground font-serif text-balance text-center">
          AI 도서 큐레이터
        </h2>
        <p className="text-sm text-muted-foreground text-center max-w-md leading-relaxed text-pretty">
          교보문고, 밀리의서재, 알라딘의 랭킹 데이터를 실시간으로 분석하여
          당신에게 딱 맞는 도서를 추천해 드립니다.
        </p>
      </div>

      {/* Suggested Questions */}
      <div className="flex flex-col gap-2 w-full">
        <span className="text-[11px] font-medium text-muted-foreground text-center">
          이런 질문을 해보세요
        </span>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          {suggestedQuestions.map((q) => (
            <motion.button
              key={q}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => onSuggestionClick(q)}
              className="flex items-center gap-2 rounded-xl border border-border bg-card px-4 py-3 text-left text-sm text-card-foreground hover:border-accent/50 hover:shadow-sm transition-all"
            >
              <Sparkles className="h-3.5 w-3.5 text-accent flex-shrink-0" />
              <span>{q}</span>
            </motion.button>
          ))}
        </div>
      </div>

      {/* Data Sources */}
      <div className="flex items-center gap-4 flex-wrap justify-center">
        {[
          { name: "교보문고", color: "#C4956A" },
          { name: "밀리의서재", color: "#7BA08A" },
          { name: "알라딘", color: "#5B8FA8" },
        ].map((store) => (
          <div key={store.name} className="flex items-center gap-1.5">
            <div className="h-2 w-2 rounded-full" style={{ backgroundColor: store.color }} />
            <span className="text-[11px] text-muted-foreground">{store.name}</span>
          </div>
        ))}
      </div>
    </motion.div>
  )
}
