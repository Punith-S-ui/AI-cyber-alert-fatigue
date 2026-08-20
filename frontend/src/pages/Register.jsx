import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Radar, ArrowRight, AlertCircle } from 'lucide-react'

export default function Register({ auth }) {
  const [form, setForm] = useState({ full_name: '', email: '', password: '', role: 'SECURITY_ANALYST' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  function update(field, value) {
    setForm((f) => ({ ...f, [field]: value }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await auth.register(form)
      navigate('/dashboard')
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed.')
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
          <h1 className="text-xl font-semibold mb-1">Create an account</h1>
          <p className="text-sm text-ink-500 mb-6">Join the SOC. Choose your role below.</p>

          {error && (
            <div className="mb-4 flex items-center gap-2 text-sm text-signal-red bg-signal-red/10 border border-signal-red/30 rounded-lg px-3 py-2">
              <AlertCircle size={16} /> {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs uppercase tracking-wider text-ink-500 mb-1.5">Full name</label>
              <input required value={form.full_name} onChange={(e) => update('full_name', e.target.value)}
                className="w-full bg-base-800 border border-base-600 rounded-lg px-3 py-2.5 text-sm focus-ring outline-none" />
            </div>
            <div>
              <label className="block text-xs uppercase tracking-wider text-ink-500 mb-1.5">Email</label>
              <input type="email" required value={form.email} onChange={(e) => update('email', e.target.value)}
                className="w-full bg-base-800 border border-base-600 rounded-lg px-3 py-2.5 text-sm focus-ring outline-none" />
            </div>
            <div>
              <label className="block text-xs uppercase tracking-wider text-ink-500 mb-1.5">Password</label>
              <input type="password" required minLength={6} value={form.password} onChange={(e) => update('password', e.target.value)}
                className="w-full bg-base-800 border border-base-600 rounded-lg px-3 py-2.5 text-sm focus-ring outline-none" />
            </div>
            <div>
              <label className="block text-xs uppercase tracking-wider text-ink-500 mb-1.5">Role</label>
              <select value={form.role} onChange={(e) => update('role', e.target.value)}
                className="w-full bg-base-800 border border-base-600 rounded-lg px-3 py-2.5 text-sm focus-ring outline-none">
                <option value="SECURITY_ANALYST">Security Analyst</option>
                <option value="ADMIN">Admin</option>
              </select>
            </div>
            <button type="submit" disabled={loading}
              className="w-full flex items-center justify-center gap-2 bg-signal-cyan text-base-950 font-medium rounded-lg px-4 py-2.5 text-sm hover:brightness-110 transition disabled:opacity-60">
              {loading ? 'Creating account…' : 'Create account'} <ArrowRight size={16} />
            </button>
          </form>

          <p className="mt-5 text-sm text-center text-ink-500">
            Already registered? <Link to="/login" className="text-signal-cyan hover:underline">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
