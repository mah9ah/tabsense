const BASE_URL = 'http://127.0.0.1:8000'

export type TabType = 'browser_tab' | 'desktop_app'
export type TabStatus = 'active' | 'inactive' | 'auto_closed' | 'manually_closed'

export interface Tab {
  id: number
  type: TabType
  title: string
  url: string | null
  app_name: string | null
  favicon_url: string | null
  opened_at: string
  last_active_at: string
  closed_at: string | null
  status: TabStatus
  ai_summary: string | null
  ai_category: string | null
  inactivity_threshold: number | null
  auto_close_enabled: boolean
}

export interface InactiveTab {
  tab: Tab
  inactive_for_seconds: number
  will_auto_close: boolean
}

export interface UserSettings {
  id: number
  default_inactivity_threshold: number
  auto_close_enabled_globally: boolean
  notifications_enabled: boolean
  ai_summaries_enabled: boolean
  updated_at: string
}

export interface AuthUser {
  display_name: string
  email?: string
}

// ── Token storage ──────────────────────────────────────────────────────────────
export const tokenStore = {
  get: () => localStorage.getItem('tabsense_token'),
  set: (t: string) => localStorage.setItem('tabsense_token', t),
  clear: () => localStorage.removeItem('tabsense_token'),
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const token = tokenStore.get()
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (token) headers['Authorization'] = `Bearer ${token}`

  const res = await fetch(`${BASE_URL}${path}`, { headers, ...options })

  if (res.status === 401) {
    tokenStore.clear()
    window.location.hash = '#/auth'
    throw new Error('Session expired. Please log in again.')
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || 'Request failed')
  }
  if (res.status === 204) return undefined as T
  return res.json()
}

export const api = {
  // Auth
  register: (email: string, password: string, display_name?: string) =>
    request<{ access_token: string; display_name: string }>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, display_name }),
    }),
  login: (email: string, password: string) =>
    request<{ access_token: string; display_name: string }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),
  me: () => request<AuthUser>('/auth/me'),

  // Tabs
  getTabs: (params?: { status?: TabStatus; search?: string }) => {
    const qs = new URLSearchParams()
    if (params?.status) qs.set('status', params.status)
    if (params?.search) qs.set('search', params.search)
    return request<Tab[]>(`/tabs/${qs.toString() ? '?' + qs : ''}`)
  },
  getTab: (id: number) => request<Tab>(`/tabs/${id}`),
  createTab: (data: Partial<Tab>) =>
    request<Tab>('/tabs/', { method: 'POST', body: JSON.stringify(data) }),
  updateTab: (id: number, data: Partial<Tab>) =>
    request<Tab>(`/tabs/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  closeTab: (id: number, auto = false) =>
    request<Tab>(`/tabs/${id}/close?auto=${auto}`, { method: 'POST' }),
  deleteTab: (id: number) =>
    request<void>(`/tabs/${id}`, { method: 'DELETE' }),

  // Summaries
  generateSummary: (tabId: number) =>
    request<{ tab_id: number; summary: string; category: string | null }>(
      '/summaries/', { method: 'POST', body: JSON.stringify({ tab_id: tabId }) }
    ),

  // Inactivity
  checkInactive: () => request<InactiveTab[]>('/inactivity/check'),
  processInactive: () => request<Tab[]>('/inactivity/process', { method: 'POST' }),

  // Settings
  getSettings: () => request<UserSettings>('/settings/'),
  updateSettings: (data: Partial<UserSettings>) =>
    request<UserSettings>('/settings/', { method: 'PATCH', body: JSON.stringify(data) }),
}
