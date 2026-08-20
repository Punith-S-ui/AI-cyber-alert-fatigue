import { useEffect, useState } from 'react'
import api from '../services/api'

export default function Settings({ user }) {
  const [me, setMe] = useState(user)

  useEffect(() => {
    api.get('/auth/me').then((res) => setMe(res.data))
  }, [])

  return (
    <div className="max-w-lg">
      <h1 className="text-2xl font-semibold mb-1">Profile & Settings</h1>
      <p className="text-sm text-ink-500 mb-6">Your account details for this SentryGrid workspace.</p>

      <div className="panel p-6 space-y-4">
        <div>
          <p className="text-xs uppercase tracking-wider text-ink-500 mb-1">Full name</p>
          <p className="text-sm">{me?.full_name}</p>
        </div>
        <div>
          <p className="text-xs uppercase tracking-wider text-ink-500 mb-1">Email</p>
          <p className="text-sm">{me?.email}</p>
        </div>
        <div>
          <p className="text-xs uppercase tracking-wider text-ink-500 mb-1">Role</p>
          <p className="text-sm">{me?.role}</p>
        </div>
      </div>

      <div className="panel p-6 mt-6">
        <p className="text-xs uppercase tracking-wider text-ink-500 mb-2">About this workspace</p>
        <p className="text-sm text-ink-300 leading-relaxed">
          SentryGrid is a demo AI-based cybersecurity alert correlation and fatigue reduction system.
          All alert data in this workspace is labeled DEMO DATA and generated for demonstration purposes only.
        </p>
      </div>
    </div>
  )
}
