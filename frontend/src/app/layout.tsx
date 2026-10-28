import type { Metadata } from 'next'
import './globals.css'

/**
 * QingXi V1 根布局
 */

export const metadata: Metadata = {
  title: 'QingXi V1 - 慢热型陪伴 Agent',
  description: '通过长期真诚交流建立信任，逐步开放人格的 AI 陪伴者。V1 支持人生记忆、时间轴、洞察、反思等模块。',
  keywords: ['AI', '陪伴', '慢热', '信任', '情感', '人生记忆', '时间轴'],
  authors: [{ name: 'QingXi Team' }],
  themeColor: '#0f172a',
  viewport: 'width=device-width, initial-scale=1, maximum-scale=1',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body className="min-h-screen bg-qx-bg text-qx-text antialiased">
        {children}
      </body>
    </html>
  )
}
