import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search, Filter } from 'lucide-react'
import api from '../services/api'

const SEVERITY_COLORS = { LOW: 'text-signal-blue', MEDIUM: 'text-signal-amber', HIGH: 'text-orange-400', CRITICAL: 'text-signal-red' }

export default function AlertExplorer() {
  const [alerts, setAlerts] = useState([])
  const [total, setTotal] = useState(0)
  const [search, setSearch] = useState('')
  const [severity, setSeverity] = useState('')
  const [anomalyStatus, setAnomalyStatus] = useState('')
  const [offset, setOffset] = useState(0)
  const limit = 25
  const navigate = useNavigate()

  async function load() {
    const params = { limit, offset }
    if (search) params.search = search
    if (severity) params.severity = severity
    if (anomalyStatus) params.anomaly_status = anomalyStatus
    const res = await api.get('/alerts', { params })
    setAlerts(res.data.items)
    setTotal(res.data.total)
  }

  useEffect(() => { load() }, [offset, severity, anomalyStatus])

  function handleSearch(e) {
    e.preventDefault()
    setOffset(0)
    load()
  }

  return (
    <div>
      <h1 className="text-2xl font-semibold mb-1">Alert Explorer</h1>
      <p className="text-sm text-ink-500 mb-6">{total} alerts on record. Filter by severity, anomaly status, or free text.</p>

      <div className="panel p-4 mb-4 flex flex-wrap gap-3 items-center">
        <form onSubmit={handleSearch} className="flex items-center gap-2 flex-1 min-w-[240px]">
          <Search size={16} className="text-ink-500" />
          <input
            value={search} onChange={(e) => setSearch(e.target.value)}
            placeholder="Search message, source IP, destination IP…"
            className="flex-1 bg-transparent text-sm focus-ring outline-none placeholder:text-ink-500"
          />
        </form>
        <div className="flex items-center gap-2">
          <Filter size={14} className="text-ink-500" />
          <select value={severity} onChange={(e) => { setSeverity(e.target.value); setOffset(0) }}
            className="bg-base-800 border border-base-600 rounded-lg px-2 py-1.5 text-xs focus-ring outline-none">
            <option value="">All severities</option>
            {['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'].map(s => <option key={s} value={s}>{s}</option>)}
          </select>
          <select value={anomalyStatus} onChange={(e) => { setAnomalyStatus(e.target.value); setOffset(0) }}
            className="bg-base-800 border border-base-600 rounded-lg px-2 py-1.5 text-xs focus-ring outline-none">
            <option value="">All anomaly states</option>
            <option value="ANOMALY">Anomaly</option>
            <option value="NORMAL">Normal</option>
          </select>
        </div>
      </div>

      <div className="panel overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-base-800 text-ink-500 text-xs uppercase tracking-wider">
            <tr>
              <th className="text-left px-4 py-3">Time</th>
              <th className="text-left px-4 py-3">Type</th>
              <th className="text-left px-4 py-3">Source → Dest</th>
              <th className="text-left px-4 py-3">Severity</th>
              <th className="text-left px-4 py-3">Priority</th>
              <th className="text-left px-4 py-3">Anomaly</th>
              <th className="text-left px-4 py-3">Status</th>
            </tr>
          </thead>
          <tbody>
            {alerts.map((a) => (
              <tr key={a.id} onClick={() => navigate(`/alerts/${a.id}`)}
                className="border-t border-base-700 hover:bg-base-800/60 cursor-pointer transition-colors">
                <td className="px-4 py-3 text-ink-500 font-mono text-xs">{new Date(a.timestamp).toLocaleString()}</td>
                <td className="px-4 py-3">{a.alert_type}</td>
                <td className="px-4 py-3 font-mono text-xs text-ink-300">{a.source_ip} → {a.destination_ip}</td>
                <td className={`px-4 py-3 font-medium ${SEVERITY_COLORS[a.predicted_severity || a.severity]}`}>
                  {a.predicted_severity || a.severity}
                </td>
                <td className="px-4 py-3 font-mono">{a.priority_score ?? '—'}</td>
                <td className="px-4 py-3">
                  {a.anomaly_status === 'ANOMALY'
                    ? <span className="text-signal-red text-xs font-medium px-2 py-0.5 rounded bg-signal-red/10">ANOMALY</span>
                    : <span className="text-ink-500 text-xs">normal</span>}
                </td>
                <td className="px-4 py-3 text-xs text-ink-500">{a.status}</td>
              </tr>
            ))}
            {alerts.length === 0 && (
              <tr><td colSpan={7} className="px-4 py-10 text-center text-ink-500">No alerts match these filters.</td></tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="flex items-center justify-between mt-4 text-sm text-ink-500">
        <span>Showing {offset + 1}–{Math.min(offset + limit, total)} of {total}</span>
        <div className="flex gap-2">
          <button disabled={offset === 0} onClick={() => setOffset(Math.max(0, offset - limit))}
            className="px-3 py-1.5 rounded-lg bg-base-800 border border-base-600 disabled:opacity-40">Prev</button>
          <button disabled={offset + limit >= total} onClick={() => setOffset(offset + limit)}
            className="px-3 py-1.5 rounded-lg bg-base-800 border border-base-600 disabled:opacity-40">Next</button>
        </div>
      </div>
    </div>
  )
}
