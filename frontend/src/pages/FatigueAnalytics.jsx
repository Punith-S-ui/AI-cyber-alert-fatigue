import { useEffect, useState } from 'react'
import { ResponsiveContainer, FunnelChart, Funnel, LabelList, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts'
import { TrendingDown } from 'lucide-react'
import api from '../services/api'

export default function FatigueAnalytics() {
  const [fatigue, setFatigue] = useState(null)
  const [topSources, setTopSources] = useState([])

  useEffect(() => {
    api.get('/dashboard/fatigue').then((res) => setFatigue(res.data))
    api.get('/dashboard/top-sources').then((res) => setTopSources(res.data))
  }, [])

  if (!fatigue) return <p className="text-ink-500">Loading…</p>

  const funnelData = fatigue.funnel.map((f, i) => ({
    name: f.stage, value: f.count,
    fill: ['#3B82F6', '#2DD4BF', '#F5A623', '#34D399'][i % 4],
  }))

  return (
    <div>
      <h1 className="text-2xl font-semibold mb-1">Alert Fatigue Analytics</h1>
      <p className="text-sm text-ink-500 mb-6">How much analyst workload the correlation engine actually removed.</p>

      <div className="panel p-8 mb-6 flex items-center gap-6">
        <div className="p-4 rounded-full bg-signal-green/10 text-signal-green">
          <TrendingDown size={36} />
        </div>
        <div>
          <p className="text-xs uppercase tracking-wider text-ink-500 mb-1">Alert Reduction</p>
          <p className="text-5xl font-mono font-semibold text-signal-green">{fatigue.alert_reduction_pct}%</p>
          <p className="text-sm text-ink-500 mt-1">
            {fatigue.total_alerts} raw alerts condensed to {fatigue.final_incidents} actionable incidents
            (formula: (total − final) ÷ total × 100)
          </p>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        {[
          ['Total Alerts', fatigue.total_alerts],
          ['Duplicate Alerts', fatigue.duplicate_alerts],
          ['Unique Alerts', fatigue.unique_alerts],
          ['Final Incidents', fatigue.final_incidents],
        ].map(([label, value]) => (
          <div key={label} className="panel p-4">
            <p className="text-xs uppercase tracking-wider text-ink-500 mb-1">{label}</p>
            <p className="text-2xl font-mono">{value}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="panel p-5">
          <h2 className="text-sm font-medium text-ink-300 mb-4">Reduction funnel</h2>
          <ResponsiveContainer width="100%" height={280}>
            <FunnelChart>
              <Tooltip contentStyle={{ background: '#141C26', border: '1px solid #28374A', borderRadius: 8 }} />
              <Funnel dataKey="value" data={funnelData} isAnimationActive>
                <LabelList position="right" fill="#E6EDF3" stroke="none" dataKey="name" fontSize={12} />
              </Funnel>
            </FunnelChart>
          </ResponsiveContainer>
        </div>

        <div className="panel p-5">
          <h2 className="text-sm font-medium text-ink-300 mb-4">Top source IPs</h2>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={topSources}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1B2531" />
              <XAxis dataKey="source_ip" stroke="#6B7C8D" fontSize={10} angle={-30} textAnchor="end" height={60} />
              <YAxis stroke="#6B7C8D" fontSize={12} />
              <Tooltip contentStyle={{ background: '#141C26', border: '1px solid #28374A', borderRadius: 8 }} />
              <Bar dataKey="count" fill="#F5A623" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}
