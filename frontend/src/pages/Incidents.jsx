import { useEffect, useState } from 'react'
import api from '../services/api'

const PRIORITY_COLORS = {
  LOW: 'bg-signal-blue/10 text-signal-blue', MEDIUM: 'bg-signal-amber/10 text-signal-amber',
  HIGH: 'bg-orange-400/10 text-orange-400', CRITICAL: 'bg-signal-red/10 text-signal-red',
}
const STATUS_OPTIONS = ['OPEN', 'INVESTIGATING', 'RESOLVED']

export default function Incidents() {
  const [incidents, setIncidents] = useState([])

  async function load() {
    const res = await api.get('/incidents')
    setIncidents(res.data)
  }

  useEffect(() => { load() }, [])

  async function updateStatus(id, status) {
    await api.put(`/incidents/${id}/status`, { status })
    load()
  }

  return (
    <div>
      <h1 className="text-2xl font-semibold mb-1">Incident Management</h1>
      <p className="text-sm text-ink-500 mb-6">Correlated groups of related alerts, ranked by risk score.</p>

      <div className="space-y-3">
        {incidents.map((inc) => (
          <div key={inc.id} className="panel p-5">
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className={`text-xs font-medium px-2 py-0.5 rounded ${PRIORITY_COLORS[inc.priority]}`}>{inc.priority}</span>
                  <h2 className="font-medium">{inc.title}</h2>
                </div>
                <p className="text-sm text-ink-500">{inc.description}</p>
                <div className="flex gap-6 mt-3 text-xs text-ink-500">
                  <span>Alerts: <span className="font-mono text-ink-300">{inc.alert_count}</span></span>
                  <span>Risk score: <span className="font-mono text-ink-300">{inc.risk_score}</span></span>
                  <span>First seen: <span className="font-mono text-ink-300">{new Date(inc.first_seen).toLocaleString()}</span></span>
                  <span>Last seen: <span className="font-mono text-ink-300">{new Date(inc.last_seen).toLocaleString()}</span></span>
                </div>
              </div>
              <select
                value={inc.status}
                onChange={(e) => updateStatus(inc.id, e.target.value)}
                className="bg-base-800 border border-base-600 rounded-lg px-3 py-1.5 text-xs focus-ring outline-none"
              >
                {STATUS_OPTIONS.map((s) => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
          </div>
        ))}
        {incidents.length === 0 && (
          <div className="panel p-10 text-center text-ink-500 text-sm">
            No incidents yet. Run the AI analysis from the Dashboard to correlate alerts into incidents.
          </div>
        )}
      </div>
    </div>
  )
}
