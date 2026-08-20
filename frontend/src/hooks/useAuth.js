import { useState, useCallback } from 'react'
import api from '../services/api'

export function useAuth() {
  const [user, setUser] = useState(() => {
    const raw = localStorage.getItem('sentrygrid_user')
    return raw ? JSON.parse(raw) : null
  })

  const login = useCallback(async (email, password) => {
    const form = new URLSearchParams()
    form.append('username', email)
    form.append('password', password)
    const res = await api.post('/auth/login', form, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
    localStorage.setItem('sentrygrid_token', res.data.access_token)
    localStorage.setItem('sentrygrid_user', JSON.stringify(res.data.user))
    setUser(res.data.user)
    return res.data.user
  }, [])

  const register = useCallback(async (payload) => {
    await api.post('/auth/register', payload)
    return login(payload.email, payload.password)
  }, [login])

  const logout = useCallback(() => {
    localStorage.removeItem('sentrygrid_token')
    localStorage.removeItem('sentrygrid_user')
    setUser(null)
  }, [])

  return { user, login, register, logout, isAuthenticated: !!user }
}
