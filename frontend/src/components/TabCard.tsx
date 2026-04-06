import { useState } from 'react'
import { api, type Tab } from '../api/client'
import { StatusBadge } from './StatusBadge'

interface Props {
  tab: Tab
  onUpdate: () => void
}

export default function TabCard({ tab, onUpdate }: Props) {
  const [loadingSummary, setLoadingSummary] = useState(false)
  const [expanded, setExpanded] = useState(false)

  const timeAgo = (iso: string) => {
    const secs = Math.floor((Date.now() - new Date(iso).getTime()) / 1000)
    if (secs < 60) return `${secs}s ago`
    if (secs < 3600) return `${Math.floor(secs / 60)}m ago`
    return `${Math.floor(secs / 3600)}h ago`
  }

  const handleGenerateSummary = async () => {
    setLoadingSummary(true)
    try {
      await api.generateSummary(tab.id)
      onUpdate()
    } finally {
      setLoadingSummary(false)
    }
  }

  const handleClose = async (auto: boolean) => {
    await api.closeTab(tab.id, auto)
    onUpdate()
  }

  const handleDelete = async () => {
    await api.deleteTab(tab.id)
    onUpdate()
  }

  const isClosed = tab.status === 'auto_closed' || tab.status === 'manually_closed'

  return (
    <div
      className={`bg-[#16162a] border rounded-xl p-4 transition-all hover:border-indigo-500/30 ${
        isClosed ? 'border-white/5 opacity-60' : 'border-white/8'
      }`}
    >
      <div className="flex items-start gap-3">
        {/* Icon */}
        <div className="w-9 h-9 rounded-lg bg-[#1e1e35] flex items-center justify-center text-lg shrink-0">
          {tab.type === 'browser_tab' ? '🌐' : '🖥️'}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-medium text-sm text-white truncate">{tab.title}</span>
            <StatusBadge status={tab.status} />
            {tab.ai_category && (
              <span className="text-xs bg-indigo-500/10 text-indigo-300 px-2 py-0.5 rounded-full">
                {tab.ai_category}
              </span>
            )}
          </div>

          {tab.url && (
            <p className="text-xs text-gray-500 truncate mt-0.5">{tab.url}</p>
          )}
          {tab.app_name && !tab.url && (
            <p className="text-xs text-gray-500 mt-0.5">{tab.app_name}</p>
          )}

          {/* AI Summary */}
          {tab.ai_summary ? (
            <p className="text-xs text-gray-400 mt-2 leading-relaxed">{tab.ai_summary}</p>
          ) : (
            !isClosed && (
              <button
                onClick={handleGenerateSummary}
                disabled={loadingSummary}
                className="mt-2 text-xs text-indigo-400 hover:text-indigo-300 flex items-center gap-1 transition-colors disabled:opacity-50"
              >
                {loadingSummary ? '⏳ Generating…' : '✨ Generate AI summary'}
              </button>
            )
          )}

          {/* Expanded settings */}
          {expanded && !isClosed && (
            <div className="mt-3 pt-3 border-t border-white/5 flex items-center gap-3 flex-wrap">
              <label className="flex items-center gap-2 text-xs text-gray-400">
                <input
                  type="checkbox"
                  checked={tab.auto_close_enabled}
                  onChange={async (e) => {
                    await api.updateTab(tab.id, { auto_close_enabled: e.target.checked })
                    onUpdate()
                  }}
                  className="accent-indigo-500"
                />
                Auto-close
              </label>
              <label className="flex items-center gap-2 text-xs text-gray-400">
                Timer:
                <select
                  value={tab.inactivity_threshold ?? ''}
                  onChange={async (e) => {
                    await api.updateTab(tab.id, {
                      inactivity_threshold: e.target.value ? Number(e.target.value) : undefined,
                    })
                    onUpdate()
                  }}
                  className="bg-[#1e1e35] border border-white/10 text-white text-xs rounded px-2 py-1"
                >
                  <option value="">Default</option>
                  <option value="300">5 min</option>
                  <option value="900">15 min</option>
                  <option value="1800">30 min</option>
                  <option value="3600">1 hour</option>
                  <option value="7200">2 hours</option>
                </select>
              </label>
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="flex items-center gap-1 shrink-0">
          <span className="text-xs text-gray-600">{timeAgo(tab.last_active_at)}</span>

          {!isClosed && (
            <button
              onClick={() => setExpanded(e => !e)}
              className="ml-1 p-1 text-gray-600 hover:text-gray-300 transition-colors rounded"
              title="Settings"
            >
              ⚙️
            </button>
          )}

          {!isClosed && (
            <button
              onClick={() => handleClose(false)}
              className="p-1 text-gray-600 hover:text-red-400 transition-colors rounded"
              title="Close tab"
            >
              ✕
            </button>
          )}

          <button
            onClick={handleDelete}
            className="p-1 text-gray-700 hover:text-red-500 transition-colors rounded"
            title="Remove from history"
          >
            🗑
          </button>
        </div>
      </div>
    </div>
  )
}
