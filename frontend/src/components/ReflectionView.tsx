'use client'

/**
 * 反思回顾组件
 * 展示 QingXi 对用户过去一段时间的回顾
 */

import React, { useState, useEffect } from 'react'
import { Reflection } from '@/types'
import { getReflections } from '@/services/api'

interface ReflectionViewProps {
  userId: string
}

const REFLECTION_TYPE_CONFIG: Record<string, { icon: string; label: string; color: string }> = {
  weekly: { icon: '📅', label: '周回顾', color: 'border-blue-400/30' },
  monthly: { icon: '📆', label: '月回顾', color: 'border-purple-400/30' },
  yearly: { icon: '📚', label: '年回顾', color: 'border-amber-400/30' },
}

export default function ReflectionView({ userId }: ReflectionViewProps) {
  const [reflections, setReflections] = useState<Reflection[]>([])
  const [loading, setLoading] = useState(true)
  const [typeFilter, setTypeFilter] = useState<string>('all')

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true)
        const data = await getReflections(userId, typeFilter === 'all' ? undefined : typeFilter)
        setReflections(data)
      } catch (error) {
        console.error('加载反思回顾失败:', error)
      } finally {
        setLoading(false)
      }
    }
    if (userId) load()
  }, [userId, typeFilter])

  const typeFilters = [
    { key: 'all', label: '全部', icon: '📋' },
    { key: 'weekly', label: '周回顾', icon: '📅' },
    { key: 'monthly', label: '月回顾', icon: '📆' },
    { key: 'yearly', label: '年回顾', icon: '📚' },
  ]

  if (loading) {
    return <div className="text-qx-text-muted animate-pulse text-center py-12">加载中...</div>
  }

  return (
    <div className="max-w-3xl mx-auto p-4 space-y-6">
      <div className="flex items-center gap-3">
        <span className="text-3xl">📖</span>
        <div>
          <h1 className="text-xl font-medium text-qx-text">反思回顾</h1>
          <p className="text-xs text-qx-text-muted">回望我们一起走过的时光</p>
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

      {reflections.length === 0 ? (
        <div className="text-center py-16">
          <div className="text-5xl mb-4">📝</div>
          <div className="text-qx-text-secondary mb-2">还没有反思回顾</div>
          <div className="text-qx-text-muted text-sm">
            随着我们交流的积累，QingXi 会定期为你回顾一段时间内的点点滴滴。
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          {reflections.map((reflection, index) => {
            const typeConfig = REFLECTION_TYPE_CONFIG[reflection.reflection_type] || REFLECTION_TYPE_CONFIG.weekly
            return (
              <div
                key={reflection.id}
                className={`bg-qx-bg-secondary rounded-2xl p-6 border ${typeConfig.color} animate-fade-in`}
                style={{ animationDelay: `${index * 120}ms` }}
              >
                <div className="flex items-center gap-2 mb-4">
                  <span className="text-xl">{typeConfig.icon}</span>
                  <h3 className="text-base font-medium text-qx-text">{reflection.title}</h3>
                  <span className="text-xs text-qx-text-muted ml-auto">{typeConfig.label}</span>
                </div>
                
                {/* 时间范围 */}
                <div className="text-xs text-qx-text-muted mb-3 flex items-center gap-2">
                  <span>{new Date(reflection.period_start).toLocaleDateString('zh-CN')}</span>
                  <span>→</span>
                  <span>{new Date(reflection.period_end).toLocaleDateString('zh-CN')}</span>
                </div>

                {/* 摘要 */}
                <div className="bg-qx-bg rounded-lg p-3 mb-3">
                  <p className="text-sm text-qx-accent italic">{reflection.summary}</p>
                </div>

                {/* 详细内容 */}
                <p className="text-sm text-qx-text-secondary leading-relaxed whitespace-pre-wrap">
                  {reflection.content}
                </p>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
