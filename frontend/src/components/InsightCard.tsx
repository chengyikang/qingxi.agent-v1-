'use client'

/**
 * 洞察卡片组件
 * 展示 QingXi 对用户的观察和洞察
 */

import React, { useState, useEffect } from 'react'
import { Insight } from '@/types'
import { getInsights } from '@/services/api'

interface InsightCardProps {
  userId: string
}

/** 洞察类型配置 */
const INSIGHT_TYPE_CONFIG: Record<string, { icon: string; color: string; label: string }> = {
  weekly: { icon: '📊', color: 'bg-blue-500/10 border-blue-500/20 text-blue-300', label: '周洞察' },
  monthly: { icon: '📈', color: 'bg-purple-500/10 border-purple-500/20 text-purple-300', label: '月洞察' },
  behavioral: { icon: '🔍', color: 'bg-cyan-500/10 border-cyan-500/20 text-cyan-300', label: '行为洞察' },
  pattern: { icon: '🧩', color: 'bg-amber-500/10 border-amber-500/20 text-amber-300', label: '模式洞察' },
}

export default function InsightCard({ userId }: InsightCardProps) {
  const [insights, setInsights] = useState<Insight[]>([])
  const [loading, setLoading] = useState(true)
  const [typeFilter, setTypeFilter] = useState<string>('all')

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true)
        const data = await getInsights(userId, typeFilter === 'all' ? undefined : typeFilter)
        setInsights(data)
      } catch (error) {
        console.error('加载洞察失败:', error)
      } finally {
        setLoading(false)
      }
    }
    if (userId) load()
  }, [userId, typeFilter])

  const typeFilters = [
    { key: 'all', label: '全部', icon: '📋' },
    { key: 'behavioral', label: '行为', icon: '🔍' },
    { key: 'pattern', label: '模式', icon: '🧩' },
    { key: 'weekly', label: '周度', icon: '📊' },
  ]

  if (loading) {
    return <div className="text-qx-text-muted animate-pulse text-center py-12">加载中...</div>
  }

  return (
    <div className="max-w-3xl mx-auto p-4 space-y-6">
      <div className="flex items-center gap-3">
        <span className="text-3xl">💡</span>
        <div>
          <h1 className="text-xl font-medium text-qx-text">洞察</h1>
          <p className="text-xs text-qx-text-muted">QingXi 对你的一些观察</p>
        </div>
      </div>

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

      {insights.length === 0 ? (
        <div className="text-center py-16">
          <div className="text-5xl mb-4">🔮</div>
          <div className="text-qx-text-secondary mb-2">还没有生成洞察</div>
          <div className="text-qx-text-muted text-sm">当积累了足够的交流数据后，QingXi 会尝试发现一些关于你的模式和规律。</div>
        </div>
      ) : (
        <div className="space-y-4">
          {insights.map((insight, index) => {
            const typeConfig = INSIGHT_TYPE_CONFIG[insight.insight_type] || INSIGHT_TYPE_CONFIG.pattern
            return (
              <div
                key={insight.id}
                className={`rounded-xl p-5 border animate-fade-in ${typeConfig.color}`}
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <div className="flex items-center gap-2 mb-3">
                  <span className="text-lg">{typeConfig.icon}</span>
                  <h3 className="text-sm font-medium text-qx-text">{insight.title}</h3>
                  <span className="text-xs text-qx-text-muted ml-auto">
                    {new Date(insight.created_at).toLocaleDateString('zh-CN')}
                  </span>
                </div>
                <p className="text-sm text-qx-text-secondary leading-relaxed mb-3">{insight.content}</p>
                <div className="flex items-center gap-4 text-xs text-qx-text-muted">
                  <span>置信度: {(insight.confidence * 100).toFixed(0)}%</span>
                  <span>基于 {insight.based_on_count} 次观察</span>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
