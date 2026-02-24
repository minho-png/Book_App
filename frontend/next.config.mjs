/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',        // Docker 최적화
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
    remotePatterns: [
      { protocol: 'https', hostname: '*.kyobobook.co.kr' },
      { protocol: 'https', hostname: '*.aladin.co.kr' },
      { protocol: 'https', hostname: '*.millie.co.kr' },
    ],
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:80'}/api/:path*`,
      },
    ]
  },
}

export default nextConfig
