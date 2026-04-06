import type { TabStatus } from '../api/client'

const STATUS_MAP: Record<TabStatus, { label: string; dot: string; badge: string }> = {
  active:           { label: 'Active',       dot: 'bg-emerald-400',   badge: 'text-emerald-400 bg-emerald-400/10' },
  inactive:         { label: 'Idle',         dot: 'bg-yellow-400',    badge: 'text-yellow-400 bg-yellow-400/10' },
  auto_closed:      { label: 'Auto-closed',  dot: 'bg-gray-500',      badge: 'text-gray-400 bg-gray-500/10' },
  manually_closed:  { label: 'Closed',       dot: 'bg-gray-500',      badge: 'text-gray-400 bg-gray-500/10' },
}

export function StatusBadge({ status }: { status: TabStatus }) {
  const s = STATUS_MAP[status] ?? STATUS_MAP.manually_closed
  return (
    <span className={`inline-flex items-center gap-1.5 text-xs font-medium px-2 py-0.5 rounded-full ${s.badge}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${s.dot}`} />
      {s.label}
    </span>
  )
}
