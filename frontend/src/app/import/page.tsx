'use client'

/**
 * 人生资料导入页面
 * 支持文本粘贴和文件上传两种方式，解析后展示结构化的人格数据
 */

import React, { useState, useRef, useCallback } from 'react'
import Link from 'next/link'
import { useUser } from '@/hooks/useUser'
import { importFromText, importFromFile, getImportHistory } from '@/services/api'

// 来源类型选项
const SOURCE_TYPES = [
  { value: 'auto', label: '自动检测', icon: '🔍' },
  { value: 'qq_chat', label: 'QQ聊天', icon: '💬' },
  { value: 'wechat_chat', label: '微信聊天', icon: '💚' },
  { value: 'txt', label: 'TXT文本', icon: '📄' },
  { value: 'markdown', label: 'Markdown', icon: '📝' },
  { value: 'diary', label: '日记', icon: '📔' },
  { value: 'note', label: '笔记', icon: '📒' },
]

// 导入中的颜文字提示
const LOADING_MESSAGES = [
  '（◔◡◦）正在仔细阅读...',
  '（◔◡◦）一字一句地读着...',
  '（◔◡◦）在字里行间寻找你的痕迹...',
  '（◔◡◦）认真记录每一个重要的人...',
  '（◔◡◦）试着理解你的世界...',
]

// 解析结果的类别配置
const PARSED_CATEGORIES = [
  { key: 'people', icon: '👥', label: '人物关系', color: 'text-blue-400' },
  { key: 'interests', icon: '🎯', label: '兴趣爱好', color: 'text-green-400' },
  { key: 'goals', icon: '🌟', label: '人生目标', color: 'text-yellow-400' },
  { key: 'dreams', icon: '💭', label: '梦想', color: 'text-purple-400' },
  { key: 'emotions', icon: '😢', label: '情绪模式', color: 'text-pink-400' },
  { key: 'life_events', icon: '📅', label: '人生事件', color: 'text-orange-400' },
  { key: 'growth', icon: '🌱', label: '成长轨迹', color: 'text-emerald-400' },
  { key: 'values', icon: '💎', label: '价值观', color: 'text-cyan-400' },
]

// 解析结果数据类型
interface ParsedData {
  people: { name: string; relation: string; mentions: number }[]
  interests: { name: string; level: string; evidence: string }[]
  goals: { goal: string; status: string }[]
  dreams: { dream: string; importance: string }[]
  emotions: { pattern: string; frequency: string; context: string }[]
  life_events: { title: string; time: string; type: string; impact: string }[]
  growth: { area: string; description: string }[]
  values: { value: string; importance: string }[]
  [key: string]: any
}

interface ImportResult {
  import_id: string
  source_type: string
  parsed_data: ParsedData
  memories_created: number
  events_created: number
}

export default function ImportPage() {
  const { userId } = useUser()

  // 状态管理
  const [activeTab, setActiveTab] = useState<'text' | 'file'>('text')
  const [textContent, setTextContent] = useState('')
  const [sourceType, setSourceType] = useState('auto')
  const [isImporting, setIsImporting] = useState(false)
  const [importResult, setImportResult] = useState<ImportResult | null>(null)
  const [importError, setImportError] = useState<string | null>(null)
  const [loadingMsgIndex, setLoadingMsgIndex] = useState(0)
  const [importHistory, setImportHistory] = useState<any[]>([])
  const [historyLoaded, setHistoryLoaded] = useState(false)

  // 拖拽相关状态
  const [isDragging, setIsDragging] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // 拖拽事件处理
  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const files = e.dataTransfer.files
    if (files.length > 0) {
      setSelectedFile(files[0])
    }
  }, [])

  // 文件选择处理
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files.length > 0) {
      setSelectedFile(files[0])
    }
  }

  // 执行导入
  const handleImport = async () => {
    if (!userId) return
    setIsImporting(true)
    setImportError(null)
    setImportResult(null)

    // 轮播加载颜文字
    const msgInterval = setInterval(() => {
      setLoadingMsgIndex(prev => (prev + 1) % LOADING_MESSAGES.length)
    }, 2000)

    try {
      let result: ImportResult
      if (activeTab === 'text') {
        if (!textContent.trim()) {
          setImportError('请先粘贴一些文字内容')
          setIsImporting(false)
          clearInterval(msgInterval)
          return
        }
        result = await importFromText(userId, textContent, sourceType)
      } else {
        if (!selectedFile) {
          setImportError('请先选择一个文件')
          setIsImporting(false)
          clearInterval(msgInterval)
          return
        }
        result = await importFromFile(userId, selectedFile) as ImportResult
      }
      setImportResult(result)
      // 导入成功后加载历史
      loadHistory()
    } catch (err: any) {
      setImportError(err.message || '导入失败，请稍后再试')
    } finally {
      setIsImporting(false)
      clearInterval(msgInterval)
    }
  }

  // 加载导入历史
  const loadHistory = async () => {
    if (!userId) return
    try {
      const history = await getImportHistory(userId)
      setImportHistory(history)
      setHistoryLoaded(true)
    } catch (err) {
      console.error('加载导入历史失败:', err)
    }
  }

  // 重置状态
  const handleReset = () => {
    setTextContent('')
    setSelectedFile(null)
    setImportResult(null)
    setImportError(null)
    setSourceType('auto')
  }

  return (
    <div className="max-w-4xl mx-auto p-4 space-y-6 animate-fade-in">
      {/* 顶部导航 */}
      <div className="flex items-center gap-3">
        <Link href="/dashboard" className="text-qx-text-muted hover:text-qx-text transition-colors">
          ← 返回
        </Link>
      </div>

      {/* 页面标题 */}
      <div className="text-center py-4">
        <div className="text-4xl mb-3">📥</div>
        <h1 className="text-2xl font-medium text-qx-text">人生资料导入</h1>
        <p className="text-sm text-qx-text-muted mt-2">
          把你的聊天记录、日记、笔记交给我，让我更了解你一些
        </p>
        <p className="text-xs text-qx-text-muted/50 mt-1">
          （◕‿◕✿）我会认真读的
        </p>
      </div>

      {/* ====== 导入区域 ====== */}
      <div className="bg-qx-bg-secondary rounded-2xl p-6 border border-qx-bg-tertiary">
        {/* Tab 切换 */}
        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setActiveTab('text')}
            className={`px-4 py-2 rounded-lg text-sm transition-all duration-300 ${
              activeTab === 'text'
                ? 'bg-qx-accent/20 text-qx-accent border border-qx-accent/30'
                : 'text-qx-text-muted hover:text-qx-text bg-qx-bg border border-transparent'
            }`}
          >
            📝 粘贴文本
          </button>
          <button
            onClick={() => setActiveTab('file')}
            className={`px-4 py-2 rounded-lg text-sm transition-all duration-300 ${
              activeTab === 'file'
                ? 'bg-qx-accent/20 text-qx-accent border border-qx-accent/30'
                : 'text-qx-text-muted hover:text-qx-text bg-qx-bg border border-transparent'
            }`}
          >
            📁 上传文件
          </button>
        </div>

        {/* 文本粘贴区 */}
        {activeTab === 'text' && (
          <div className="space-y-4">
            <textarea
              value={textContent}
              onChange={(e) => setTextContent(e.target.value)}
              placeholder="在这里粘贴你的聊天记录、日记、笔记或任何想让我了解的文字...&#10;&#10;比如：&#10;- QQ/微信的聊天记录导出&#10;- 你的日记或随笔&#10;- 关于自己的笔记&#10;- 任何记录了你想法和生活的文字"
              className="w-full h-48 p-4 bg-qx-bg rounded-xl border border-qx-bg-tertiary text-qx-text text-sm placeholder:text-qx-text-muted/50 resize-none focus:outline-none focus:border-qx-accent/30 transition-colors"
              disabled={isImporting}
            />
            <div className="flex items-center justify-between text-xs text-qx-text-muted">
              <span>已输入 {textContent.length} 字</span>
              <span>建议 100 字以上，信息越丰富解析越准确</span>
            </div>
          </div>
        )}

        {/* 文件上传区 */}
        {activeTab === 'file' && (
          <div className="space-y-4">
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`w-full h-48 flex flex-col items-center justify-center rounded-xl border-2 border-dashed cursor-pointer transition-all duration-300 ${
                isDragging
                  ? 'border-qx-accent bg-qx-accent/5'
                  : selectedFile
                  ? 'border-green-500/50 bg-green-500/5'
                  : 'border-qx-bg-tertiary hover:border-qx-accent/30'
              }`}
            >
              {selectedFile ? (
                <div className="text-center">
                  <div className="text-3xl mb-2">✅</div>
                  <div className="text-sm text-qx-text">{selectedFile.name}</div>
                  <div className="text-xs text-qx-text-muted mt-1">
                    {(selectedFile.size / 1024).toFixed(1)} KB · 点击重新选择
                  </div>
                </div>
              ) : (
                <div className="text-center">
                  <div className="text-3xl mb-2">📄</div>
                  <div className="text-sm text-qx-text-muted">
                    拖拽文件到此处，或点击选择
                  </div>
                  <div className="text-xs text-qx-text-muted/50 mt-2">
                    支持 .txt .md .pdf .docx 格式
                  </div>
                </div>
              )}
            </div>
            <input
              ref={fileInputRef}
              type="file"
              accept=".txt,.md,.pdf,.docx"
              onChange={handleFileSelect}
              className="hidden"
            />
          </div>
        )}

        {/* 来源类型选择 + 操作按钮 */}
        <div className="flex flex-wrap items-center gap-4 mt-6">
          <div className="flex items-center gap-2">
            <span className="text-sm text-qx-text-muted">来源：</span>
            <select
              value={sourceType}
              onChange={(e) => setSourceType(e.target.value)}
              className="bg-qx-bg border border-qx-bg-tertiary rounded-lg px-3 py-2 text-sm text-qx-text focus:outline-none focus:border-qx-accent/30 transition-colors"
              disabled={isImporting}
            >
              {SOURCE_TYPES.map(type => (
                <option key={type.value} value={type.value}>
                  {type.icon} {type.label}
                </option>
              ))}
            </select>
          </div>
          <div className="flex gap-2 ml-auto">
            {importResult && (
              <button
                onClick={handleReset}
                className="px-5 py-2 rounded-full text-sm border border-qx-bg-tertiary text-qx-text-muted hover:text-qx-text hover:border-qx-accent/30 transition-all duration-300"
                disabled={isImporting}
              >
                重新导入
              </button>
            )}
            <button
              onClick={handleImport}
              disabled={isImporting}
              className={`px-6 py-2 rounded-full text-sm font-medium transition-all duration-300 ${
                isImporting
                  ? 'bg-qx-bg-tertiary text-qx-text-muted cursor-not-allowed'
                  : 'bg-qx-accent text-white hover:bg-qx-accent-dark shadow-lg shadow-qx-accent/20'
              }`}
            >
              {isImporting ? '导入中...' : '📥 开始导入'}
            </button>
          </div>
        </div>
      </div>

      {/* ====== 导入状态区 ====== */}
      {isImporting && (
        <div className="bg-qx-bg-secondary rounded-2xl p-8 border border-qx-bg-tertiary text-center animate-fade-in">
          <div className="text-4xl mb-4 animate-pulse">📖</div>
          <div className="text-qx-text text-sm transition-all duration-500">
            {LOADING_MESSAGES[loadingMsgIndex]}
          </div>
          <div className="mt-4 w-48 mx-auto h-1 bg-qx-bg-tertiary rounded-full overflow-hidden">
            <div className="h-full bg-qx-accent rounded-full animate-loading-bar"></div>
          </div>
        </div>
      )}

      {/* ====== 导入错误 ====== */}
      {importError && (
        <div className="bg-red-500/5 border border-red-500/20 rounded-2xl p-6 text-center animate-fade-in">
          <div className="text-3xl mb-2">（；◡◡）</div>
          <div className="text-red-400 text-sm">{importError}</div>
          <button
            onClick={() => setImportError(null)}
            className="mt-3 text-xs text-qx-text-muted hover:text-qx-text transition-colors"
          >
            知道了
          </button>
        </div>
      )}

      {/* ====== 解析结果展示区 ====== */}
      {importResult && !isImporting && (
        <div className="space-y-4 animate-fade-in">
          {/* 结果概览 */}
          <div className="bg-qx-bg-secondary rounded-2xl p-6 border border-qx-bg-tertiary">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <span className="text-2xl">(◕‿◕✿)</span>
                <h2 className="text-lg font-medium text-qx-text">解析完成</h2>
              </div>
              <div className="flex items-center gap-4 text-xs text-qx-text-muted">
                <span>📝 新增记忆 {importResult.memories_created} 条</span>
                <span>📅 新增事件 {importResult.events_created} 条</span>
              </div>
            </div>
            <div className="text-xs text-qx-text-muted">
              来源类型：{SOURCE_TYPES.find(t => t.value === importResult.source_type)?.label || importResult.source_type}
            </div>
          </div>

          {/* 各分类卡片 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {PARSED_CATEGORIES.map(category => {
              const items = importResult.parsed_data[category.key]
              if (!items || items.length === 0) return null
              return (
                <div
                  key={category.key}
                  className="bg-qx-bg-secondary rounded-xl p-5 border border-qx-bg-tertiary animate-fade-in"
                >
                  <div className="flex items-center gap-2 mb-3">
                    <span className="text-lg">{category.icon}</span>
                    <span className={`text-sm font-medium ${category.color}`}>{category.label}</span>
                    <span className="text-xs text-qx-text-muted ml-auto">{items.length} 项</span>
                  </div>
                  <div className="space-y-2">
                    {items.map((item: any, index: number) => (
                      <div
                        key={index}
                        className="p-3 bg-qx-bg rounded-lg text-sm animate-fade-in"
                        style={{ animationDelay: `${index * 80}ms` }}
                      >
                        {/* 人物 */}
                        {category.key === 'people' && (
                          <div className="flex items-center justify-between">
                            <span className="text-qx-text font-medium">{item.name}</span>
                            <div className="flex items-center gap-2">
                              <span className="text-xs text-qx-text-muted">{item.relation}</span>
                              <span className="text-xs text-qx-accent">提及 {item.mentions} 次</span>
                            </div>
                          </div>
                        )}
                        {/* 兴趣 */}
                        {category.key === 'interests' && (
                          <div>
                            <div className="flex items-center justify-between">
                              <span className="text-qx-text font-medium">{item.name}</span>
                              <span className={`text-xs px-2 py-0.5 rounded-full ${
                                item.level === 'high' ? 'bg-red-500/10 text-red-400' :
                                item.level === 'medium' ? 'bg-yellow-500/10 text-yellow-400' :
                                'bg-blue-500/10 text-blue-400'
                              }`}>
                                {item.level === 'high' ? '热爱' : item.level === 'medium' ? '喜欢' : '偶尔'}
                              </span>
                            </div>
                            <div className="text-xs text-qx-text-muted mt-1">{item.evidence}</div>
                          </div>
                        )}
                        {/* 目标 */}
                        {category.key === 'goals' && (
                          <div className="flex items-center justify-between">
                            <span className="text-qx-text">🎯 {item.goal}</span>
                            <span className={`text-xs px-2 py-0.5 rounded-full ${
                              item.status === 'active' ? 'bg-green-500/10 text-green-400' : 'bg-gray-500/10 text-gray-400'
                            }`}>
                              {item.status === 'active' ? '进行中' : '已完成'}
                            </span>
                          </div>
                        )}
                        {/* 梦想 */}
                        {category.key === 'dreams' && (
                          <div className="flex items-center justify-between">
                            <span className="text-qx-text">✨ {item.dream}</span>
                            <span className={`text-xs ${
                              item.importance === 'high' ? 'text-yellow-400' : 'text-qx-text-muted'
                            }`}>
                              {item.importance === 'high' ? '★★★' : item.importance === 'medium' ? '★★' : '★'}
                            </span>
                          </div>
                        )}
                        {/* 情绪 */}
                        {category.key === 'emotions' && (
                          <div>
                            <div className="text-qx-text">{item.pattern}</div>
                            <div className="text-xs text-qx-text-muted mt-1">
                              频率：{item.frequency === 'frequent' ? '经常' : item.frequency === 'occasional' ? '偶尔' : '罕见'} · {item.context}
                            </div>
                          </div>
                        )}
                        {/* 人生事件 */}
                        {category.key === 'life_events' && (
                          <div className="flex items-center justify-between">
                            <span className="text-qx-text">{item.title}</span>
                            <div className="flex items-center gap-2">
                              <span className="text-xs text-qx-text-muted">{item.time}</span>
                              <span className={`text-xs ${
                                item.impact === 'high' ? 'text-orange-400' : 'text-qx-text-muted'
                              }`}>
                                {item.impact === 'high' ? '影响大' : item.impact === 'medium' ? '影响中' : '影响小'}
                              </span>
                            </div>
                          </div>
                        )}
                        {/* 成长 */}
                        {category.key === 'growth' && (
                          <div>
                            <div className="text-qx-text font-medium">{item.area}</div>
                            <div className="text-xs text-qx-text-muted mt-1">{item.description}</div>
                          </div>
                        )}
                        {/* 价值观 */}
                        {category.key === 'values' && (
                          <div className="flex items-center justify-between">
                            <span className="text-qx-text font-medium">💎 {item.value}</span>
                            <span className={`text-xs ${
                              item.importance === 'high' ? 'text-cyan-400' : 'text-qx-text-muted'
                            }`}>
                              {item.importance === 'high' ? '核心' : '重要'}
                            </span>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* ====== 导入历史 ====== */}
      <div className="bg-qx-bg-secondary rounded-2xl p-6 border border-qx-bg-tertiary">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-medium text-qx-text-secondary flex items-center gap-2">
            📋 导入历史
          </h3>
          {!historyLoaded && (
            <button
              onClick={loadHistory}
              className="text-xs text-qx-accent hover:underline"
            >
              加载历史
            </button>
          )}
        </div>

        {historyLoaded && importHistory.length === 0 && (
          <div className="text-center py-6 text-qx-text-muted text-sm">
            还没有导入记录
          </div>
        )}

        {importHistory.length > 0 && (
          <div className="space-y-2">
            {importHistory.map((item: any) => (
              <div key={item.id} className="flex items-center justify-between p-3 bg-qx-bg rounded-lg">
                <div className="flex items-center gap-3">
                  <span className="text-lg">
                    {item.source_type === 'qq_chat' ? '💬' :
                     item.source_type === 'wechat_chat' ? '💚' :
                     item.source_type === 'txt' ? '📄' : '📝'}
                  </span>
                  <div>
                    <div className="text-sm text-qx-text">{item.file_name || '未命名'}</div>
                    <div className="text-xs text-qx-text-muted">
                      {new Date(item.created_at).toLocaleDateString('zh-CN')} · 
                      记忆 {item.extracted_memory_count} 条 · 
                      事件 {item.extracted_event_count} 条
                    </div>
                  </div>
                </div>
                <span className={`text-xs px-2 py-1 rounded-full ${
                  item.status === 'completed'
                    ? 'bg-green-500/10 text-green-400'
                    : item.status === 'failed'
                    ? 'bg-red-500/10 text-red-400'
                    : 'bg-yellow-500/10 text-yellow-400'
                }`}>
                  {item.status === 'completed' ? '已完成' : item.status === 'failed' ? '失败' : '处理中'}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 底部提示 */}
      <div className="text-center py-4">
        <p className="text-xs text-qx-text-muted/50">
          所有数据仅保存在你的本地数据库中，不会被上传到其他地方
        </p>
      </div>
    </div>
  )
}
