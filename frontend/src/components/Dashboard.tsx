'use client'

/**
 * Dashboard 数据面板组件 V1
 * 展示用户与 QingXi 关系的各项数据，新增 V1 模块入口
 */

import React, { useState, useEffect } from 'react'
import Link from 'next/link'
import { DashboardData, AnalyticsData, Memory, RELATIONSHIP_STAGE_CONFIG, MEMORY_LAYER_CONFIG, MemoryLayer } from '@/types'
import { getDashboard, getAnalytics, getMemories } from '@/services/api'
import EmotionChart from './EmotionChart'

interface DashboardProps {
  userId: string
}

export default function Dashboard({ userId }: DashboardProps) {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null)
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null)
  const [memories, setMemories] = useState<Memory[]>([])
  const [loading, setLoading] = useState(true)
  const [layerFilter, setLayerFilter] = useState<MemoryLayer | 'all'>('all')

  // 加载数据
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true)
        const [dashboard, analytics, memoryList] = await Promise.all([
          getDashboard(userId),
          getAnalytics(userId),
          getMemories(userId, layerFilter === 'all' ? undefined : layerFilter)
        ])
        setDashboardData(dashboard)
        setAnalyticsData(analytics)
        setMemories(memoryList)
      } catch (error) {
        console.error('加载Dashboard数据失败:', error)
      } finally {
        setLoading(false)
      }
    }
    if (userId) loadData()
  }, [userId, layerFilter])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-qx-text-muted animate-pulse">加载中...</div>
      </div>
    )
  }

  if (!dashboardData) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-qx-text-muted">数据加载失败</div>
      </div>
    )
  }

  const stageConfig = RELATIONSHIP_STAGE_CONFIG[dashboardData.relationship_stage]

  // 信任成长曲线（SVG实现）
  const renderTrustCurve = () => {
    const points = dashboardData.trust_growth_curve
    if (points.length < 2) return null
    const maxScore = Math.max(...points.map(p => p.score))
    const minScore = Math.min(...points.map(p => p.score))
    const range = maxScore - minScore || 1
    const width = 100, height = 60, padding = 5
    
    const pathPoints = points.map((point, index) => {
      const x = padding + (index / (points.length - 1)) * (width - padding * 2)
      const y = height - padding - ((point.score - minScore) / range) * (height - padding * 2)
      return `${x},${y}`
    })
    const pathD = `M ${pathPoints.join(' L ')}`
    const areaD = `${pathD} L ${width - padding},${height - padding} L ${padding},${height - padding} Z`

    return (
      <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-24">
        <defs>
          <linearGradient id="trustGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#f97316" stopOpacity="0.3" />
            <stop offset="100%" stopColor="#f97316" stopOpacity="0" />
          </linearGradient>
        </defs>
        <path d={areaD} fill="url(#trustGradient)" />
        <path d={pathD} fill="none" stroke="#f97316" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        {points.map((point, index) => {
          const x = padding + (index / (points.length - 1)) * (width - padding * 2)
          const y = height - padding - ((point.score - minScore) / range) * (height - padding * 2)
          return (
            <circle key={index} cx={x} cy={y} r="2" fill="#f97316"
              className="animate-fade-in" style={{ animationDelay: `${index * 100}ms` }} />
          )
        })}
      </svg>
    )
  }

  // 记忆层级过滤器
  const layerButtons: { key: MemoryLayer | 'all'; label: string; icon: string }[] = [
    { key: 'all', label: '全部', icon: '📋' },
    ...Object.entries(MEMORY_LAYER_CONFIG).map(([key, config]) => ({
      key: key as MemoryLayer, label: config.label, icon: config.icon,
    }))
  ]

  return (
    <div className="max-w-4xl mx-auto p-4 space-y-6">
      {/* 顶部大卡片：关系阶段 + 信任分数 */}
      <div className="bg-gradient-to-br from-qx-bg-secondary to-qx-bg p-6 rounded-2xl border border-qx-bg-tertiary">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="text-5xl">
              {dashboardData.relationship_stage === 'stranger' && '🌫️'}
              {dashboardData.relationship_stage === 'acquaintance' && '🌤️'}
              {dashboardData.relationship_stage === 'friend' && '☀️'}
              {dashboardData.relationship_stage === 'confidant' && '🔥'}
            </div>
            <div>
              <div className={`text-2xl font-medium ${stageConfig.color}`}>{stageConfig.label}</div>
              <div className="text-qx-text-muted text-sm">{stageConfig.description}</div>
            </div>
          </div>
          <div className="text-right">
            <div className="text-qx-text-muted text-sm">信任分数</div>
            <div className={`text-4xl font-light ${stageConfig.color}`}>{dashboardData.trust_score}</div>
            <div className="text-qx-text-muted text-xs">/ 1000</div>
          </div>
        </div>
      </div>

      {/* V1 新模块入口卡片 */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <Link href="/timeline" className="group bg-qx-bg-secondary rounded-xl p-4 border border-qx-bg-tertiary hover:border-qx-accent/30 transition-all duration-300">
          <div className="text-2xl mb-2 group-hover:scale-110 transition-transform">🕐</div>
          <div className="text-sm font-medium text-qx-text">人生时间轴</div>
          <div className="text-xs text-qx-text-muted mt-1">记录重要的瞬间</div>
        </Link>
        <Link href="/insight" className="group bg-qx-bg-secondary rounded-xl p-4 border border-qx-bg-tertiary hover:border-qx-accent/30 transition-all duration-300">
          <div className="text-2xl mb-2 group-hover:scale-110 transition-transform">💡</div>
          <div className="text-sm font-medium text-qx-text">洞察</div>
          <div className="text-xs text-qx-text-muted mt-1">发现隐藏的模式</div>
        </Link>
        <Link href="/reflection" className="group bg-qx-bg-secondary rounded-xl p-4 border border-qx-bg-tertiary hover:border-qx-accent/30 transition-all duration-300">
          <div className="text-2xl mb-2 group-hover:scale-110 transition-transform">📖</div>
          <div className="text-sm font-medium text-qx-text">反思回顾</div>
          <div className="text-xs text-qx-text-muted mt-1">回望走过的路</div>
        </Link>
        <Link href="/import" className="group bg-qx-bg-secondary rounded-xl p-4 border border-qx-bg-tertiary hover:border-qx-accent/30 transition-all duration-300">
          <div className="text-2xl mb-2 group-hover:scale-110 transition-transform">🪪</div>
          <div className="text-sm font-medium text-qx-text">人格画像</div>
          <div className="text-xs text-qx-text-muted mt-1">导入资料，塑造你的画像</div>
        </Link>
      </div>

      {/* 统计卡片 */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard icon="💬" label="聊天次数" value={analyticsData?.total_chats || 0} unit="次" />
        <StatCard icon="📝" label="记忆数量" value={dashboardData.memory_count} unit="条" />
        <StatCard icon="⏱️" label="在一起" value={dashboardData.days_together} unit="天" />
        <StatCard icon="📈" label="信任增速" value={analyticsData?.trust_growth_speed || 0} unit="/天" decimal />
      </div>

      {/* 情绪趋势 */}
      <div className="bg-qx-bg-secondary rounded-2xl p-6">
        <EmotionChart data={dashboardData.emotion_trend} title="近7天情绪趋势" />
      </div>

      {/* 信任成长曲线 */}
      <div className="bg-qx-bg-secondary rounded-2xl p-6">
        <h3 className="text-sm font-medium text-qx-text-secondary mb-4">信任成长曲线</h3>
        <div className="text-qx-text-muted text-xs mb-2">近7天信任值变化</div>
        {renderTrustCurve()}
      </div>

      {/* 记忆列表（V1 支持按层级过滤） */}
      <div className="bg-qx-bg-secondary rounded-2xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-medium text-qx-text-secondary">记忆摘要</h3>
          <span className="text-xs text-qx-text-muted">{memories.length} 条记忆</span>
        </div>
        
        {/* 层级过滤器 */}
        <div className="flex flex-wrap gap-2 mb-4">
          {layerButtons.map(btn => (
            <button
              key={btn.key}
              onClick={() => setLayerFilter(btn.key)}
              className={`px-3 py-1 rounded-full text-xs transition-all duration-300 ${
                layerFilter === btn.key
                  ? 'bg-qx-accent/20 text-qx-accent border border-qx-accent/30'
                  : 'bg-qx-bg text-qx-text-muted hover:text-qx-text border border-transparent'
              }`}
            >
              {btn.icon} {btn.label}
            </button>
          ))}
        </div>

        {memories.length === 0 ? (
          <div className="text-qx-text-muted text-sm text-center py-8">
            {layerFilter === 'all' ? '还没有记录任何记忆' : `暂无${MEMORY_LAYER_CONFIG[layerFilter as MemoryLayer]?.label || ''}类记忆`}
          </div>
        ) : (
          <div className="space-y-3">
            {memories.map((memory) => {
              const layerConfig = MEMORY_LAYER_CONFIG[memory.layer]
              return (
                <div key={memory.id} className="flex items-start gap-3 p-3 bg-qx-bg rounded-lg animate-fade-in">
                  <div className="text-lg">{layerConfig?.icon || '📌'}</div>
                  <div className="flex-1">
                    <div className="text-sm text-qx-text">{memory.content}</div>
                    <div className="flex items-center gap-2 mt-1 flex-wrap">
                      <span className={`text-xs ${layerConfig?.color || 'text-qx-accent'}`}>
                        {layerConfig?.label || memory.category}
                      </span>
                      <span className="text-xs text-qx-text-muted">
                        来源: {memory.source === 'chat' ? '对话' : memory.source === 'import' ? '导入' : memory.source}
                      </span>
                      <span className="text-xs text-qx-text-muted">
                        置信度: {(memory.confidence * 100).toFixed(0)}%
                      </span>
                      <span className="text-xs text-qx-text-muted">
                        {new Date(memory.created_at).toLocaleDateString('zh-CN')}
                      </span>
                    </div>
                  </div>
                  <div className="flex gap-0.5">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <span key={star} className={`text-xs ${star <= memory.importance ? 'text-stage-friend' : 'text-qx-bg-tertiary'}`}>
                        ★
                      </span>
                    ))}
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}

function StatCard({ icon, label, value, unit, decimal = false }: {
  icon: string; label: string; value: number; unit: string; decimal?: boolean
}) {
  return (
    <div className="bg-qx-bg-secondary rounded-xl p-4 text-center">
      <div className="text-2xl mb-1">{icon}</div>
      <div className="text-xl font-medium text-qx-text">
        {decimal ? value.toFixed(1) : value}
        <span className="text-xs text-qx-text-muted ml-1">{unit}</span>
      </div>
      <div className="text-xs text-qx-text-muted">{label}</div>
    </div>
  )
}
