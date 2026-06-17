/**
 * 用户身份管理 Hook
 * 处理用户创建、验证和状态管理
 */

import { useState, useEffect, useRef } from 'react'
import { User, UseUserReturn } from '@/types'
import { createUser, getUserProfile } from '@/services/api'

const STORAGE_KEY = 'qingxi_user_id'

export function useUser(): UseUserReturn {
  const [userId, setUserId] = useState<string | null>(null)
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  // 防止重复初始化
  const initRef = useRef(false)

  useEffect(() => {
    // 防止 React StrictMode 双重执行
    if (initRef.current) return
    initRef.current = true

    const initUser = async () => {
      if (typeof window === 'undefined') {
        setLoading(false)
        return
      }

      const storedUserId = localStorage.getItem(STORAGE_KEY)
      
      // 有有效存储 ID，先验证
      if (storedUserId && storedUserId !== 'undefined' && storedUserId !== 'null') {
        try {
          const profile = await getUserProfile(storedUserId)
          setUser(profile)
          setUserId(storedUserId)
          setLoading(false)
          return
        } catch (err) {
          console.error('验证用户失败，将创建新用户:', err)
          localStorage.removeItem(STORAGE_KEY)
        }
      } else {
        localStorage.removeItem(STORAGE_KEY)
      }

      // 创建新用户
      try {
        setLoading(true)
        setError(null)
        
        const result = await createUser()
        
        if (!result.user_id || result.user_id === 'undefined') {
          throw new Error('创建用户返回无效ID')
        }
        
        localStorage.setItem(STORAGE_KEY, result.user_id)
        
        const profile = await getUserProfile(result.user_id)
        setUser(profile)
        setUserId(result.user_id)
      } catch (err) {
        console.error('创建用户失败:', err)
        setError('无法创建用户，请刷新页面重试')
        initRef.current = false // 允许重试
      } finally {
        setLoading(false)
      }
    }

    initUser()
  }, [])

  return {
    userId,
    user,
    loading,
    error
  }
}
