import { useEffect, useState } from 'react'
import { BrainCircuit, Network, Radar, RefreshCcw } from 'lucide-react'
import api from '../services/api'

export default function ModelInsights() {
  const [info, setInfo] = useState(null)
  const [training, setTraining] = useState(false)
  const [trainMsg, setTrainMsg] = useState('')

  async function load() {
    const res = await api.get('/ml/model-info')
    setInfo(res.data)
  }

  useEffect(() => { load() }, [])

  async function retrain() {
    setTraining(true)
    setTrainMsg('')
    try {
      const res = await api.post('/ml/train')
      setTrainMsg(`Training complete — accuracy ${(res.data.accuracy * 100).toFixed(1)}% on ${res.data.n_test} held-out samples.`)
      load()
    } catch (err) {
      setTrainMsg(err.response?.data?.detail || 'Training failed (admin role required).')
    } finally {
      setTraining(false)
    }
  }

  if (!info) return <p className="text-ink-500">Loading…</p>

  const cards = [
    { title: 'Severity Classifier', icon: BrainCircuit, algo: info.severity_model.algorithm,
      detail: `Trained: ${info.severity_model.trained ? 'Yes' : 'No'} · Classes: ${info.severity_model.classes.join(', ')}` },
    { title: 'Alert Clustering', icon: Network, algo: info.clustering_model.algorithm,
      detail: 'Groups similar alert messages using TF-IDF vectors + K-Means, labeled by top terms per cluster.' },
    { title: 'Anomaly Detection', icon: Radar, algo: info.anomaly_model.algorithm,
      detail: 'Flags statistically unusual alerts using severity, source frequency, category rarity and timing features.' },
  ]

  return (
    <div>
      <h1 className="text-2xl font-semibold mb-1">AI Model Insights</h1>
      <p className="text-sm text-ink-500 mb-6">The three models powering correlation, prioritization, and noise reduction.</p>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mb-6">
        {cards.map(({ title, icon: Icon, algo, detail }) => (
          <div key={title} className="panel p-5">
            <div className="flex items-center gap-2 mb-3 text-signal-cyan">
              <Icon size={18} />
              <h2 className="text-sm font-medium">{title}</h2>
            </div>
            <p className="font-mono text-xs text-ink-500 mb-2">{algo}</p>
            <p className="text-sm text-ink-300 leading-relaxed">{detail}</p>
          </div>
        ))}
      </div>

      <div className="panel p-6">
        <h2 className="text-sm font-medium text-ink-300 mb-2">Retrain severity model</h2>
        <p className="text-sm text-ink-500 mb-4">
          Regenerates the synthetic labeled training set and retrains the Random Forest classifier from scratch. Admin role required.
        </p>
        <button onClick={retrain} disabled={training}
          className="flex items-center gap-2 bg-signal-cyan text-base-950 font-medium rounded-lg px-4 py-2.5 text-sm hover:brightness-110 transition disabled:opacity-60">
          <RefreshCcw size={16} className={training ? 'animate-spin' : ''} /> {training ? 'Training…' : 'Retrain model'}
        </button>
        {trainMsg && <p className="mt-3 text-sm text-ink-300">{trainMsg}</p>}
      </div>
    </div>
  )
}
