import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Radar, ArrowRight, AlertCircle } from 'lucide-react'

export default function Login({ auth }) {
  const [email, setEmail] = useState('analyst@demo.local')
  const [password, setPassword] = useState('Analyst@123')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await auth.login(email, password)
      navigate('/dashboard')
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Check your credentials.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="flex items-center gap-2 justify-center mb-8">
          <Radar className="text-signal-cyan" size={28} />
          <span className="font-mono font-semibold text-2xl tracking-tight">SentryGrid</span>
        </div>

        <div className="panel p-8">
          <h1 className="text-xl font-semibold mb-1">Analyst sign-in</h1>
          <p className="text-sm text-ink-500 mb-6">Correlate alerts. Cut the noise. Focus on what matters.</p>

          {error && (
            <div className="mb-4 flex items-center gap-2 text-sm text-signal-red bg-signal-red/10 border border-signal-red/30 rounded-lg px-3 py-2">
              <AlertCircle size={16} /> {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs uppercase tracking-wider text-ink-500 mb-1.5">Email</label>
              <input
                type="email" required value={email} onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-base-800 border border-base-600 rounded-lg px-3 py-2.5 text-sm focus-ring outline-none"
              />
            </div>
            <div>
              <label className="block text-xs uppercase tracking-wider text-ink-500 mb-1.5">Password</label>
              <input
                type="password" required value={password} onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-base-800 border border-base-600 rounded-lg px-3 py-2.5 text-sm focus-ring outline-none"
              />
            </div>
            <button
              type="submit" disabled={loading}
              className="w-full flex items-center justify-center gap-2 bg-signal-cyan text-base-950 font-medium rounded-lg px-4 py-2.5 text-sm hover:brightness-110 transition disabled:opacity-60"
            >
              {loading ? 'Signing in…' : 'Sign in'} <ArrowRight size={16} />
            </button>
          </form>

          <div className="mt-5 text-xs text-ink-500 bg-base-800 rounded-lg p-3 leading-relaxed">
            Demo credentials — Analyst: <span className="font-mono text-ink-300">analyst@demo.local / Analyst@123</span><br />
            Admin: <span className="font-mono text-ink-300">admin@demo.local / Admin@123</span>
          </div>

          <p className="mt-5 text-sm text-center text-ink-500">
            No account? <Link to="/register" className="text-signal-cyan hover:underline">Register</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
