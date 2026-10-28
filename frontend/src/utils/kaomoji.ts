/**
 * QingXi 颜文字系统
 * 根据情绪和关系阶段自动匹配颜文字
 * 风格定位：慢热、温柔、内敛
 */

import { RelationshipStage, KaomojiCategory } from '@/types'

// ==================== 颜文字库 ====================

/** 所有颜文字分类 */
export const KAOMOJI_DATA: Record<KaomojiCategory, string[]> = {
  // 开心/温暖
  happy: [
    '(◕‿◕)', '(｡◕‿◕｡)', '(✿◠‿◠)', '(*´▽`*)',
    '(◠‿◠)', '(ノ◕ヮ◕)ノ*:・゚✧', '(´｡• ᵕ •｡`)', '(❁´◡`❁)',
  ],
  // 思考/沉思
  thinking: [
    '(・_・?)', '(´-ω-`)', '(_ _)', '(〃\'▽\'〃)',
    '( ˘ω˘ )', '(ー_ー)', '(´・ω・)', '(・ω・｀)',
  ],
  // 鼓励/陪伴
  comfort: [
    '( ´ ▽ ` )ﾉ', '(￣▽￣)ノ', '(੭ˊ꒳ˋ)੭', '(つ˚Д˚)つ',
    '(っ´ω`c)♡', '(ノ_<。) ', '(⊃｡•́‿•̀｡)⊃', '(つ♡•̀ω•́)つ',
  ],
  // 害羞/慢热
  shy: [
    '(*/ω＼*)', '(⁄ ⁄•⁄ω•⁄ ⁄)', '(。﹏。)', '(*/▽＼*)',
    '(*μ_μ)', '(//▽//)', '(｡ﾉω＼)', '(*/ω＼)',
  ],
  // 感动
  touched: [
    '(╥﹏╥)', '(;´༎ຶД༎ຶ`)', '(T⌓T)', '(ノ_<。)',
    '(╥_╥)', '(；∀；)', '(T_T)', '(ノДT)',
  ],
  // 日常/平静
  neutral: [
    '(・ω・)', '(´・ω・`)', '(=^･^=)', '(ᵔᴥᵔ)',
    '╰(*´︶`*)╯', '(・ω・)ノ', '(´ω`)', '(・ー・)',
  ],
  // 打招呼（陌生阶段）
  greeting: [
    '(｡･ω･)ﾉﾞ', '(・∀・)', '(｡◕‿‿◕｡)', '(*゜▽゜*)',
    '(｡+･`ω･´)', '(｡･ω･｡)', '(・ω・)ﾉ', '(´｡• ᵕ •｡)ﾉ',
  ],
}

// ==================== 关系阶段使用规则 ====================

/** 每个关系阶段的颜文字使用策略 */
const STAGE_KAOMOJI_RULES: Record<RelationshipStage, {
  /** 可使用的分类 */
  allowedCategories: KaomojiCategory[]
  /** 使用该阶段颜文字的概率 (0-1) */
  usageProbability: number
  /** 描述 */
  description: string
}> = {
  stranger: {
    allowedCategories: ['neutral', 'greeting'],
    usageProbability: 0.15,
    description: '极少使用，偶尔用 neutral/greeting 表示礼貌',
  },
  acquaintance: {
    allowedCategories: ['neutral', 'thinking'],
    usageProbability: 0.25,
    description: '适度使用 neutral/thinking，开始放松',
  },
  friend: {
    allowedCategories: ['happy', 'comfort', 'thinking', 'neutral'],
    usageProbability: 0.4,
    description: '较多使用 happy/comfort/thinking，关系更亲近',
  },
  confidant: {
    allowedCategories: ['happy', 'comfort', 'thinking', 'neutral', 'shy', 'touched', 'greeting'],
    usageProbability: 0.55,
    description: '丰富使用所有类型，包括 shy/touched，完全敞开心扉',
  },
}

// ==================== 情绪到颜文字分类的映射 ====================

/** 情绪对应的颜文字分类 */
const EMOTION_TO_KAOMOJI: Record<string, KaomojiCategory[]> = {
  happy: ['happy'],
  calm: ['neutral'],
  sad: ['touched'],
  anxious: ['thinking'],
  excited: ['happy'],
  thoughtful: ['thinking'],
  neutral: ['neutral'],
}

// ==================== 工具函数 ====================

/** 从数组中随机选取一个元素 */
function pickRandom<T>(arr: T[]): T {
  return arr[Math.floor(Math.random() * arr.length)]
}

/**
 * 根据关系阶段和情绪获取一个合适的颜文字
 * @param stage 当前关系阶段
 * @param emotion 当前情绪（可选）
 * @returns 颜文字字符串，可能返回空字符串（不使用颜文字）
 */
export function getKaomoji(stage: RelationshipStage, emotion?: string): string {
  const rules = STAGE_KAOMOJI_RULES[stage]
  
  // 根据概率决定是否使用颜文字
  if (Math.random() > rules.usageProbability) {
    return ''
  }
  
  // 确定可用的分类
  let categories = rules.allowedCategories
  
  // 如果有情绪，优先使用情绪对应的分类
  if (emotion && EMOTION_TO_KAOMOJI[emotion]) {
    const emotionCategories = EMOTION_TO_KAOMOJI[emotion]
    const availableEmotionCategories = emotionCategories.filter(c => categories.includes(c))
    if (availableEmotionCategories.length > 0) {
      categories = availableEmotionCategories
    }
  }
  
  // 随机选择一个分类
  const category = pickRandom(categories)
  const kaomojiList = KAOMOJI_DATA[category]
  
  return pickRandom(kaomojiList)
}

/**
 * 根据关系阶段获取一组推荐颜文字
 * @param stage 当前关系阶段
 * @returns 推荐颜文字数组
 */
export function getRecommendedKaomoji(stage: RelationshipStage): string[] {
  const rules = STAGE_KAOMOJI_RULES[stage]
  const result: string[] = []
  
  for (const category of rules.allowedCategories) {
    const kaomojiList = KAOMOJI_DATA[category]
    // 每个分类取2个
    const shuffled = [...kaomojiList].sort(() => Math.random() - 0.5)
    result.push(...shuffled.slice(0, 2))
  }
  
  return result
}

/**
 * 在消息文本中检测颜文字
 * @param text 消息内容
 * @returns 检测到的颜文字数组及其位置
 */
export function detectKaomoji(text: string): { kaomoji: string; index: number }[] {
  // 匹配常见的颜文字模式
  const patterns = [
    // 带括号类颜文字
    /(\([^\)]*[\u2500-\u25FF\u2600-\u26FF\u2700-\u27BF\u3000-\u303F\uFF00-\uFFEF\u0400-\u04FF\w][^\)]*\))/g,
    // 带特殊符号的短颜文字
    /(╰[^\)]*╯)/g,
  ]
  
  const results: { kaomoji: string; index: number }[] = []
  const seen = new Set<string>()
  
  // 用更精确的正则匹配颜文字
  const kaomojiRegex = /(\([◕ω_`´´ʃʖʘ∀∀✿❁༎ຶД⌓▽ﾛﾜεε꒳ˊˋ⊃⊂•́•̀﹏∥；_˚Д˚\s.·:・゚\*✧｀´˘∀・ー=^ﾐᵔᴥ╥Д⊃｡\u043c\u0443\u03c9\ud83d\ude44]+[\)╯]\))/g
  
  let match
  const regex = /((?:\([^\)]*\))|(?:(?:╰|（)[^\)）]*(?:╯|）)))/g
  
  while ((match = regex.exec(text)) !== null) {
    const kaomoji = match[1]
    // 简单过滤：至少包含一些特殊字符才算颜文字
    if (kaomoji.length >= 4 && /[◕ω_`´∀✿❁▽﹏⌓˘・ー^ﾐ•ᵔ╥∥꒳\u2020-\u2048]/.test(kaomoji)) {
      const key = `${match.index}:${kaomoji}`
      if (!seen.has(key)) {
        seen.add(key)
        results.push({ kaomoji, index: match.index })
      }
    }
  }
  
  return results
}

/**
 * 检查文本是否包含颜文字
 */
export function hasKaomoji(text: string): boolean {
  return detectKaomoji(text).length > 0
}

/**
 * 获取 "正在思考" 时的随机颜文字提示
 * @returns 包含颜文字的等待提示
 */
export function getThinkingMessage(): string {
  const messages = [
    'QingXi 正在思考...',
    'QingXi 正在认真想...',
    'QingXi 在想...',
    '慢慢来，QingXi在组织语言...',
    'QingXi 在斟酌字句...',
  ]
  const message = pickRandom(messages)
  const kaomoji = pickRandom(KAOMOJI_DATA.thinking)
  return `${message} ${kaomoji}`
}

/**
 * 获取颜文字分类信息（用于 UI 展示）
 */
export function getKaomojiCategories() {
  return Object.entries(KAOMOJI_DATA).map(([key, values]) => ({
    category: key as KaomojiCategory,
    count: values.length,
    samples: values.slice(0, 3),
  }))
}

/**
 * 获取阶段颜文字规则信息（用于 UI 展示）
 */
export function getStageRules() {
  return STAGE_KAOMOJI_RULES
}
