'use client'

/**
 * 时间轴展示组件
 * 展示用户人生时间轴上的重要事件
 */

import React, { useState, useEffect } from 'react'
import { TimelineEntry } from '@/types'
import { getTimeline } from '@/services/api'

interface TimelineViewProps {
  userId: string
}

/** 时间轴条目的类型图标和颜色 */
const ENTRY_TYPE_CONFIG: Record<string, { icon: string; color: string; label: string }> = {
  event: { icon: '📅', color: 'border-amber-400/50', label: '事件' },
  memory: { icon: '💭', color: 'border-blue-400/50', label: '记忆' },
  milestone: { icon: '🏆', color: 'border-qx-accent/50', label: '里程碑' },
  emotion: { icon: '💫', color: 'border-purple-400/50', label: '情绪' },
}

export default function TimelineView({ userId }: TimelineViewProps) {
  const [entries, setEntries] = useState<TimelineEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [typeFilter, setTypeFilter] = useState<string>('all')

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true)
        const data = await getTimeline(userId, typeFilter === 'all' ? undefined : typeFilter)
        setEntries(data)
      } catch (error) {
        console.error('加载时间轴失败:', error)
      } finally {
        setLoading(false)
      }
    }
    if (userId) load()
  }, [userId, typeFilter])

  const formatDate = (dateStr: string) => {
    const d = new Date(dateStr)
    return d.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
  }

  const typeFilters = [
    { key: 'all', label: '全部', icon: '📋' },
    { key: 'event', label: '事件', icon: '📅' },
    { key: 'memory', label: '记忆', icon: '💭' },
    { key: 'emotion', label: '情绪', icon: '💫' },
  ]

  if (loading) {
    return <div className="text-qx-text-muted animate-pulse text-center py-12">加载中...</div>
  }

  return (
    <div className="max-w-3xl mx-auto p-4 space-y-6">
      {/* 页面标题 */}
      <div className="flex items-center gap-3">
        <span className="text-3xl">🕐</span>
        <div>
          <h1 className="text-xl font-medium text-qx-text">人生时间轴</h1>
          <p className="text-xs text-qx-text-muted">记录那些值得记住的瞬间</p>
        </div>
      </div>

      {/* 类型过滤器 */}
      <div className="flex gap-2">
        {typeFilters.map(f => (
          <button
            key={f.key}
            onClick={() => setTypeFilter(f.key)}
            className={`px-3 py-1.5 rounded-full text-xs transition-all duration-300 ${
              typeFilter === f.key
                ? 'bg-qx-accent/20 text-qx-accent border border-qx-accent/30'
                : 'bg-qx-bg-secondary text-qx-text-muted hover:text-qx-text border border-transparent'
            }`}
          >
            {f.icon} {f.label}
          </button>
        ))}
      </div>

      {/* 时间轴列表 */}
      {entries.length === 0 ? (
        <div className="text-center py-16">
          <div className="text-5xl mb-4">🌙</div>
          <div className="text-qx-text-secondary mb-2">时间轴还是空的</div>
          <div className="text-qx-text-muted text-sm">随着交流的深入，重要的瞬间会被一一记录。</div>
        </div>
      ) : (
        <div className="relative">
          {/* 时间轴连线 */}
          <div className="absolute left-6 top-0 bottom-0 w-px bg-qx-bg-tertiary" />
          
          <div className="space-y-6">
            {entries.map((entry, index) => {
              const typeConfig = ENTRY_TYPE_CONFIG[entry.entry_type] || ENTRY_TYPE_CONFIG.event
              return (
                <div key={entry.id} className="relative flex gap-4 animate-fade-in" style={{ animationDelay: `${index * 80}ms` }}>
                  {/* 节点圆点 */}
                  <div className={`relative z-10 flex items-center justify-center w-12 h-12 rounded-full bg-qx-bg-secondary border-2 ${typeConfig.color}`}>
                    <span className="text-lg">{typeConfig.icon}</span>
                  </div>
                  
                  {/* 内容卡片 */}
                  <div className="flex-1 bg-qx-bg-secondary rounded-xl p-4 border border-qx-bg-terti0 hover:border-qx-accent/20 transition-colors">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-xs text-qx-accent">{typeConfig.label}</span>
                      <span className="text-xs text-qx-text-muted">{formatDate(entry.occurred_at)}</span>
                      {entry.importance >= 4 && <span className="text-xs">⭐</span>}
                    </div>
                    <h3 className="text-sm font-medium text-qx-text mb-1">{entry.title}</h3>
                    <p className="text-xs text-qx-text-muted leading-relaxed">{entry.description}</p>
                    {entry.emotion_marker && (
                      <div className="mt-2 text-xs text-qx-accent/60">
                        情绪标记: {entry.emotion_marker}
                      </div>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}
