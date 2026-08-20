export default function StatCard({ label, value, accent = 'text-signal-cyan', icon: Icon, suffix = '' }) {
  return (
    <div className="panel p-5 flex items-start justify-between">
      <div>
        <p className="text-xs uppercase tracking-wider text-ink-500 mb-2">{label}</p>
        <p className={`text-3xl font-mono font-semibold ${accent}`}>
          {value}{suffix}
        </p>
      </div>
      {Icon && (
        <div className={`p-2 rounded-lg bg-base-800 ${accent}`}>
          <Icon size={20} />
        </div>
      )}
    </div>
  )
}
