import { NavLink, useNavigate } from 'react-router-dom'
import {
  LayoutGrid, UploadCloud, ListFilter, ShieldAlert, Gauge,
  BrainCircuit, Settings, LogOut, Radar,
} from 'lucide-react'

const NAV_ITEMS = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutGrid },
  { to: '/alerts', label: 'Alert Explorer', icon: ListFilter },
  { to: '/upload', label: 'Alert Upload', icon: UploadCloud },
  { to: '/incidents', label: 'Incidents', icon: ShieldAlert },
  { to: '/fatigue', label: 'Fatigue Analytics', icon: Gauge },
  { to: '/model-insights', label: 'AI Model Insights', icon: BrainCircuit },
  { to: '/settings', label: 'Settings', icon: Settings },
]

export default function Sidebar({ user, onLogout }) {
  const navigate = useNavigate()

  return (
    <aside className="w-64 shrink-0 bg-base-900 border-r border-base-700 flex flex-col h-screen sticky top-0">
      <div className="flex items-center gap-2 px-5 h-16 border-b border-base-700">
        <Radar className="text-signal-cyan" size={22} />
        <span className="font-mono font-semibold tracking-tight text-lg">SentryGrid</span>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-1">
        {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
                isActive
                  ? 'bg-base-800 text-signal-cyan border border-base-600'
                  : 'text-ink-300 hover:bg-base-800 hover:text-ink-100 border border-transparent'
              }`
            }
          >
            <Icon size={17} />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="px-3 py-4 border-t border-base-700">
        <div className="flex items-center gap-3 px-3 py-2 mb-2">
          <div className="w-8 h-8 rounded-full bg-signal-cyan/20 text-signal-cyan flex items-center justify-center font-mono text-sm">
            {user?.full_name?.[0] ?? 'U'}
          </div>
          <div className="min-w-0">
            <p className="text-sm truncate">{user?.full_name}</p>
            <p className="text-xs text-ink-500 truncate">{user?.role}</p>
          </div>
        </div>
        <button
          onClick={() => { onLogout(); navigate('/login') }}
          className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-ink-300 hover:bg-base-800 hover:text-signal-red transition-colors focus-ring"
        >
          <LogOut size={16} /> Log out
        </button>
      </div>
    </aside>
  )
}
