export interface ChatMessageData {
    id: string
    role: 'user' | 'assistant'
    content: string
    books?: import('./book').BookData[]
    sources?: import('./book').SourceData[]
    isStreaming?: boolean
}
