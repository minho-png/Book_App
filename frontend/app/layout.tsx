import type { Metadata, Viewport } from 'next'
import { Noto_Sans_KR, Noto_Serif_KR } from 'next/font/google'
import { Analytics } from '@vercel/analytics/next'
import './globals.css'

const notoSansKR = Noto_Sans_KR({
  subsets: ['latin'],
  variable: '--font-sans',
  weight: ['300', '400', '500', '700'],
})

const notoSerifKR = Noto_Serif_KR({
  subsets: ['latin'],
  variable: '--font-serif',
  weight: ['400', '600', '700'],
})

export const metadata: Metadata = {
  title: 'BookCurator AI - AI 도서 큐레이터',
  description: 'RAG 기반 AI가 교보문고, 밀리의서재, 알라딘의 랭킹 데이터를 분석하여 맞춤 도서를 추천합니다.',
  icons: {
    icon: [
      {
        url: '/icon-light-32x32.png',
        media: '(prefers-color-scheme: light)',
      },
      {
        url: '/icon-dark-32x32.png',
        media: '(prefers-color-scheme: dark)',
      },
      {
        url: '/icon.svg',
        type: 'image/svg+xml',
      },
    ],
    apple: '/apple-icon.png',
  },
}

export const viewport: Viewport = {
  themeColor: '#F5F0E8',
  userScalable: true,
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="ko">
      <body className={`${notoSansKR.variable} ${notoSerifKR.variable} font-sans antialiased`}>
        {children}
        <Analytics />
      </body>
    </html>
  )
}
