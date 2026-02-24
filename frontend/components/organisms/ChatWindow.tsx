'use client'

import { useRef, useEffect, useCallback } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { Sparkles } from 'lucide-react'
import { ChatBubble } from '@/components/molecules/ChatBubble'
import { RAGLoading } from '@/components/rag-loading'
import type { ChatMessageData } from '@/types/chat'

interface ChatWindowProps {
    messages: ChatMessageData[]
    isLoading: boolean
    onRAGComplete?: () => void
}

export function ChatWindow({ messages, isLoading, onRAGComplete }: ChatWindowProps) {
    const scrollRef = useRef<HTMLDivElement>(null)

    const scrollToBottom = useCallback(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight
        }
    }, [])

    useEffect(() => { scrollToBottom() }, [messages, isLoading, scrollToBottom])

    return (
        <div ref={scrollRef} className="flex-1 overflow-y-auto">
            <div className="mx-auto max-w-3xl px-4 sm:px-6 py-6">
                <div className="flex flex-col gap-6">
                    {messages.map((msg) => (
                        <ChatBubble key={msg.id} message={msg} />
                    ))}

                    {/* RAG Loading indicator while waiting for first tokens */}
                    <AnimatePresence>
                        {isLoading && messages.at(-1)?.role !== 'assistant' && (
                            <motion.div
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -10 }}
                                className="flex gap-3"
                            >
                                <div className="flex-shrink-0 h-8 w-8 rounded-full flex items-center justify-center bg-accent text-accent-foreground">
                                    <Sparkles className="h-4 w-4" />
                                </div>
                                <div className="bg-card border border-border rounded-2xl rounded-tl-md px-4 py-3 shadow-sm">
                                    <RAGLoading onComplete={onRAGComplete ?? (() => { })} />
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            </div>
        </div>
    )
}
