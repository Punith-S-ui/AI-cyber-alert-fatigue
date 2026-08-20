import { useEffect, useState } from 'react'
import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  PieChart, Pie, Cell, LineChart, Line, Legend,
} from 'recharts'
import { ShieldAlert, Flame, Radar as RadarIcon, ShieldCheck, TrendingDown, PlayCircle } from 'lucide-react'
import api from '../services/api'
import StatCard from '../components/StatCard'

const SEVERITY_COLORS = { LOW: '#3B82F6', MEDIUM: '#F5A623', HIGH: '#FB923C', CRITICAL: '#EF4444' }

export default function Dashboard() {
  const [summary, setSummary] = useState(null)
  const [severity, setSeverity] = useState([])
  const [categories, setCategories] = useState([])
  const [timeline, setTimeline] = useState([])
  const [processing, setProcessing] = useState(false)
  const [message, setMessage] = useState('')

  async function loadAll() {
    const [s, sev, cat, tl] = await Promise.all([
      api.get('/dashboard/summary'),
      api.get('/dashboard/severity'),
      api.get('/dashboard/categories'),
      api.get('/dashboard/timeline'),
    ])
    setSummary(s.data)
    setSeverity(sev.data)
    setCategories(cat.data)
    setTimeline(tl.data)
  }

  useEffect(() => { loadAll() }, [])

  async function runAnalysis() {
    setProcessing(true)
    setMessage('')
    try {
      const res = await api.post('/analysis/process')
      setMessage(`Pipeline complete: ${res.data.total_alerts} alerts processed, ${res.data.incidents_created} incidents created, ${res.data.alert_reduction_pct}% reduction.`)
      await loadAll()
    } catch (err) {
      setMessage(err.response?.data?.detail || 'Analysis failed.')
    } finally {
      setProcessing(false)
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-semibold">Operations Dashboard</h1>
          <p className="text-sm text-ink-500">Live signal from the correlation engine — no static figures.</p>
        </div>
        <button
          onClick={runAnalysis} disabled={processing}
          className="flex items-center gap-2 bg-signal-cyan text-base-950 font-medium rounded-lg px-4 py-2.5 text-sm hover:brightness-110 transition disabled:opacity-60"
        >
          <PlayCircle size={16} /> {processing ? 'Running AI pipeline…' : 'Run AI Analysis'}
        </button>
      </div>

      {message && (
        <div className="mb-6 text-sm text-signal-cyan bg-signal-cyan/10 border border-signal-cyan/30 rounded-lg px-4 py-3">
          {message}
        </div>
      )}

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
        <StatCard label="Total Alerts" value={summary?.total_alerts ?? '—'} icon={RadarIcon} accent="text-signal-blue" />
        <StatCard label="Critical" value={summary?.critical_alerts ?? '—'} icon={Flame} accent="text-signal-red" />
        <StatCard label="High Risk" value={summary?.high_alerts ?? '—'} icon={ShieldAlert} accent="text-signal-amber" />
        <StatCard label="Anomalies" value={summary?.anomalies ?? '—'} icon={RadarIcon} accent="text-signal-cyan" />
        <StatCard label="Active Incidents" value={summary?.active_incidents ?? '—'} icon={ShieldCheck} accent="text-signal-green" />
        <StatCard label="Fatigue Reduction" value={summary?.alert_fatigue_reduction_pct ?? '—'} suffix="%" icon={TrendingDown} accent="text-signal-green" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="panel p-5">
          <h2 className="text-sm font-medium text-ink-300 mb-4">Severity distribution</h2>
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie data={severity} dataKey="count" nameKey="severity" innerRadius={55} outerRadius={90} paddingAngle={3}>
                {severity.map((entry, i) => (
                  <Cell key={i} fill={SEVERITY_COLORS[entry.severity] || '#6B7C8D'} />
                ))}
              </Pie>
              <Legend />
              <Tooltip contentStyle={{ background: '#141C26', border: '1px solid #28374A', borderRadius: 8 }} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="panel p-5">
          <h2 className="text-sm font-medium text-ink-300 mb-4">Alert categories</h2>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={categories} layout="vertical" margin={{ left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1B2531" horizontal={false} />
              <XAxis type="number" stroke="#6B7C8D" fontSize={12} />
              <YAxis type="category" dataKey="category" stroke="#6B7C8D" fontSize={11} width={140} />
              <Tooltip contentStyle={{ background: '#141C26', border: '1px solid #28374A', borderRadius: 8 }} />
              <Bar dataKey="count" fill="#2DD4BF" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="panel p-5">
        <h2 className="text-sm font-medium text-ink-300 mb-4">Alerts over time</h2>
        <ResponsiveContainer width="100%" height={240}>
          <LineChart data={timeline}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1B2531" />
            <XAxis dataKey="date" stroke="#6B7C8D" fontSize={11} />
            <YAxis stroke="#6B7C8D" fontSize={12} />
            <Tooltip contentStyle={{ background: '#141C26', border: '1px solid #28374A', borderRadius: 8 }} />
            <Line type="monotone" dataKey="count" stroke="#2DD4BF" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
