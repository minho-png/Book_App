// Book & ranking types
export interface BookRanking {
  store: 'kyobo' | 'millie' | 'aladdin' | string
  category: string
  rank: number
}

export interface BookData {
  id: string
  title: string
  author: string
  genre?: string
  rating?: number
  description?: string
  cover_color?: string
  image_url?: string
  rankings: Record<string, number>  // store -> rank
  crawled_at?: string
}

export interface SourceData {
  store: 'kyobo' | 'millie' | 'aladdin' | string
  category: string
  confidence: number
}

// Streaming chunk types
export type StreamChunkType = 'text' | 'books' | 'sources' | 'done' | 'error'

export interface StreamChunk {
  type: StreamChunkType
  data: string | BookData[] | SourceData[] | null
}

// Crawl
export interface CrawlStatus {
  id: number
  store: string
  status: 'running' | 'done' | 'error'
  books_found: number
  error_message?: string
  started_at: string
  finished_at?: string
}
