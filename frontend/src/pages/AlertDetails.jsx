import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, BrainCircuit, Trash2 } from 'lucide-react'
import api from '../services/api'

function Field({ label, value }) {
  return (
    <div>
      <p className="text-xs uppercase tracking-wider text-ink-500 mb-1">{label}</p>
      <p className="text-sm font-mono">{value ?? '—'}</p>
    </div>
  )
}

export default function AlertDetails() {
  const { id } = useParams()
  const [alert, setAlert] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    api.get(`/alerts/${id}`).then((res) => setAlert(res.data))
  }, [id])

  async function handleDelete() {
    if (!window.confirm('Delete this alert permanently?')) return
    await api.delete(`/alerts/${id}`)
    navigate('/alerts')
  }

  if (!alert) return <p className="text-ink-500">Loading…</p>

  return (
    <div className="max-w-3xl">
      <button onClick={() => navigate(-1)} className="flex items-center gap-1 text-sm text-ink-500 hover:text-ink-100 mb-4">
        <ArrowLeft size={16} /> Back
      </button>

      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="text-2xl font-semibold">{alert.alert_type}</h1>
          <p className="text-sm text-ink-500">Alert #{alert.id} · {new Date(alert.timestamp).toLocaleString()}</p>
        </div>
        <button onClick={handleDelete} className="flex items-center gap-1.5 text-sm text-signal-red hover:bg-signal-red/10 px-3 py-1.5 rounded-lg">
          <Trash2 size={14} /> Delete
        </button>
      </div>

      {alert.ai_explanation && (
        <div className="panel p-5 mb-6 border-signal-cyan/30">
          <h2 className="text-sm font-medium text-signal-cyan mb-2 flex items-center gap-2">
            <BrainCircuit size={16} /> AI Explanation
          </h2>
          <p className="text-sm text-ink-300 leading-relaxed">{alert.ai_explanation}</p>
        </div>
      )}

      <div className="panel p-6 grid grid-cols-2 gap-6 mb-6">
        <Field label="Source IP" value={alert.source_ip} />
        <Field label="Destination IP" value={alert.destination_ip} />
        <Field label="Source Port" value={alert.source_port} />
        <Field label="Destination Port" value={alert.destination_port} />
        <Field label="Protocol" value={alert.protocol} />
        <Field label="Category" value={alert.category} />
        <Field label="Reported Severity" value={alert.severity} />
        <Field label="AI Predicted Severity" value={alert.predicted_severity} />
        <Field label="Priority Score" value={alert.priority_score} />
        <Field label="Priority Level" value={alert.priority_level} />
        <Field label="Anomaly Status" value={alert.anomaly_status} />
        <Field label="Anomaly Score" value={alert.anomaly_score} />
        <Field label="Asset Criticality" value={alert.asset_criticality} />
        <Field label="Duplicate" value={alert.is_duplicate ? 'Yes' : 'No'} />
        <Field label="Cluster ID" value={alert.cluster_id} />
        <Field label="Incident ID" value={alert.incident_id} />
      </div>

      <div className="panel p-6">
        <p className="text-xs uppercase tracking-wider text-ink-500 mb-2">Message</p>
        <p className="text-sm leading-relaxed">{alert.message}</p>
      </div>
    </div>
  )
}
