import axios from 'axios'
import { createContext, useContext, useState } from 'react'

const API = axios.create({ baseURL: '/api' })
const AuthCtx = createContext(null)

API.interceptors.request.use(cfg => {
  const token = localStorage.getItem('token')
  if (token) {
    cfg.headers = cfg.headers || {}
    cfg.headers['Authorization'] = `Bearer ${token}`
  }
  // Never manually set Content-Type for FormData — let browser handle boundary
  if (cfg.data instanceof FormData) {
    delete cfg.headers['Content-Type']
  }
  return cfg
})

export function AuthProvider({ children }) {
  const [token, setToken] = useState(localStorage.getItem('token'))
  const [user, setUser] = useState(JSON.parse(localStorage.getItem('user') || 'null'))

  const login = (tok, usr) => {
    localStorage.setItem('token', tok)
    localStorage.setItem('user', JSON.stringify(usr))
    setToken(tok); setUser(usr)
  }
  const logout = () => {
    localStorage.removeItem('token'); localStorage.removeItem('user')
    setToken(null); setUser(null)
  }
  return <AuthCtx.Provider value={{ token, user, login, logout }}>{children}</AuthCtx.Provider>
}

export const useAuth = () => useContext(AuthCtx)
export default API
