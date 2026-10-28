'use client'

/**
 * 人格画像面板组件
 * 展示用户的人格画像数据
 */

import React, { useState, useEffect } from 'react'
import { Persona } from '@/types'
import { getPersona } from '@/services/api'

interface PersonaPanelProps {
  userId: string
}

export default function PersonaPanel({ userId }: PersonaPanelProps) {
  const [persona, setPersona] = useState<Persona | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true)
        const data = await getPersona(userId)
        setPersona(data)
      } catch (error) {
        console.error('加载人格画像失败:', error)
      } finally {
        setLoading(false)
      }
    }
    if (userId) load()
  }, [userId])

  if (loading) {
    return <div className="text-qx-text-muted animate-pulse text-center py-8">加载人格画像中...</div>
  }

  if (!persona || !persona.user_id) {
    return (
      <div className="text-center py-12">
        <div className="text-4xl mb-4">🪞</div>
        <div className="text-qx-text-secondary mb-2">人格画像尚未生成</div>
        <div className="text-qx-text-muted text-sm">随着交流的深入，QingXi 会慢慢了解你是一个什么样的人。</div>
      </div>
    )
  }

  // 渲染维度条
  const renderDimensionBar = (label: string, value: number, color: string) => (
    <div className="flex items-center gap-3">
      <span className="text-xs text-qx-text-muted w-16 text-right">{label}</span>
      <div className="flex-1 h-2 bg-qx-bg rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${color} transition-all duration-1000`} style={{ width: `${value * 100}%` }} />
      </div>
      <span className="text-xs text-qx-text-muted w-8">{(value * 100).toFixed(0)}%</span>
    </div>
  )

  return (
    <div className="max-w-4xl mx-auto p-4 space-y-6">
      {/* 身份摘要 */}
      <div className="bg-gradient-to-br from-qx-bg-secondary to-qx-bg p-6 rounded-2xl border border-qx-bg-tertiary">
        <div className="flex items-center gap-3 mb-4">
          <span className="text-3xl">🪪</span>
          <div>
            <h2 className="text-lg font-medium text-qx-text">人格画像</h2>
            <p className="text-xs text-qx-text-muted">基于你的言行，QingXi 对你的了解</p>
          </div>
        </div>
        <p className="text-qx-text text-sm leading-relaxed bg-qx-bg rounded-lg p-4">
          {persona.identity_summary}
        </p>
      </div>

      {/* 性格特质 */}
      <div className="bg-qx-bg-secondary rounded-2xl p-6">
        <h3 className="text-sm font-medium text-qx-text-secondary mb-4">性格特质</h3>
        <div className="flex flex-wrap gap-2">
          {persona.identity_traits.map((trait, i) => (
            <span key={i} className="px-3 py-1.5 bg-purple-500/10 text-purple-300 rounded-full text-sm border border-purple-500/20">
              {trait}
            </span>
          ))}
        </div>
      </div>

      {/* 沟通风格维度 */}
      <div className="bg-qx-bg-secondary rounded-2xl p-6">
        <h3 className="text-sm font-medium text-qx-text-secondary mb-4">沟通风格</h3>
        <div className="space-y-3">
          {renderDimensionBar('正式度', persona.comm_formality, 'bg-blue-400')}
          {renderDimensionBar('表达力', persona.comm_expressiveness, 'bg-pink-400')}
          {renderDimensionBar('直接度', persona.comm_directness, 'bg-amber-400')}
        </div>
      </div>

      {/* 思维方式维度 */}
      <div className="bg-qx-bg-secondary rounded-2xl p-6">
        <h3 className="text-sm font-medium text-qx-text-secondary mb-4">思维方式</h3>
        <div className="space-y-3">
          {renderDimensionBar('分析性', persona.thinking_analytical, 'bg-cyan-400')}
          {renderDimensionBar('创造性', persona.thinking_creative, 'bg-violet-400')}
          {renderDimensionBar('稳定性', persona.emotion_stability, 'bg-green-400')}
          {renderDimensionBar('乐观度', persona.emotion_optimism, 'bg-yellow-400')}
        </div>
      </div>

      {/* 核心价值观 */}
      <div className="bg-qx-bg-secondary rounded-2xl p-6">
        <h3 className="text-sm font-medium text-qx-text-secondary mb-4">核心价值观</h3>
        <div className="flex flex-wrap gap-2">
          {persona.values_core.map((value, i) => (
            <span key={i} className="px-3 py-1.5 bg-amber-500/10 text-amber-300 rounded-full text-sm border border-amber-500/20">
              {value}
            </span>
          ))}
        </div>
      </div>

      {/* 当前目标 & 兴趣话题 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-qx-bg-secondary rounded-2xl p-6">
          <h3 className="text-sm font-medium text-qx-text-secondary mb-4">🎯 当前目标</h3>
          <ul className="space-y-2">
            {persona.current_goals.map((goal, i) => (
              <li key={i} className="text-sm text-qx-text flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-qx-accent" />
                {goal}
              </li>
            ))}
          </ul>
        </div>
        <div className="bg-qx-bg-secondary rounded-2xl p-6">
          <h3 className="text-sm font-medium text-qx-text-secondary mb-4">💬 感兴趣的话题</h3>
          <div className="flex flex-wrap gap-2">
            {persona.preferences_topics.map((topic, i) => (
              <span key={i} className="px-2.5 py-1 bg-cyan-500/10 text-cyan-300 rounded-full text-xs border border-cyan-500/20">
                {topic}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* 成熟度 & 更新次数 */}
      <div className="flex items-center justify-between bg-qx-bg-secondary rounded-xl p-4">
        <div className="text-xs text-qx-text-muted">
          成熟度 <span className="text-qx-accent font-medium">{(persona.maturity_score * 100).toFixed(0)}%</span>
        </div>
        <div className="text-xs text-qx-text-muted">
          已更新 <span className="text-qx-accent font-medium">{persona.update_count}</span> 次
        </div>
      </div>
    </div>
  )
}
