import type { BookData, SourceData, StreamChunk } from '@/types/book'

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:80'

// ── Books ─────────────────────────────────────────────────────────────────────

export async function fetchBooks(params?: {
    skip?: number
    limit?: number
    genre?: string
    store?: string
}): Promise<BookData[]> {
    const query = new URLSearchParams()
    if (params?.skip) query.set('skip', String(params.skip))
    if (params?.limit) query.set('limit', String(params.limit))
    if (params?.genre) query.set('genre', params.genre)
    if (params?.store) query.set('store', params.store)

    const res = await fetch(`${API_URL}/api/books?${query}`, { cache: 'no-store' })
    if (!res.ok) throw new Error(`fetchBooks failed: ${res.status}`)
    return res.json()
}

export async function fetchBook(id: number): Promise<BookData> {
    const res = await fetch(`${API_URL}/api/books/${id}`, { cache: 'no-store' })
    if (!res.ok) throw new Error(`fetchBook failed: ${res.status}`)
    return res.json()
}

export async function searchBooks(q: string): Promise<BookData[]> {
    const res = await fetch(`${API_URL}/api/books/search?q=${encodeURIComponent(q)}`, {
        cache: 'no-store',
    })
    if (!res.ok) throw new Error(`searchBooks failed: ${res.status}`)
    return res.json()
}

// ── Streaming Recommend ───────────────────────────────────────────────────────

/**
 * POST /api/recommend — NDJSON 스트리밍
 * Yields StreamChunk objects as they arrive from the backend.
 */
export async function* streamRecommend(
    query: string,
    maxBooks = 6,
    apiKey?: string,
): AsyncGenerator<StreamChunk> {
    const res = await fetch(`${API_URL}/api/recommend`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            query,
            max_books: maxBooks,
            google_api_key: apiKey
        }),
    })

    if (!res.ok || !res.body) {
        throw new Error(`streamRecommend failed: ${res.status}`)
    }

    const reader = res.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() ?? ''   // 마지막 불완전 줄 보류

        for (const line of lines) {
            const trimmed = line.trim()
            if (!trimmed) continue
            try {
                const chunk: StreamChunk = JSON.parse(trimmed)
                yield chunk
            } catch {
                // 파싱 실패 시 skip
            }
        }
    }

    // 잔여 버퍼 처리
    if (buffer.trim()) {
        try {
            const chunk: StreamChunk = JSON.parse(buffer.trim())
            yield chunk
        } catch {
            // ignore
        }
    }
}
