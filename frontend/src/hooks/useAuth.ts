import { useState, useEffect } from 'react'
import { tokenStore, api } from '../api/client'

export function useAuth() {
  const [token, setToken] = useState<string | null>(tokenStore.get())
  const [displayName, setDisplayName] = useState<string>('')

  useEffect(() => {
    if (token) {
      api.me()
        .then(u => setDisplayName(u.display_name || ''))
        .catch(() => logout())
    }
  }, [token])

  const login = async (email: string, password: string) => {
    const res = await api.login(email, password)
    tokenStore.set(res.access_token)
    setToken(res.access_token)
    setDisplayName(res.display_name)
    return res
  }

  const register = async (email: string, password: string, name?: string) => {
    const res = await api.register(email, password, name)
    tokenStore.set(res.access_token)
    setToken(res.access_token)
    setDisplayName(res.display_name)
    return res
  }

  const logout = () => {
    tokenStore.clear()
    setToken(null)
    setDisplayName('')
  }

  return { token, displayName, isLoggedIn: !!token, login, register, logout }
}
