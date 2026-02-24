'use client'

import { useState, useCallback, useRef } from 'react'
import { streamRecommend } from '@/lib/api'
import type { BookData, SourceData } from '@/types/book'
import type { ChatMessageData } from '@/types/chat'

export function useStream() {
    const [messages, setMessages] = useState<ChatMessageData[]>([])
    const [isLoading, setIsLoading] = useState(false)
    const abortRef = useRef<AbortController | null>(null)

    const updateLastAssistantMsg = useCallback(
        (updater: (prev: ChatMessageData) => ChatMessageData) => {
            setMessages((prev) => {
                const copy = [...prev]
                const lastIdx = copy.findLastIndex((m) => m.role === 'assistant')
                if (lastIdx === -1) return prev
                copy[lastIdx] = updater(copy[lastIdx])
                return copy
            })
        },
        []
    )

    const sendMessage = useCallback(async (query: string) => {
        // 사용자 메시지 추가
        const userId = `user-${Date.now()}`
        const assistantId = `assistant-${Date.now()}`

        setMessages((prev) => [
            ...prev,
            { id: userId, role: 'user', content: query },
            { id: assistantId, role: 'assistant', content: '', isStreaming: true },
        ])
        setIsLoading(true)

        try {
            const apiKey = localStorage.getItem('google_api_key') || ''

            if (!apiKey) {
                updateLastAssistantMsg((msg) => ({
                    ...msg,
                    content: '⚠️ Google API Key가 설정되지 않았습니다. 사이드바 하단 설정에서 API Key를 입력해주세요.',
                    isStreaming: false,
                }))
                setIsLoading(false)
                return
            }

            const generator = streamRecommend(query, 6, apiKey)

            for await (const chunk of generator) {
                switch (chunk.type) {
                    case 'text':
                        updateLastAssistantMsg((msg) => ({
                            ...msg,
                            content: msg.content + (chunk.data as string),
                        }))
                        break

                    case 'books':
                        updateLastAssistantMsg((msg) => ({
                            ...msg,
                            books: chunk.data as BookData[],
                        }))
                        break

                    case 'sources':
                        updateLastAssistantMsg((msg) => ({
                            ...msg,
                            sources: chunk.data as SourceData[],
                        }))
                        break

                    case 'done':
                        updateLastAssistantMsg((msg) => ({ ...msg, isStreaming: false }))
                        break

                    case 'error':
                        updateLastAssistantMsg((msg) => ({
                            ...msg,
                            content: msg.content + '\n\n⚠️ 오류가 발생했습니다. 잠시 후 다시 시도해주세요.',
                            isStreaming: false,
                        }))
                        break
                }
            }
        } catch (err) {
            console.error('Stream error:', err)
            updateLastAssistantMsg((msg) => ({
                ...msg,
                content: '⚠️ 서버 연결에 실패했습니다. 잠시 후 다시 시도해주세요.',
                isStreaming: false,
            }))
        } finally {
            setIsLoading(false)
        }
    }, [updateLastAssistantMsg])

    const clearMessages = useCallback(() => {
        setMessages([])
    }, [])

    return { messages, isLoading, sendMessage, clearMessages }
}
