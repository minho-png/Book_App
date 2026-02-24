"use client"

import { motion } from "framer-motion"
import { Bot, User } from "lucide-react"
import { BookCardCarousel, type BookData } from "@/components/book-card"
import { SourceCitationGroup, type SourceData } from "@/components/source-citation"

export interface ChatMessageData {
  id: string
  role: "user" | "assistant"
  content: string
  books?: BookData[]
  sources?: SourceData[]
  isStreaming?: boolean
}

export function ChatMessage({ message }: { message: ChatMessageData }) {
  const isUser = message.role === "user"

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`flex gap-3 ${isUser ? "flex-row-reverse" : "flex-row"}`}
    >
      {/* Avatar */}
      <div
        className={`flex-shrink-0 h-8 w-8 rounded-full flex items-center justify-center ${
          isUser ? "bg-primary text-primary-foreground" : "bg-accent text-accent-foreground"
        }`}
      >
        {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
      </div>

      {/* Content */}
      <div
        className={`flex flex-col gap-2 max-w-[85%] md:max-w-[70%] ${
          isUser ? "items-end" : "items-start"
        }`}
      >
        <div
          className={`rounded-2xl px-4 py-3 text-sm leading-relaxed ${
            isUser
              ? "bg-primary text-primary-foreground rounded-tr-md"
              : "bg-card text-card-foreground border border-border rounded-tl-md shadow-sm"
          }`}
        >
          <p className="whitespace-pre-wrap">{message.content}</p>
          {message.isStreaming && (
            <motion.span
              className="inline-block w-1.5 h-4 bg-accent ml-0.5 rounded-sm"
              animate={{ opacity: [1, 0, 1] }}
              transition={{ duration: 0.8, repeat: Infinity }}
            />
          )}
        </div>

        {/* Source Citations */}
        {message.sources && message.sources.length > 0 && (
          <SourceCitationGroup sources={message.sources} />
        )}

        {/* Book Cards Carousel */}
        {message.books && message.books.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="w-full mt-1"
          >
            <BookCardCarousel books={message.books} />
          </motion.div>
        )}
      </div>
    </motion.div>
  )
}
