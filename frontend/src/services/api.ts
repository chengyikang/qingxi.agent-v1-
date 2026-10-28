/**
 * QingXi V1 API 服务封装
 * 负责与后端V1 API的所有交互，包含V1新模块接口
 */

import {
  User,
  ChatMessage,
  TrustProfile,
  Memory,
  EmotionLog,
  DashboardData,
  AnalyticsData,
  SendMessageResponse,
  RelationshipStage,
  Persona,
  TimelineEntry,
  Insight,
  Reflection,
  LifeProfile,
  RelationshipContext,
  RelationshipMilestone,
} from '@/types'

// API基础URL
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// 是否使用Mock数据
const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK === 'true'

// Mock数据存储
let mockUserId = ''
let mockTrustScore = 120
let mockMessages: ChatMessage[] = []
let mockTrustHistory: { date: string; score: number }[] = []
let mockEmotionHistory: { date: string; emotion: string }[] = []

/**
 * 从后端统一响应 {ok, data} 中提取 data
 */
function extractData<T>(result: any): T {
  if (result && typeof result === 'object' && 'ok' in result && 'data' in result) {
    return result.data as T
  }
  return result as T
}

/** 生成唯一ID */
function generateId(): string {
  return Date.now().toString(36) + Math.random().toString(36).substr(2)
}

/** 获取关系阶段 */
function getRelationshipStage(score: number): RelationshipStage {
  if (score >= 750) return 'confidant'
  if (score >= 500) return 'friend'
  if (score >= 250) return 'acquaintance'
  return 'stranger'
}

/** 初始化Mock数据 */
function initMockData(userId: string) {
  if (mockMessages.length > 0) return
  mockUserId = userId
  const now = new Date()
  
  for (let i = 6; i >= 0; i--) {
    const date = new Date(now)
    date.setDate(date.getDate() - i)
    mockTrustHistory.push({
      date: date.toISOString().split('T')[0],
      score: 100 + Math.floor(i * 15) + Math.floor(Math.random() * 10)
    })
  }
  
  const emotions = ['calm', 'happy', 'thoughtful', 'calm', 'happy', 'neutral', 'calm']
  for (let i = 6; i >= 0; i--) {
    const date = new Date(now)
    date.setDate(date.getDate() - i)
    mockEmotionHistory.push({
      date: date.toISOString().split('T')[0],
      emotion: emotions[6 - i]
    })
  }
  
  mockMessages = [
    {
      id: '1', user_id: userId, role: 'assistant',
      content: '你好，我是 QingXi。很高兴认识你。',
      created_at: new Date(now.getTime() - 3600000 * 24).toISOString()
    },
    {
      id: '2', user_id: userId, role: 'user',
      content: '你好，QingXi！',
      created_at: new Date(now.getTime() - 3600000 * 23).toISOString()
    },
    {
      id: '3', user_id: userId, role: 'assistant',
      content: '😊 今天过得怎么样？',
      created_at: new Date(now.getTime() - 3600000 * 22).toISOString()
    }
  ]
}

// ==================== 用户 API ====================

/** 创建新用户 */
export async function createUser(): Promise<{ user_id: string; nickname: string }> {
  if (USE_MOCK) {
    const userId = generateId()
    initMockData(userId)
    return { user_id: userId, nickname: '新朋友' }
  }
  const response = await fetch(`${API_BASE}/api/user/create`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  })
  if (!response.ok) throw new Error('创建用户失败')
  const result = await response.json()
  return extractData<{ user_id: string; nickname: string }>(result)
}

/** 获取用户资料 */
export async function getUserProfile(userId: string): Promise<User> {
  if (USE_MOCK) {
    return {
      id: userId, nickname: '新朋友',
      created_at: new Date(Date.now() - 86400000 * 7).toISOString(),
      last_active_at: new Date().toISOString()
    }
  }
  const response = await fetch(`${API_BASE}/api/user/profile?user_id=${userId}`)
  if (!response.ok) throw new Error('获取用户资料失败')
  const result = await response.json()
  return extractData<User>(result)
}

// ==================== 聊天 API ====================

/** 发送聊天消息 */
export async function sendMessage(userId: string, message: string): Promise<SendMessageResponse> {
  if (USE_MOCK) {
    const responses = [
      '嗯，我听到了。',
      '这样啊，我理解你的感受。',
      '谢谢你愿意和我分享这些。',
      '慢慢来，不用着急。',
      '我在这里陪着你。',
      '你的想法很有意思。',
      '我会记住这些的。',
    ]
    const randomResponse = responses[Math.floor(Math.random() * responses.length)]
    const trustChange = Math.floor(Math.random() * 5) + 1
    mockTrustScore = Math.min(1000, mockTrustScore + trustChange)
    
    mockMessages.push({
      id: generateId(), user_id: userId, role: 'user',
      content: message, created_at: new Date().toISOString()
    })
    mockMessages.push({
      id: generateId(), user_id: userId, role: 'assistant',
      content: randomResponse, created_at: new Date().toISOString()
    })
    
    return { reply: randomResponse, trust_change: trustChange, emotion: 'calm', confidence: 0.85 }
  }

  const response = await fetch(`${API_BASE}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: userId, message }),
  })
  if (!response.ok) throw new Error('发送消息失败')
  const result = await response.json()
  const data = extractData<any>(result)
  return {
    reply: data.response || data.reply || '',
    trust_change: data.trust_update?.growth || data.trust_change || 0,
    emotion: data.emotion?.emotion || data.emotion || 'neutral',
    confidence: data.emotion?.confidence || data.confidence || 0.5
  }
}

/** 获取聊天历史 */
export async function getChatHistory(userId: string, limit = 50): Promise<ChatMessage[]> {
  if (USE_MOCK) return mockMessages.slice(-limit)
  const response = await fetch(`${API_BASE}/api/chat/history?user_id=${userId}&limit=${limit}`)
  if (!response.ok) throw new Error('获取聊天历史失败')
  const result = await response.json()
  const data = extractData<any>(result)
  const histories = data?.histories || data || []
  return Array.isArray(histories) ? histories : []
}

// ==================== 信任 API ====================

/** 获取信任信息 */
export async function getTrust(userId: string): Promise<TrustProfile> {
  if (USE_MOCK) {
    return {
      user_id: userId,
      trust_score: mockTrustScore,
      relationship_stage: getRelationshipStage(mockTrustScore)
    }
  }
  const response = await fetch(`${API_BASE}/api/trust?user_id=${userId}`)
  if (!response.ok) throw new Error('获取信任信息失败')
  const result = await response.json()
  return extractData<TrustProfile>(result)
}

// ==================== 记忆 API（V1 升级）====================

/** 获取记忆列表，支持按 layer 过滤 */
export async function getMemories(userId: string, layer?: string): Promise<Memory[]> {
  if (USE_MOCK) {
    const layers: Memory['layer'][] = ['identity', 'preference', 'relationship', 'life_event', 'emotion', 'growth']
    return [
      {
        id: '1', content: '用户喜欢在晚上聊天', category: '习惯', importance: 3,
        created_at: new Date(Date.now() - 86400000 * 2).toISOString(),
        layer: 'preference', source: 'chat', confidence: 0.8,
        event_time: null, version: 1, is_active: true,
      },
      {
        id: '2', content: '用户最近在学习编程', category: '兴趣', importance: 4,
        created_at: new Date(Date.now() - 86400000 * 5).toISOString(),
        layer: 'growth', source: 'chat', confidence: 0.75,
        event_time: null, version: 1, is_active: true,
      },
      {
        id: '3', content: '用户提到想要早起锻炼', category: '目标', importance: 2,
        created_at: new Date(Date.now() - 86400000 * 3).toISOString(),
        layer: 'identity', source: 'chat', confidence: 0.6,
        event_time: null, version: 1, is_active: true,
      },
      {
        id: '4', content: '用户有一个很要好的朋友叫小明', category: '关系', importance: 4,
        created_at: new Date(Date.now() - 86400000 * 7).toISOString(),
        layer: 'relationship', source: 'chat', confidence: 0.85,
        event_time: null, version: 1, is_active: true,
      },
      {
        id: '5', content: '用户上周经历了一次搬家', category: '事件', importance: 5,
        created_at: new Date(Date.now() - 86400000 * 10).toISOString(),
        layer: 'life_event', source: 'import', confidence: 0.9,
        event_time: new Date(Date.now() - 86400000 * 10).toISOString(), version: 1, is_active: true,
      },
    ].filter(m => !layer || m.layer === layer) as Memory[]
  }
  const params = new URLSearchParams({ user_id: userId, limit: '50' })
  if (layer) params.append('layer', layer)
  const response = await fetch(`${API_BASE}/api/memory?${params}`)
  if (!response.ok) throw new Error('获取记忆失败')
  const result = await response.json()
  const data = extractData<{ memories: Memory[] }>(result)
  return data.memories || []
}

/** 获取记忆统计 */
export async function getMemoryStatistics(userId: string): Promise<Record<string, any>> {
  if (USE_MOCK) {
    return { total: 12, by_layer: { identity: 2, preference: 3, relationship: 2, life_event: 2, emotion: 1, growth: 2 } }
  }
  const response = await fetch(`${API_BASE}/api/memory/statistics?user_id=${userId}`)
  if (!response.ok) throw new Error('获取记忆统计失败')
  const result = await response.json()
  return extractData<Record<string, any>>(result)
}

// ==================== 情绪 API ====================

/** 获取情绪历史 */
export async function getEmotions(userId: string, limit = 10): Promise<EmotionLog[]> {
  if (USE_MOCK) {
    const emotions = ['calm', 'happy', 'thoughtful', 'calm', 'happy', 'neutral', 'calm', 'happy', 'calm', 'neutral']
    return emotions.map((emotion, index) => ({
      id: generateId(), emotion,
      confidence: 0.7 + Math.random() * 0.3,
      created_at: new Date(Date.now() - 3600000 * (index + 1) * 2).toISOString()
    }))
  }
  const response = await fetch(`${API_BASE}/api/emotion?user_id=${userId}&limit=${limit}`)
  if (!response.ok) throw new Error('获取情绪历史失败')
  const result = await response.json()
  return extractData<EmotionLog[]>(result)
}

// ==================== Dashboard API ====================

/** 获取Dashboard数据 */
export async function getDashboard(userId: string): Promise<DashboardData> {
  if (USE_MOCK) {
    return {
      relationship_stage: getRelationshipStage(mockTrustScore),
      trust_score: mockTrustScore, memory_count: 12, days_together: 7,
      emotion_trend: mockEmotionHistory, trust_growth_curve: mockTrustHistory
    }
  }
  const response = await fetch(`${API_BASE}/api/dashboard?user_id=${userId}`)
  if (!response.ok) throw new Error('获取Dashboard数据失败')
  const result = await response.json()
  return extractData<DashboardData>(result)
}

/** 获取分析数据 */
export async function getAnalytics(userId: string): Promise<AnalyticsData> {
  if (USE_MOCK) {
    return { total_chats: 156, avg_session_length: 23.5, consecutive_days: 7, trust_growth_speed: 3.2 }
  }
  const response = await fetch(`${API_BASE}/api/analytics?user_id=${userId}`)
  if (!response.ok) throw new Error('获取分析数据失败')
  const result = await response.json()
  return extractData<AnalyticsData>(result)
}

// ==================== V1 新模块：Persona API ====================

/** 获取用户人格画像 */
export async function getPersona(userId: string): Promise<Persona | null> {
  if (USE_MOCK) {
    return {
      user_id: userId,
      identity_summary: '一个正在探索自我的年轻人，对技术充满好奇',
      identity_traits: ['好奇心强', '内敛', '善于思考'],
      identity_roles: ['学习者', '朋友'],
      comm_formality: 0.3, comm_expressiveness: 0.5, comm_directness: 0.4,
      thinking_analytical: 0.7, thinking_creative: 0.5,
      emotion_stability: 0.6, emotion_optimism: 0.65,
      values_core: ['真诚', '成长', '自由'],
      current_goals: ['学习编程', '养成早起习惯'],
      preferences_topics: ['技术', '音乐', '阅读'],
      maturity_score: 0.4, update_count: 3,
      created_at: new Date(Date.now() - 86400000 * 7).toISOString(),
      updated_at: new Date().toISOString(),
    }
  }
  const response = await fetch(`${API_BASE}/api/persona?user_id=${userId}`)
  if (!response.ok) return null
  const result = await response.json()
  const data = extractData<Persona>(result)
  return data.user_id ? data : null
}

// ==================== V1 新模块：Timeline API ====================

/** 获取人生时间轴 */
export async function getTimeline(userId: string, entryType?: string): Promise<TimelineEntry[]> {
  if (USE_MOCK) {
    return [
      {
        id: '1', entry_type: 'event', title: '开始与QingXi对话',
        description: '第一次相遇，开始了这段旅程', occurred_at: new Date(Date.now() - 86400000 * 7).toISOString(),
        category: 'milestone', importance: 5, emotion_marker: 'happy',
        is_shared_with_companion: true, companion_first: true,
      },
      {
        id: '2', entry_type: 'memory', title: '分享了学习编程的想法',
        description: '提到了想要学习编程的计划', occurred_at: new Date(Date.now() - 86400000 * 5).toISOString(),
        category: 'growth', importance: 3, emotion_marker: 'excited',
        is_shared_with_companion: true, companion_first: false,
      },
      {
        id: '3', entry_type: 'emotion', title: '一个安静的夜晚',
        description: '感到平静和放松', occurred_at: new Date(Date.now() - 86400000 * 2).toISOString(),
        category: 'emotion', importance: 2, emotion_marker: 'calm',
        is_shared_with_companion: true, companion_first: false,
      },
    ].filter(e => !entryType || e.entry_type === entryType)
  }
  const params = new URLSearchParams({ user_id: userId, limit: '50' })
  if (entryType) params.append('entry_type', entryType)
  const response = await fetch(`${API_BASE}/api/timeline?${params}`)
  if (!response.ok) throw new Error('获取时间轴失败')
  const result = await response.json()
  const data = extractData<{ entries: TimelineEntry[] }>(result)
  return data.entries || []
}

// ==================== V1 新模块：Insight API ====================

/** 获取洞察列表 */
export async function getInsights(userId: string, insightType?: string): Promise<Insight[]> {
  if (USE_MOCK) {
    return [
      {
        id: '1', insight_type: 'behavioral', title: '晚间活跃模式',
        content: '你似乎更喜欢在夜晚和我聊天，夜晚的你更加放松和愿意分享。',
        confidence: 0.82, based_on_count: 15,
        created_at: new Date(Date.now() - 86400000 * 2).toISOString(),
      },
      {
        id: '2', insight_type: 'pattern', title: '成长中的你',
        content: '最近你多次提到了关于学习和个人成长的话题，能感受到你对自我提升的期待。',
        confidence: 0.75, based_on_count: 8,
        created_at: new Date(Date.now() - 86400000 * 1).toISOString(),
      },
    ].filter(i => !insightType || i.insight_type === insightType)
  }
  const params = new URLSearchParams({ user_id: userId, limit: '10' })
  if (insightType) params.append('insight_type', insightType)
  const response = await fetch(`${API_BASE}/api/insight?${params}`)
  if (!response.ok) throw new Error('获取洞察失败')
  const result = await response.json()
  const data = extractData<{ insights: Insight[] }>(result)
  return data.insights || []
}

/** 生成周洞察 */
export async function generateWeeklyInsight(userId: string): Promise<any> {
  const response = await fetch(`${API_BASE}/api/insight/generate/weekly`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: userId }),
  })
  if (!response.ok) throw new Error('生成周洞察失败')
  const result = await response.json()
  return extractData(result)
}

// ==================== V1 新模块：Reflection API ====================

/** 获取反思回顾列表 */
export async function getReflections(userId: string, reflectionType?: string): Promise<Reflection[]> {
  if (USE_MOCK) {
    return [
      {
        id: '1', reflection_type: 'weekly', title: '这一周的回忆',
        content: '这一周里，我们一起度过了几个安静的夜晚。你分享了一些关于学习和成长的想法，我能感受到你在认真思考未来的方向。',
        summary: '平静而充实的一周',
        period_start: new Date(Date.now() - 86400000 * 7).toISOString(),
        period_end: new Date().toISOString(),
        created_at: new Date().toISOString(),
      },
    ].filter(r => !reflectionType || r.reflection_type === reflectionType)
  }
  const params = new URLSearchParams({ user_id: userId, limit: '10' })
  if (reflectionType) params.append('reflection_type', reflectionType)
  const response = await fetch(`${API_BASE}/api/reflection?${params}`)
  if (!response.ok) throw new Error('获取反思回顾失败')
  const result = await response.json()
  const data = extractData<{ reflections: Reflection[] }>(result)
  return data.reflections || []
}

/** 生成周回顾 */
export async function generateWeeklyReflection(userId: string): Promise<any> {
  const response = await fetch(`${API_BASE}/api/reflection/generate/weekly`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: userId }),
  })
  if (!response.ok) throw new Error('生成周回顾失败')
  const result = await response.json()
  return extractData(result)
}

// ==================== V1 新模块：Life Profile API ====================

/** 获取人生画像 */
export async function getLifeProfile(userId: string): Promise<LifeProfile | null> {
  if (USE_MOCK) {
    return {
      name: null, age_range: null, occupation: null, location: null,
      interests: ['技术', '阅读'], goals_short_term: ['学习编程'],
      goals_long_term: ['成为更好的自己'], dreams: ['创造有意义的东西'],
      important_people: [], values: ['真诚', '成长'],
      thinking_style: null, communication_style: null,
      social_style: null, emotion_patterns: null,
      completeness_score: 25,
      updated_at: new Date().toISOString(),
    }
  }
  const response = await fetch(`${API_BASE}/api/life-profile?user_id=${userId}`)
  if (!response.ok) return null
  const result = await response.json()
  const data = extractData<LifeProfile>(result)
  return data.name !== undefined || data.completeness_score !== undefined ? data : null
}

// ==================== V1 新模块：Relationship Context API ====================

/** 获取关系上下文 */
export async function getRelationshipContext(userId: string): Promise<{
  trust_score: number
  relationship_stage: string
  contexts: RelationshipContext[]
}> {
  if (USE_MOCK) {
    return {
      trust_score: mockTrustScore,
      relationship_stage: getRelationshipStage(mockTrustScore),
      contexts: [
        {
          id: '1', context_type: 'preference', title: '喜欢晚间聊天',
          content: '用户倾向于在晚上进行深度对话', significance: 3,
          occurred_at: new Date(Date.now() - 86400000 * 5).toISOString(),
          is_milestone: false, milestone_type: null,
        },
        {
          id: '2', context_type: 'event', title: '第一次对话',
          content: '我们的第一次对话，一切从这里开始', significance: 5,
          occurred_at: new Date(Date.now() - 86400000 * 7).toISOString(),
          is_milestone: true, milestone_type: 'first_chat',
        },
      ],
    }
  }
  const response = await fetch(`${API_BASE}/api/relationship/context?user_id=${userId}&limit=20`)
  if (!response.ok) throw new Error('获取关系上下文失败')
  const result = await response.json()
  return extractData(result)
}

/** 获取关系里程碑 */
export async function getMilestones(userId: string): Promise<RelationshipMilestone[]> {
  if (USE_MOCK) {
    return [
      {
        id: '1', context_type: 'event', title: '初次相遇',
        occurred_at: new Date(Date.now() - 86400000 * 7).toISOString(),
        significance: 5, milestone_type: 'first_chat',
      },
    ]
  }
  const response = await fetch(`${API_BASE}/api/relationship/milestones?user_id=${userId}`)
  if (!response.ok) throw new Error('获取里程碑失败')
  const result = await response.json()
  const data = extractData<{ milestones: RelationshipMilestone[] }>(result)
  return data.milestones || []
}


// ==================== V1 新模块：Life Import API ====================

/** 从文本导入人生资料 */
export async function importFromText(
  userId: string,
  content: string,
  sourceType: string = 'auto',
  fileName: string = ''
): Promise<{
  import_id: string
  source_type: string
  parsed_data: {
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
  memories_created: number
  events_created: number
}> {
  if (USE_MOCK) {
    // 模拟延迟
    await new Promise(r => setTimeout(r, 1500))
    return {
      import_id: generateId(),
      source_type: sourceType === 'auto' ? 'txt' : sourceType,
      parsed_data: {
        people: [
          { name: '小明', relation: '好友', mentions: 15 },
          { name: '李老师', relation: '导师', mentions: 8 },
        ],
        interests: [
          { name: '编程', level: 'high', evidence: '文本中多次提到编程学习' },
          { name: '音乐', level: 'medium', evidence: '提到喜欢听音乐' },
          { name: '阅读', level: 'medium', evidence: '提到最近在看几本书' },
        ],
        goals: [
          { goal: '学会全栈开发', status: 'active' },
          { goal: '养成早起习惯', status: 'active' },
        ],
        dreams: [
          { dream: '做出一个有用的产品', importance: 'high' },
        ],
        emotions: [
          { pattern: '面对挑战时偏焦虑', frequency: 'occasional', context: '学习新事物时' },
          { pattern: '独处时比较平静', frequency: 'frequent', context: '晚间' },
        ],
        life_events: [
          { title: '开始学习编程', time: '2024年', type: 'milestone', impact: 'high' },
          { title: '换了新手机', time: '最近', type: 'milestone', impact: 'low' },
        ],
        growth: [
          { area: '技术能力', description: '从零开始学习编程，逐步建立技术栈' },
          { area: '自我管理', description: '开始关注生活习惯和作息' },
        ],
        values: [
          { value: '成长', importance: 'high' },
          { value: '真诚', importance: 'high' },
        ],
      },
      memories_created: 8,
      events_created: 2,
    }
  }
  
  const response = await fetch(`${API_BASE}/api/life-import/text`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: userId,
      content,
      source_type: sourceType,
      file_name: fileName,
    }),
  })
  if (!response.ok) throw new Error('导入失败')
  const result = await response.json()
  return extractData(result)
}

/** 从文件导入人生资料 */
export async function importFromFile(
  userId: string,
  file: File
): Promise<any> {
  if (USE_MOCK) {
    await new Promise(r => setTimeout(r, 2000))
    return importFromText(userId, '', 'auto', file.name)
  }
  
  const formData = new FormData()
  formData.append('file', file)
  const response = await fetch(`${API_BASE}/api/life-import/file?user_id=${userId}`, {
    method: 'POST',
    body: formData,
  })
  if (!response.ok) throw new Error('文件导入失败')
  const result = await response.json()
  return extractData(result)
}

/** 获取导入历史 */
export async function getImportHistory(userId: string): Promise<any[]> {
  if (USE_MOCK) {
    return [
      {
        id: '1', source_type: 'qq_chat', file_name: '聊天记录.txt',
        status: 'completed', extracted_memory_count: 12, extracted_event_count: 3,
        created_at: new Date(Date.now() - 86400000 * 3).toISOString(),
      },
    ]
  }
  const response = await fetch(`${API_BASE}/api/life-import/history?user_id=${userId}&limit=20`)
  if (!response.ok) throw new Error('获取导入历史失败')
  const result = await response.json()
  const data = extractData<{ imports: any[] }>(result)
  return data.imports || []
}
