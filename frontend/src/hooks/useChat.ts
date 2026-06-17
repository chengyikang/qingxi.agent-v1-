/**
 * 聊天管理 Hook
 * 处理消息发送、历史加载和状态管理
 */

import { useState, useCallback, useRef } from 'react'
import { ChatMessage, UseChatReturn } from '@/types'
import { sendMessage, getChatHistory } from '@/services/api'

export function useChat(userId: string | null): UseChatReturn {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [loading, setLoading] = useState(false)
  const [sending, setSending] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  // 用于防止重复发送
  const sendingRef = useRef(false)

  /**
   * 加载聊天历史
   */
  const loadHistory = useCallback(async () => {
    if (!userId) return
    
    try {
      setLoading(true)
      setError(null)
      
      const history = await getChatHistory(userId, 50)
      // 保护：确保 history 是数组
      setMessages(Array.isArray(history) ? history : [])
    } catch (err) {
      console.error('加载历史记录失败:', err)
      setMessages([])
      setError('加载历史记录失败')
    } finally {
      setLoading(false)
    }
  }, [userId])

  /**
   * 发送消息
   */
  const handleSendMessage = useCallback(async (text: string) => {
    if (!userId || !text.trim()) return
    if (sendingRef.current) return
    
    // 防止重复发送
    sendingRef.current = true
    
    try {
      setSending(true)
      setError(null)
      
      // 添加用户消息到列表
      const userMessage: ChatMessage = {
        id: Date.now().toString(),
        user_id: userId,
        role: 'user',
        content: text.trim(),
        created_at: new Date().toISOString()
      }
      setMessages(prev => [...prev, userMessage])
      
      // 调用API发送消息
      const response = await sendMessage(userId, text.trim())
      
      // 添加助手回复到列表
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        user_id: userId,
        role: 'assistant',
        content: response.reply,
        created_at: new Date().toISOString(),
        emotion: response.emotion,
        confidence: response.confidence
      }
      setMessages(prev => [...prev, assistantMessage])
      
    } catch (err) {
      console.error('发送消息失败:', err)
      setError('发送消息失败，请重试')
      
      // 移除刚才添加的用户消息（因为发送失败了）
      setMessages(prev => prev.slice(0, -1))
    } finally {
      setSending(false)
      sendingRef.current = false
    }
  }, [userId])

  return {
    messages,
    loading,
    error,
    sending,
    sendMessage: handleSendMessage,
    loadHistory
  }
}
