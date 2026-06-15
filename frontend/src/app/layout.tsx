import type { Metadata } from 'next'
import './globals.css'

/**
 * QingXi 根布局
 * 配置全局字体和样式
 */

export const metadata: Metadata = {
  title: 'QingXi - 慢热型陪伴 Agent',
  description: '通过长期真诚交流建立信任，逐步开放人格的 AI 陪伴者',
  keywords: ['AI', '陪伴', '慢热', '信任', '情感'],
  authors: [{ name: 'QingXi Team' }],
  themeColor: '#0f172a',
  viewport: 'width=device-width, initial-scale=1, maximum-scale=1',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-CN">
      <body className="min-h-screen bg-qx-bg text-qx-text antialiased">
        {children}
      </body>
    </html>
  )
}
