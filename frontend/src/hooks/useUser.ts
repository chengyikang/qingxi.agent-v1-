/**
 * 用户身份管理 Hook
 * 处理用户创建、验证和状态管理
 */

import { useState, useEffect, useCallback } from 'react'
import { User, UseUserReturn } from '@/types'
import { createUser, getUserProfile } from '@/services/api'

const STORAGE_KEY = 'qingxi_user_id'

export function useUser(): UseUserReturn {
  const [userId, setUserId] = useState<string | null>(null)
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  /**
   * 验证用户身份
   */
  const validateUser = useCallback(async (id: string) => {
    try {
      const profile = await getUserProfile(id)
      setUser(profile)
      setUserId(id)
      return true
    } catch (err) {
      console.error('验证用户失败:', err)
      // 如果验证失败，清除本地存储
      if (typeof window !== 'undefined') {
        localStorage.removeItem(STORAGE_KEY)
      }
      return false
    }
  }, [])

  /**
   * 创建新用户
   */
  const handleCreateUser = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      
      const result = await createUser()
      
      // 保存到本地存储
      if (typeof window !== 'undefined') {
        localStorage.setItem(STORAGE_KEY, result.user_id)
      }
      
      // 获取完整用户资料
      const profile = await getUserProfile(result.user_id)
      setUser(profile)
      setUserId(result.user_id)
    } catch (err) {
      console.error('创建用户失败:', err)
      setError('无法创建用户，请刷新页面重试')
    } finally {
      setLoading(false)
    }
  }, [])

  /**
   * 初始化：检查本地存储或创建新用户
   */
  useEffect(() => {
    const initUser = async () => {
      if (typeof window === 'undefined') {
        setLoading(false)
        return
      }

      const storedUserId = localStorage.getItem(STORAGE_KEY)
      
      if (storedUserId) {
        // 验证已有用户
        const isValid = await validateUser(storedUserId)
        if (!isValid) {
          // 验证失败，创建新用户
          await handleCreateUser()
        }
      } else {
        // 没有存储的用户ID，创建新用户
        await handleCreateUser()
      }
    }

    initUser()
  }, [validateUser, handleCreateUser])

  return {
    userId,
    user,
    loading,
    error
  }
}
