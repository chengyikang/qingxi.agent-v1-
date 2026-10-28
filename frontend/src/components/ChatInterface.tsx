'use client'

/**
 * 聊天界面组件 V1
 * 消息列表 + 输入框 + 颜文字等待提示
 */

import React, { useState, useEffect, useRef } from 'react'
import { ChatMessage } from '@/types'
import MessageBubble from './MessageBubble'
import { getThinkingMessage } from '@/utils/kaomoji'

interface ChatInterfaceProps {
  messages: ChatMessage[]
  loading: boolean
  sending: boolean
  onSendMessage: (text: string) => void
}

export default function ChatInterface({
  messages,
  loading,
  sending,
  onSendMessage
}: ChatInterfaceProps) {
  const [inputText, setInputText] = useState('')
  const [thinkingText, setThinkingText] = useState('QingXi 正在思考...')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  // 自动滚动到底部
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // 发送时随机显示带颜文字的等待提示
  useEffect(() => {
    if (sending) {
      setThinkingText(getThinkingMessage())
    }
  }, [sending])

  // 处理发送
  const handleSend = () => {
    if (inputText.trim() && !sending) {
      onSendMessage(inputText)
      setInputText('')
      inputRef.current?.focus()
    }
  }

  // 处理回车发送（Shift+Enter换行）
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* 消息列表区域 */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {loading ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-qx-text-muted text-sm animate-pulse">
              加载中...
            </div>
          </div>
        ) : messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="text-5xl mb-6 animate-bounce-subtle">🌙</div>
            <div className="text-qx-text-secondary text-xl mb-3">
              夜深了，风很温柔
            </div>
            <div className="text-qx-text-muted text-sm max-w-xs leading-relaxed">
              我是 QingXi，一个慢热的陪伴者。
              <br />
              不用急，慢慢来。
              <br />
              想说什么都可以，或者只是安静地待着也好。
            </div>
            <div className="mt-6 text-qx-text-muted/40 text-xs">
              (・ω・)
            </div>
          </div>
        ) : (
          messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))
        )}
        
        {/* 发送中的指示器 */}
        {sending && (
          <div className="flex justify-start animate-fade-in">
            <div className="bg-qx-bg-secondary rounded-2xl rounded-tl-sm px-4 py-3">
              <div className="text-qx-text-muted text-sm mb-1">{thinkingText}</div>
              <div className="flex gap-1">
                <span className="w-2 h-2 bg-qx-accent rounded-full animate-typing" style={{ animationDelay: '0ms' }} />
                <span className="w-2 h-2 bg-qx-accent rounded-full animate-typing" style={{ animationDelay: '200ms' }} />
                <span className="w-2 h-2 bg-qx-accent rounded-full animate-typing" style={{ animationDelay: '400ms' }} />
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* 输入区域 */}
      <div className="border-t border-qx-bg-secondary p-4">
        <div className="flex items-end gap-3">
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="说点什么..."
              rows={1}
              className="w-full bg-qx-bg-secondary text-qx-text rounded-2xl px-4 py-3 pr-12 
                         resize-none focus:outline-none focus:ring-2 focus:ring-qx-accent/30
                         placeholder:text-qx-text-muted text-sm
                         max-h-32 overflow-y-auto"
              style={{ minHeight: '48px' }}
            />
          </div>
          
          <button
            onClick={handleSend}
            disabled={!inputText.trim() || sending}
            className={`w-12 h-12 rounded-full flex items-center justify-center transition-all duration-300
                       ${inputText.trim() && !sending
                         ? 'bg-qx-accent text-white hover:bg-qx-accent-dark cursor-pointer'
                         : 'bg-qx-bg-secondary text-qx-text-muted cursor-not-allowed'
                       }`}
          >
            <svg
              className={`w-5 h-5 transition-transform ${sending ? 'animate-pulse' : ''}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
              />
            </svg>
          </button>
        </div>
        
        <div className="text-xs text-qx-text-muted text-center mt-2">
          按 Enter 发送 · Shift + Enter 换行
        </div>
      </div>
    </div>
  )
}
