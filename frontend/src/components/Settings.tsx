import { useEffect, useState } from 'react'
import { api, type UserSettings } from '../api/client'

export default function Settings({ onClose }: { onClose: () => void }) {
  const [settings, setSettings] = useState<UserSettings | null>(null)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    api.getSettings().then(setSettings)
  }, [])

  const save = async () => {
    if (!settings) return
    setSaving(true)
    try {
      await api.updateSettings(settings)
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
    } finally {
      setSaving(false)
    }
  }

  if (!settings) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
        <div className="bg-[#16162a] rounded-2xl p-8 text-gray-400 text-sm">Loading…</div>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="bg-[#16162a] border border-white/8 rounded-2xl p-6 w-full max-w-md shadow-2xl">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-white font-semibold text-lg">Settings</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-white transition-colors text-lg">✕</button>
        </div>

        <div className="space-y-5">
          {/* Default inactivity threshold */}
          <div>
            <label className="block text-sm text-gray-300 mb-2">Default inactivity threshold</label>
            <select
              value={settings.default_inactivity_threshold}
              onChange={e => setSettings(s => s && ({ ...s, default_inactivity_threshold: Number(e.target.value) }))}
              className="w-full bg-[#1e1e35] border border-white/10 text-white text-sm rounded-lg px-3 py-2"
            >
              <option value={300}>5 minutes</option>
              <option value={900}>15 minutes</option>
              <option value={1800}>30 minutes</option>
              <option value={3600}>1 hour</option>
              <option value={7200}>2 hours</option>
            </select>
          </div>

          {/* Toggles */}
          {[
            { key: 'notifications_enabled', label: 'Desktop notifications', desc: 'Notify when a tab goes idle' },
            { key: 'auto_close_enabled_globally', label: 'Auto-close globally', desc: 'Apply auto-close to all tabs by default' },
            { key: 'ai_summaries_enabled', label: 'AI summaries', desc: 'Generate Gemini summaries for new tabs' },
          ].map(({ key, label, desc }) => (
            <div key={key} className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-200">{label}</p>
                <p className="text-xs text-gray-500">{desc}</p>
              </div>
              <button
                onClick={() => setSettings(s => s && ({ ...s, [key]: !s[key as keyof UserSettings] }))}
                className={`w-11 h-6 rounded-full transition-colors relative ${
                  settings[key as keyof UserSettings] ? 'bg-indigo-600' : 'bg-gray-700'
                }`}
              >
                <span
                  className={`absolute top-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform ${
                    settings[key as keyof UserSettings] ? 'translate-x-5' : 'translate-x-0.5'
                  }`}
                />
              </button>
            </div>
          ))}
        </div>

        <div className="flex justify-end gap-3 mt-8">
          <button onClick={onClose} className="text-sm text-gray-400 hover:text-white px-4 py-2 transition-colors">
            Cancel
          </button>
          <button
            onClick={save}
            disabled={saving}
            className="bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium px-5 py-2 rounded-lg transition-colors disabled:opacity-50"
          >
            {saved ? '✓ Saved' : saving ? 'Saving…' : 'Save'}
          </button>
        </div>
      </div>
    </div>
  )
}
