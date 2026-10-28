'use client'

/**
 * Dashboard 页面 V1
 */

import React from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useUser } from '@/hooks/useUser'
import Dashboard from '@/components/Dashboard'

export default function DashboardPage() {
  const pathname = usePathname()
  const { userId, loading: userLoading, error: userError } = useUser()

  if (userLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="text-4xl mb-4 animate-bounce-subtle">🌙</div>
          <div className="text-qx-text-muted animate-pulse">加载中...</div>
        </div>
      </div>
    )
  }

  if (userError || !userId) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center max-w-md p-6">
          <div className="text-4xl mb-4">😔</div>
          <div className="text-qx-text mb-2">{userError || '请先开始聊天'}</div>
          <Link href="/" className="mt-4 inline-block px-6 py-2 bg-qx-accent text-white rounded-full hover:bg-qx-accent-dark transition-colors">
            返回聊天
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex flex-col">
      <header className="sticky top-0 z-50 glass border-b border-qx-bg-secondary">
        <div className="max-w-6xl mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <span className="text-2xl">🌙</span>
              <div>
                <h1 className="text-lg font-medium text-qx-text">QingXi</h1>
                <div className="text-xs text-qx-accent">数据面板</div>
              </div>
            </div>
            <nav className="flex items-center gap-1 sm:gap-2 overflow-x-auto">
              <NavBtn href="/" icon="💬" label="聊天" active={pathname === '/'} />
              <NavBtn href="/dashboard" icon="📊" label="数据" active={pathname === '/dashboard'} />
              <NavBtn href="/timeline" icon="🕐" label="时间轴" active={pathname === '/timeline'} />
              <NavBtn href="/insight" icon="💡" label="洞察" active={pathname === '/insight'} />
              <NavBtn href="/reflection" icon="📖" label="回顾" active={pathname === '/reflection'} />
            </nav>
          </div>
        </div>
      </header>
      <main className="flex-1 py-6">
        <Dashboard userId={userId} />
      </main>
      <footer className="py-6 text-center">
        <div className="text-xs text-qx-text-muted/50"><span className="opacity-50">QingXi V1 · 慢热型陪伴 Agent</span></div>
      </footer>
    </div>
  )
}

function NavBtn({ href, icon, label, active }: { href: string; icon: string; label: string; active: boolean }) {
  return (
    <Link href={href}
      className={`px-3 py-2 rounded-full text-xs sm:text-sm transition-all duration-300 whitespace-nowrap ${
        active ? 'bg-qx-accent/20 text-qx-accent' : 'text-qx-text-muted hover:text-qx-text hover:bg-qx-bg-secondary'
      }`}>
      <span className="mr-1">{icon}</span>
      <span className="hidden sm:inline">{label}</span>
    </Link>
  )
}
