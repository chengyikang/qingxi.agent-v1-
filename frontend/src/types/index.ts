/**
 * QingXi V1 前端类型定义
 * 包含所有与后端交互的数据结构，适配 V1 后端新模块
 */

// ==================== 用户相关 ====================

export interface User {
  id: string
  nickname: string | null
  created_at: string
  last_active_at: string
}

// ==================== 聊天相关 ====================

export interface ChatMessage {
  id: string
  user_id: string
  role: 'user' | 'assistant'
  content: string
  created_at: string
  emotion?: string
  confidence?: number
}

export interface SendMessageResponse {
  reply: string
  trust_change: number
  emotion: string
  confidence: number
}

// ==================== 信任相关 ====================

export type RelationshipStage = 'stranger' | 'acquaintance' | 'friend' | 'confidant'

export interface TrustProfile {
  user_id: string
  trust_score: number  // 0-1000
  relationship_stage: RelationshipStage
}

// ==================== 记忆相关（V1 升级）====================

/** V1 六层记忆分类 */
export type MemoryLayer = 'identity' | 'preference' | 'relationship' | 'life_event' | 'emotion' | 'growth'

/** 记忆来源 */
export type MemorySource = 'chat' | 'import' | 'persona' | 'insight' | 'reflection' | 'system'

export interface Memory {
  id: string
  content: string
  category: string
  importance: number  // 1-5
  created_at: string
  // V1 新增字段
  layer: MemoryLayer
  source: MemorySource
  confidence: number       // 0.0-1.0
  event_time: string | null
  version: number
  is_active: boolean
  updated_at?: string
  related_entity_type?: string | null
  related_entity_id?: string | null
  metadata_json?: Record<string, any> | null
}

/** 记忆层级配置 */
export const MEMORY_LAYER_CONFIG: Record<MemoryLayer, {
  label: string
  icon: string
  color: string
  description: string
}> = {
  identity: { label: '身份', icon: '🪪', color: 'text-purple-400', description: '关于"我是谁"的记忆' },
  preference: { label: '偏好', icon: '🎨', color: 'text-cyan-400', description: '喜欢什么、不喜欢什么' },
  relationship: { label: '关系', icon: '🤝', color: 'text-pink-400', description: '与重要的人的关系' },
  life_event: { label: '事件', icon: '📅', color: 'text-amber-400', description: '人生中的重要事件' },
  emotion: { label: '情绪', icon: '💫', color: 'text-blue-400', description: '情绪相关的记忆' },
  growth: { label: '成长', icon: '🌱', color: 'text-green-400', description: '成长与变化的轨迹' },
}

// ==================== 情绪相关 ====================

export interface EmotionLog {
  id: string
  emotion: string
  confidence: number
  created_at: string
}

// ==================== Dashboard相关 ====================

export interface EmotionTrend {
  date: string
  emotion: string
}

export interface TrustGrowthPoint {
  date: string
  score: number
}

export interface DashboardData {
  relationship_stage: RelationshipStage
  trust_score: number
  memory_count: number
  days_together: number
  emotion_trend: EmotionTrend[]
  trust_growth_curve: TrustGrowthPoint[]
}

// ==================== 分析相关 ====================

export interface AnalyticsData {
  total_chats: number
  avg_session_length: number
  consecutive_days: number
  trust_growth_speed: number
}

// ==================== V1 新模块：Persona ====================

export interface Persona {
  user_id: string
  identity_summary: string
  identity_traits: string[]
  identity_roles: string[]
  comm_formality: number      // 0-1 正式程度
  comm_expressiveness: number // 0-1 表达丰富程度
  comm_directness: number     // 0-1 直接程度
  thinking_analytical: number // 0-1 分析思维
  thinking_creative: number   // 0-1 创意思维
  emotion_stability: number   // 0-1 情绪稳定性
  emotion_optimism: number    // 0-1 乐观程度
  values_core: string[]
  current_goals: string[]
  preferences_topics: string[]
  maturity_score: number
  update_count: number
  created_at: string
  updated_at: string
}

// ==================== V1 新模块：Timeline ====================

export interface TimelineEntry {
  id: string
  entry_type: string        // event/memory/milestone/emotion
  title: string
  description: string
  occurred_at: string
  category: string
  importance: number        // 1-5
  emotion_marker: string | null
  is_shared_with_companion: boolean
  companion_first: boolean
}

// ==================== V1 新模块：Insight ====================

export interface Insight {
  id: string
  insight_type: string      // weekly/monthly/behavioral/pattern
  title: string
  content: string
  confidence: number
  based_on_count: number
  created_at: string
}

// ==================== V1 新模块：Reflection ====================

export interface Reflection {
  id: string
  reflection_type: string   // weekly/monthly/yearly
  title: string
  content: string
  summary: string
  period_start: string
  period_end: string
  created_at: string
}

// ==================== V1 新模块：Life Profile ====================

export interface LifeProfile {
  name: string | null
  age_range: string | null
  occupation: string | null
  location: string | null
  interests: string[]
  goals_short_term: string[]
  goals_long_term: string[]
  dreams: string[]
  important_people: string[]
  values: string[]
  thinking_style: string | null
  communication_style: string | null
  social_style: string | null
  emotion_patterns: string | null
  completeness_score: number
  updated_at: string
}

// ==================== V1 新模块：Relationship Context ====================

export interface RelationshipContext {
  id: string
  context_type: string      // topic/preference/event/habit
  title: string
  content: string
  significance: number      // 1-5
  occurred_at: string
  is_milestone: boolean
  milestone_type: string | null
}

export interface RelationshipMilestone {
  id: string
  context_type: string
  title: string
  occurred_at: string
  significance: number
  milestone_type: string
}

// ==================== 颜文字系统类型 ====================

export type KaomojiCategory = 'happy' | 'thinking' | 'comfort' | 'shy' | 'touched' | 'neutral' | 'greeting'

export interface KaomojiConfig {
  categories: Record<KaomojiCategory, string[]>
  /** 按关系阶段的使用频率 */
  stageFrequency: Record<RelationshipStage, {
    categories: KaomojiCategory[]
    probability: number  // 0-1
  }>
}

// ==================== 组件Props类型 ====================

export interface MessageBubbleProps {
  message: ChatMessage
}

export interface TrustIndicatorProps {
  trustProfile: TrustProfile
  previousScore?: number
}

// ==================== API错误类型 ====================

export interface ApiError {
  error: string
  message: string
}

// ==================== Hook返回类型 ====================

export interface UseUserReturn {
  userId: string | null
  user: User | null
  loading: boolean
  error: string | null
}

export interface UseChatReturn {
  messages: ChatMessage[]
  loading: boolean
  error: string | null
  sending: boolean
  sendMessage: (text: string) => Promise<void>
  loadHistory: () => Promise<void>
}

// ==================== 关系阶段配置 ====================

export const RELATIONSHIP_STAGE_CONFIG: Record<RelationshipStage, {
  label: string
  color: string
  bgColor: string
  description: string
}> = {
  stranger: {
    label: '陌生',
    color: 'text-stage-stranger',
    bgColor: 'bg-stage-stranger',
    description: '刚刚认识的两个人'
  },
  acquaintance: {
    label: '熟悉',
    color: 'text-stage-acquaintance',
    bgColor: 'bg-stage-acquaintance',
    description: '已经有些了解的阶段'
  },
  friend: {
    label: '朋友',
    color: 'text-stage-friend',
    bgColor: 'bg-stage-friend',
    description: '可以畅所欲言的朋友'
  },
  confidant: {
    label: '知己',
    color: 'text-stage-confidant',
    bgColor: 'bg-stage-confidant',
    description: '最懂你的那个人'
  }
}

// ==================== 信任值阶段阈值 ====================

export const TRUST_STAGE_THRESHOLDS = {
  stranger: 0,
  acquaintance: 250,
  friend: 500,
  confidant: 750
}

// ==================== 情绪配置 ====================

export const EMOTION_CONFIG: Record<string, {
  label: string
  color: string
  icon: string
}> = {
  happy: { label: '开心', color: 'text-emotion-happy', icon: '😊' },
  calm: { label: '平静', color: 'text-emotion-calm', icon: '😌' },
  sad: { label: '难过', color: 'text-emotion-sad', icon: '😢' },
  anxious: { label: '焦虑', color: 'text-emotion-anxious', icon: '😰' },
  excited: { label: '兴奋', color: 'text-emotion-happy', icon: '🤩' },
  thoughtful: { label: '沉思', color: 'text-emotion-calm', icon: '🤔' },
  neutral: { label: '中性', color: 'text-qx-text-secondary', icon: '😐' }
}
