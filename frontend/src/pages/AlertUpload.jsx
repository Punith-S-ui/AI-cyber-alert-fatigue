import { useState } from 'react'
import { UploadCloud, FileCheck2, AlertTriangle } from 'lucide-react'
import api from '../services/api'

export default function AlertUpload() {
  const [file, setFile] = useState(null)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const [manual, setManual] = useState({
    source_ip: '', destination_ip: '', alert_type: 'Port Scan',
    message: '', severity: 'MEDIUM', asset_criticality: 'MEDIUM',
  })
  const [manualMsg, setManualMsg] = useState('')

  async function handleUpload(e) {
    e.preventDefault()
    if (!file) return
    setLoading(true)
    setError('')
    setResult(null)
    const form = new FormData()
    form.append('file', file)
    try {
      const res = await api.post('/alerts/upload', form, { headers: { 'Content-Type': 'multipart/form-data' } })
      setResult(res.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed.')
    } finally {
      setLoading(false)
    }
  }

  async function handleManualSubmit(e) {
    e.preventDefault()
    setManualMsg('')
    try {
      await api.post('/alerts', manual)
      setManualMsg('Alert created successfully.')
      setManual({ ...manual, source_ip: '', destination_ip: '', message: '' })
    } catch (err) {
      setManualMsg(err.response?.data?.detail?.[0]?.msg || 'Could not create alert — check the fields.')
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-semibold mb-1">Alert Upload</h1>
      <p className="text-sm text-ink-500 mb-6">Bring alerts in from a CSV/JSON export, or log one manually.</p>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="panel p-6">
          <h2 className="text-sm font-medium text-ink-300 mb-4 flex items-center gap-2"><UploadCloud size={16} /> Bulk file upload</h2>
          <form onSubmit={handleUpload}>
            <label className="block border-2 border-dashed border-base-600 rounded-xl p-8 text-center cursor-pointer hover:border-signal-cyan transition-colors">
              <input type="file" accept=".csv,.json" className="hidden" onChange={(e) => setFile(e.target.files[0])} />
              <UploadCloud className="mx-auto mb-3 text-ink-500" size={28} />
              <p className="text-sm text-ink-300">{file ? file.name : 'Click to choose a .csv or .json file'}</p>
              <p className="text-xs text-ink-500 mt-1">Required columns: source_ip, destination_ip, alert_type, message</p>
            </label>
            <button type="submit" disabled={!file || loading}
              className="mt-4 w-full bg-signal-cyan text-base-950 font-medium rounded-lg px-4 py-2.5 text-sm hover:brightness-110 transition disabled:opacity-50">
              {loading ? 'Uploading…' : 'Upload alerts'}
            </button>
          </form>

          {error && (
            <div className="mt-4 flex items-center gap-2 text-sm text-signal-red bg-signal-red/10 border border-signal-red/30 rounded-lg px-3 py-2">
              <AlertTriangle size={16} /> {error}
            </div>
          )}

          {result && (
            <div className="mt-4 text-sm bg-base-800 border border-base-600 rounded-lg p-4">
              <p className="flex items-center gap-2 text-signal-green mb-2"><FileCheck2 size={16} /> {result.filename} processed</p>
              <p>Rows received: <span className="mono-num">{result.rows_received}</span></p>
              <p>Rows valid: <span className="mono-num text-signal-green">{result.rows_valid}</span></p>
              <p>Rows rejected: <span className="mono-num text-signal-red">{result.rows_rejected}</span></p>
              {result.errors?.length > 0 && (
                <details className="mt-2">
                  <summary className="cursor-pointer text-ink-500">View {result.errors.length} row warnings</summary>
                  <ul className="mt-2 space-y-1 text-xs text-ink-500 max-h-40 overflow-y-auto">
                    {result.errors.map((e, i) => <li key={i}>{e}</li>)}
                  </ul>
                </details>
              )}
              <p className="mt-3 text-xs text-ink-500">Go to Dashboard and click "Run AI Analysis" to process these new alerts.</p>
            </div>
          )}
        </div>

        <div className="panel p-6">
          <h2 className="text-sm font-medium text-ink-300 mb-4">Manual alert entry</h2>
          <form onSubmit={handleManualSubmit} className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <input placeholder="Source IP" required value={manual.source_ip}
                onChange={(e) => setManual({ ...manual, source_ip: e.target.value })}
                className="bg-base-800 border border-base-600 rounded-lg px-3 py-2 text-sm focus-ring outline-none" />
              <input placeholder="Destination IP" required value={manual.destination_ip}
                onChange={(e) => setManual({ ...manual, destination_ip: e.target.value })}
                className="bg-base-800 border border-base-600 rounded-lg px-3 py-2 text-sm focus-ring outline-none" />
            </div>
            <select value={manual.alert_type} onChange={(e) => setManual({ ...manual, alert_type: e.target.value })}
              className="w-full bg-base-800 border border-base-600 rounded-lg px-3 py-2 text-sm focus-ring outline-none">
              {['SSH Brute Force', 'Port Scan', 'SQL Injection Attempt', 'Malware Detection', 'Suspicious Login',
                'Privilege Escalation', 'Data Exfiltration', 'DDoS Activity', 'DNS Tunneling', 'Ransomware Activity'].map(t =>
                <option key={t} value={t}>{t}</option>)}
            </select>
            <textarea placeholder="Message / description" required rows={3} value={manual.message}
              onChange={(e) => setManual({ ...manual, message: e.target.value })}
              className="w-full bg-base-800 border border-base-600 rounded-lg px-3 py-2 text-sm focus-ring outline-none" />
            <div className="grid grid-cols-2 gap-3">
              <select value={manual.severity} onChange={(e) => setManual({ ...manual, severity: e.target.value })}
                className="bg-base-800 border border-base-600 rounded-lg px-3 py-2 text-sm focus-ring outline-none">
                {['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'].map(s => <option key={s}>{s}</option>)}
              </select>
              <select value={manual.asset_criticality} onChange={(e) => setManual({ ...manual, asset_criticality: e.target.value })}
                className="bg-base-800 border border-base-600 rounded-lg px-3 py-2 text-sm focus-ring outline-none">
                {['LOW', 'MEDIUM', 'HIGH'].map(s => <option key={s}>{s}</option>)}
              </select>
            </div>
            <button type="submit" className="w-full bg-base-800 border border-base-600 hover:border-signal-cyan text-sm rounded-lg px-4 py-2.5 transition">
              Log alert
            </button>
            {manualMsg && <p className="text-xs text-ink-300">{manualMsg}</p>}
          </form>
        </div>
      </div>
    </div>
  )
}
