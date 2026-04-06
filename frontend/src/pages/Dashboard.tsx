import { useEffect, useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { api, type Tab, type TabStatus, tokenStore } from '../api/client'
import { useAuth } from '../hooks/useAuth'
import TabCard from '../components/TabCard'
import Settings from '../components/Settings'

const FILTERS: { label: string; value: TabStatus | 'all' }[] = [
  { label: 'All', value: 'all' },
  { label: 'Active', value: 'active' },
  { label: 'Idle', value: 'inactive' },
  { label: 'Closed', value: 'auto_closed' },
]

export default function Dashboard() {
  const navigate = useNavigate()
  const { displayName, logout } = useAuth()
  const [tabs, setTabs] = useState<Tab[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [filter, setFilter] = useState<TabStatus | 'all'>('all')
  const [showSettings, setShowSettings] = useState(false)
  const [showUserMenu, setShowUserMenu] = useState(false)
  const [processing, setProcessing] = useState(false)
  const [lastChecked, setLastChecked] = useState<Date | null>(null)

  const fetchTabs = useCallback(async () => {
    try {
      const data = await api.getTabs({
        status: filter === 'all' ? undefined : filter,
        search: search || undefined,
      })
      setTabs(data)
    } finally {
      setLoading(false)
    }
  }, [filter, search])

  useEffect(() => { fetchTabs() }, [fetchTabs])

  useEffect(() => {
    const iv = setInterval(async () => {
      await api.processInactive()
      setLastChecked(new Date())
      fetchTabs()
    }, 60_000)
    return () => clearInterval(iv)
  }, [fetchTabs])

  const handleScanNow = async () => {
    setProcessing(true)
    try {
      await api.processInactive()
      setLastChecked(new Date())
      await fetchTabs()
    } finally {
      setProcessing(false)
    }
  }

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  const active = tabs.filter(t => t.status === 'active').length
  const idle = tabs.filter(t => t.status === 'inactive').length
  const closed = tabs.filter(t => t.status === 'auto_closed' || t.status === 'manually_closed').length

  return (
    <div className="min-h-screen bg-[#080810] text-white flex flex-col">

      {/* ── Background ── */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-0 right-0 w-[500px] h-[400px] bg-indigo-600/8 rounded-full blur-[120px]" />
        <div className="absolute bottom-0 left-0 w-[400px] h-[300px] bg-violet-600/8 rounded-full blur-[100px]" />
      </div>

      {/* ── Header ── */}
      <header className="relative z-10 flex items-center justify-between px-6 py-4 border-b border-white/[0.05] bg-[#080810]/80 backdrop-blur-xl sticky top-0">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate('/')} className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center text-sm shadow-lg shadow-indigo-500/20 hover:scale-105 transition-transform">
            🗂️
          </button>
          <span className="font-bold text-base hidden sm:block">TabSense</span>
          <span className="text-gray-700 hidden sm:block">·</span>
          <span className="text-sm text-gray-500 hidden sm:block">Dashboard</span>
        </div>

        <div className="flex items-center gap-2">
          {lastChecked && (
            <span className="text-xs text-gray-700 hidden md:block">
              Scanned {lastChecked.toLocaleTimeString()}
            </span>
          )}
          <button
            onClick={handleScanNow}
            disabled={processing}
            className="flex items-center gap-1.5 text-xs bg-white/5 hover:bg-white/10 border border-white/8 text-gray-300 px-3 py-2 rounded-xl transition-all disabled:opacity-50"
          >
            <span className={processing ? 'animate-spin' : ''}>⟳</span>
            <span className="hidden sm:inline">{processing ? 'Scanning…' : 'Scan now'}</span>
          </button>
          <button
            onClick={() => setShowSettings(true)}
            className="p-2 text-gray-500 hover:text-white transition-colors rounded-xl hover:bg-white/5"
            title="Settings"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
            </svg>
          </button>

          {/* User menu */}
          <div className="relative">
            <button
              onClick={() => setShowUserMenu(s => !s)}
              className="flex items-center gap-2 bg-white/5 hover:bg-white/10 border border-white/8 px-3 py-2 rounded-xl transition-all"
            >
              <div className="w-5 h-5 rounded-full bg-gradient-to-br from-indigo-400 to-violet-500 flex items-center justify-center text-xs font-bold">
                {displayName?.[0]?.toUpperCase() || 'U'}
              </div>
              <span className="text-xs text-gray-300 hidden sm:block max-w-[100px] truncate">{displayName || 'Account'}</span>
            </button>
            {showUserMenu && (
              <div className="absolute right-0 mt-2 w-40 bg-[#16162a] border border-white/10 rounded-xl overflow-hidden shadow-2xl z-50">
                <button
                  onClick={handleLogout}
                  className="w-full text-left text-sm text-red-400 hover:bg-red-500/10 px-4 py-3 transition-colors"
                >
                  Sign out
                </button>
              </div>
            )}
          </div>
        </div>
      </header>

      <main className="relative z-10 flex-1 px-6 py-6 max-w-5xl mx-auto w-full" onClick={() => setShowUserMenu(false)}>

        {/* ── Search + Filter bar ── */}
        <div className="flex items-center gap-3 mb-6 flex-wrap">
          <div className="flex-1 relative min-w-[220px]">
            <svg className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-600" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
            </svg>
            <input
              type="text"
              placeholder="Search by title, URL, or AI summary…"
              value={search}
              onChange={e => setSearch(e.target.value)}
              maxLength={200}
              className="w-full bg-white/[0.04] border border-white/[0.07] text-white text-sm rounded-xl pl-9 pr-4 py-2.5 placeholder-gray-700 focus:outline-none focus:border-indigo-500/50 focus:bg-white/[0.06] transition-all"
            />
          </div>
          <div className="flex items-center gap-1 bg-white/[0.04] border border-white/[0.07] rounded-xl p-1">
            {FILTERS.map(f => (
              <button
                key={f.value}
                onClick={() => setFilter(f.value)}
                className={`text-xs px-3 py-1.5 rounded-lg font-medium transition-all ${
                  filter === f.value ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/20' : 'text-gray-500 hover:text-white'
                }`}
              >
                {f.label}
              </button>
            ))}
          </div>
        </div>

        {/* ── Stats ── */}
        <div className="grid grid-cols-3 gap-3 mb-6">
          {[
            { label: 'Active', count: active, color: 'text-emerald-400', glow: 'shadow-emerald-400/10', border: 'border-emerald-400/10', bg: 'bg-emerald-400/[0.04]' },
            { label: 'Idle', count: idle, color: 'text-yellow-400', glow: '', border: 'border-yellow-400/10', bg: 'bg-yellow-400/[0.04]' },
            { label: 'Closed', count: closed, color: 'text-gray-400', glow: '', border: 'border-white/[0.06]', bg: 'bg-white/[0.02]' },
          ].map(s => (
            <div key={s.label} className={`border ${s.border} ${s.bg} rounded-2xl p-4 text-center`}>
              <div className={`text-3xl font-bold ${s.color}`}>{s.count}</div>
              <div className="text-xs text-gray-600 mt-1 font-medium">{s.label}</div>
            </div>
          ))}
        </div>

        {/* ── Tab List ── */}
        {loading ? (
          <div className="flex flex-col items-center justify-center py-24 text-gray-700">
            <div className="w-8 h-8 border-2 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin mb-4" />
            <p className="text-sm">Loading tabs…</p>
          </div>
        ) : tabs.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-24">
            <div className="w-16 h-16 rounded-2xl bg-white/[0.04] border border-white/[0.07] flex items-center justify-center text-3xl mb-4">🗂️</div>
            <p className="text-sm font-medium text-gray-400 mb-1">No tabs found</p>
            <p className="text-xs text-gray-700">
              {search ? 'Try a different search term' : 'No tabs match the current filter'}
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            {tabs.map(tab => (
              <TabCard key={tab.id} tab={tab} onUpdate={fetchTabs} />
            ))}
          </div>
        )}
      </main>

      {showSettings && <Settings onClose={() => { setShowSettings(false); fetchTabs() }} />}
    </div>
  )
}
