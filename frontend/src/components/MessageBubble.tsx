'use client'

/**
 * 消息气泡组件 V1
 * 展示单条聊天消息，支持颜文字高亮
 */

import React from 'react'
import { MessageBubbleProps } from '@/types'
import { detectKaomoji } from '@/utils/kaomoji'

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user'
  
  // 格式化时间
  const formatTime = (dateString: string) => {
    const date = new Date(dateString)
    const hours = date.getHours().toString().padStart(2, '0')
    const minutes = date.getMinutes().toString().padStart(2, '0')
    return `${hours}:${minutes}`
  }

  /**
   * 渲染消息内容，对QingXi的回复中的颜文字进行高亮
   */
  const renderContent = (text: string) => {
    // 只对QingXi的消息做颜文字高亮
    if (isUser) {
      return <span className="whitespace-pre-wrap">{text}</span>
    }

    const kaomojiPositions = detectKaomoji(text)
    
    if (kaomojiPositions.length === 0) {
      return <span className="whitespace-pre-wrap">{text}</span>
    }

    // 将文本按颜文字位置拆分，穿插普通文本和高亮颜文字
    const parts: React.ReactNode[] = []
    let lastIndex = 0

    kaomojiPositions.forEach(({ kaomoji, index }, i) => {
      // 颜文字之前的普通文本
      if (index > lastIndex) {
        parts.push(
          <span key={`text-${i}`} className="whitespace-pre-wrap">
            {text.slice(lastIndex, index)}
          </span>
        )
      }
      // 高亮的颜文字
      parts.push(
        <span
          key={`kaomoji-${i}`}
          className="inline-block text-qx-accent-light text-lg font-medium animate-fade-in mx-0.5"
          style={{
            textShadow: '0 0 8px rgba(249, 115, 22, 0.3)',
            letterSpacing: '0.05em',
          }}
        >
          {kaomoji}
        </span>
      )
      lastIndex = index + kaomoji.length
    })

    // 剩余的文本
    if (lastIndex < text.length) {
      parts.push(
        <span key="text-end" className="whitespace-pre-wrap">
          {text.slice(lastIndex)}
        </span>
      )
    }

    return <>{parts}</>
  }

  return (
    <div
      className={`flex w-full animate-fade-in ${
        isUser ? 'justify-end' : 'justify-start'
      }`}
    >
      <div
        className={`max-w-[80%] sm:max-w-[70%] rounded-2xl px-4 py-3 transition-all duration-300 ${
          isUser
            ? 'bg-qx-accent/20 text-qx-text rounded-tr-sm'
            : 'bg-qx-bg-secondary text-qx-text rounded-tl-sm'
        }`}
      >
        {/* 消息来源标签（仅AI消息显示） */}
        {!isUser && (
          <div className="text-xs text-qx-accent mb-1 font-medium">
            QingXi
          </div>
        )}
        
        {/* 消息内容（含颜文字高亮） */}
        <div className="text-sm sm:text-base leading-relaxed">
          {renderContent(message.content)}
        </div>
        
        {/* 时间戳 */}
        <div className={`text-xs mt-1 ${isUser ? 'text-right' : ''} text-qx-text-muted`}>
          {formatTime(message.created_at)}
        </div>
      </div>
    </div>
  )
}
