import { useNavigate } from 'react-router-dom'
import { tokenStore } from '../api/client'

const features = [
  { icon: '🧠', title: 'AI Summaries', desc: 'Gemini AI explains why you opened every tab — so you never lose context again.' },
  { icon: '⏱️', title: 'Inactivity Timers', desc: 'Custom reminders per tab. Get notified before something slips through the cracks.' },
  { icon: '🤖', title: 'Auto-Close', desc: 'Automatically close tabs that have been idle past your threshold.' },
  { icon: '🔍', title: 'Smart Search', desc: 'Search your entire tab history by AI summary, category, title, or URL.' },
  { icon: '📊', title: 'Live Dashboard', desc: 'All your tabs in one place — active, idle, and closed — updated in real time.' },
  { icon: '🔒', title: 'Fully Private', desc: 'Everything stays on your machine. Nothing is sent to third-party servers.' },
]

export default function Landing() {
  const navigate = useNavigate()
  const isLoggedIn = !!tokenStore.get()

  const handleCTA = () => navigate(isLoggedIn ? '/dashboard' : '/auth')

  return (
    <div className="min-h-screen bg-[#080810] text-white flex flex-col overflow-x-hidden">

      {/* ── Background effects ── */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-0 left-1/4 w-[800px] h-[600px] bg-indigo-600/10 rounded-full blur-[140px]" />
        <div className="absolute bottom-0 right-1/4 w-[600px] h-[500px] bg-purple-600/10 rounded-full blur-[120px]" />
        <div className="absolute inset-0" style={{
          backgroundImage: `linear-gradient(rgba(99,102,241,0.04) 1px, transparent 1px),
                            linear-gradient(90deg, rgba(99,102,241,0.04) 1px, transparent 1px)`,
          backgroundSize: '80px 80px',
        }} />
      </div>

      {/* ── Nav ── */}
      <nav className="relative z-10 flex items-center justify-between px-8 py-5 border-b border-white/[0.05]">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center text-sm shadow-lg shadow-indigo-500/20">
            🗂️
          </div>
          <span className="font-bold text-lg tracking-tight">TabSense</span>
        </div>
        <div className="flex items-center gap-3">
          {isLoggedIn ? (
            <button
              onClick={() => navigate('/dashboard')}
              className="bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium px-4 py-2 rounded-xl transition-colors"
            >
              Dashboard →
            </button>
          ) : (
            <>
              <button onClick={() => navigate('/auth')} className="text-sm text-gray-400 hover:text-white transition-colors px-3 py-2">
                Sign in
              </button>
              <button
                onClick={() => navigate('/auth')}
                className="bg-white/10 hover:bg-white/15 border border-white/10 text-white text-sm font-medium px-4 py-2 rounded-xl transition-all"
              >
                Get started
              </button>
            </>
          )}
        </div>
      </nav>

      {/* ── Hero ── */}
      <section className="relative z-10 flex flex-col items-center text-center px-6 pt-24 pb-20">
        <div className="inline-flex items-center gap-2 bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs font-medium px-4 py-1.5 rounded-full mb-8">
          <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-pulse" />
          Powered by Gemini AI
        </div>

        <h1 className="text-5xl md:text-7xl font-extrabold leading-[1.08] tracking-tight max-w-4xl mb-6">
          Stop losing track of{' '}
          <span className="bg-gradient-to-r from-indigo-400 via-violet-400 to-purple-400 bg-clip-text text-transparent">
            why you're here.
          </span>
        </h1>

        <p className="text-lg md:text-xl text-gray-400 max-w-2xl leading-relaxed mb-10">
          TabSense remembers the purpose of every tab and app you open, reminds you when they go idle, and cleans up the noise — so you can stay in flow.
        </p>

        <div className="flex items-center gap-4 flex-wrap justify-center">
          <button
            onClick={handleCTA}
            className="group relative bg-gradient-to-r from-indigo-600 to-violet-600 text-white font-semibold px-8 py-3.5 rounded-2xl text-base transition-all hover:scale-[1.03] hover:shadow-2xl hover:shadow-indigo-500/30"
          >
            {isLoggedIn ? 'Open Dashboard' : 'Get started free'}
            <span className="ml-2 group-hover:translate-x-0.5 inline-block transition-transform">→</span>
          </button>
        </div>
      </section>

      {/* ── App preview mockup ── */}
      <section className="relative z-10 flex justify-center px-6 pb-20">
        <div className="w-full max-w-3xl">
          <div className="bg-white/[0.03] border border-white/[0.08] rounded-2xl overflow-hidden shadow-2xl shadow-black/50 backdrop-blur-sm">
            {/* Fake title bar */}
            <div className="flex items-center gap-1.5 px-4 py-3 bg-white/[0.03] border-b border-white/[0.06]">
              <span className="w-3 h-3 rounded-full bg-red-500/60" />
              <span className="w-3 h-3 rounded-full bg-yellow-500/60" />
              <span className="w-3 h-3 rounded-full bg-green-500/60" />
              <div className="flex-1 flex justify-center">
                <span className="text-xs text-gray-600 bg-white/5 px-4 py-0.5 rounded-md">TabSense Dashboard</span>
              </div>
            </div>
            {/* Fake tabs */}
            <div className="p-4 space-y-2">
              {[
                { title: 'Linear — Sprint Planning', status: 'active', cat: 'Work', summary: 'Planning Q2 sprint tasks for the TabSense project.', time: '2m ago' },
                { title: 'Figma — Component Library', status: 'active', cat: 'Design', summary: 'Building reusable UI components for the design system.', time: '8m ago' },
                { title: 'Spotify — Lofi Chill Mix', status: 'inactive', cat: 'Music', summary: 'Background music for deep focus sessions.', time: '47m ago' },
                { title: 'Twitter / X', status: 'auto_closed', cat: 'Social', summary: 'Checking mentions and industry news.', time: '2h ago' },
              ].map((row, i) => (
                <div key={i} className={`flex items-center gap-3 rounded-xl px-4 py-3 transition-colors ${row.status === 'auto_closed' ? 'bg-white/[0.02] opacity-50' : 'bg-white/[0.04] hover:bg-white/[0.06]'}`}>
                  <span className={`w-2 h-2 rounded-full shrink-0 ${row.status === 'active' ? 'bg-emerald-400 shadow-[0_0_6px_rgba(52,211,153,0.6)]' : row.status === 'inactive' ? 'bg-yellow-400' : 'bg-gray-600'}`} />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-white truncate">{row.title}</span>
                      <span className="text-xs bg-indigo-500/15 text-indigo-300 px-2 py-0.5 rounded-full shrink-0">{row.cat}</span>
                    </div>
                    <p className="text-xs text-gray-500 truncate mt-0.5">{row.summary}</p>
                  </div>
                  <span className="text-xs text-gray-600 shrink-0">{row.time}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ── Features ── */}
      <section className="relative z-10 px-6 pb-24 max-w-5xl mx-auto w-full">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-white mb-3">Built for focused people</h2>
          <p className="text-gray-500">Everything you need to manage your digital workspace.</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {features.map((f, i) => (
            <div key={i} className="group bg-white/[0.03] border border-white/[0.07] rounded-2xl p-6 hover:bg-white/[0.05] hover:border-indigo-500/20 transition-all duration-300">
              <div className="w-11 h-11 rounded-xl bg-indigo-500/10 border border-indigo-500/15 flex items-center justify-center text-xl mb-4 group-hover:scale-110 transition-transform">
                {f.icon}
              </div>
              <h3 className="text-white font-semibold mb-2">{f.title}</h3>
              <p className="text-gray-500 text-sm leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── CTA Banner ── */}
      <section className="relative z-10 px-6 pb-20 max-w-3xl mx-auto w-full">
        <div className="bg-gradient-to-r from-indigo-600/20 via-violet-600/20 to-purple-600/20 border border-indigo-500/20 rounded-3xl p-10 text-center backdrop-blur-sm">
          <h2 className="text-2xl font-bold text-white mb-3">Ready to take back your focus?</h2>
          <p className="text-gray-400 mb-7 text-sm">Create your free account and start in seconds.</p>
          <button
            onClick={handleCTA}
            className="bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white font-semibold px-8 py-3 rounded-xl transition-all hover:scale-[1.02] hover:shadow-xl hover:shadow-indigo-500/25"
          >
            {isLoggedIn ? 'Go to Dashboard →' : 'Get started free →'}
          </button>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="relative z-10 border-t border-white/[0.05] px-8 py-5 text-center text-xs text-gray-700">
        TabSense · All data stored locally on your device · Privacy first
      </footer>
    </div>
  )
}
