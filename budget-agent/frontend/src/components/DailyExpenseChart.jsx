import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from 'recharts'

function formatINR(amount) {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount)
}

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-ink text-paper rounded-lg px-3 py-2 font-mono text-xs shadow-card">
      <p className="font-semibold mb-0.5">{label}</p>
      <p>{formatINR(payload[0].value)}</p>
    </div>
  )
}

export default function DailyExpenseChart({ daily = [] }) {
  if (!daily.length) return null
  return (
    <section className="bg-white rounded-2xl border border-ink/10 shadow-card p-6">
      <h3 className="font-display text-xl text-ink mb-4">Daily Expense Chart</h3>
      <div style={{ width: '100%', height: 260 }}>
        <ResponsiveContainer>
          <BarChart data={daily} margin={{ top: 4, right: 8, left: 0, bottom: 4 }}>
            <CartesianGrid strokeDasharray="4 4" stroke="#16313D14" vertical={false} />
            <XAxis
              dataKey="day"
              tick={{ fontFamily: 'IBM Plex Mono', fontSize: 12, fill: '#2A4A59' }}
              axisLine={{ stroke: '#16313D22' }}
              tickLine={false}
            />
            <YAxis
              tick={{ fontFamily: 'IBM Plex Mono', fontSize: 11, fill: '#2A4A59' }}
              axisLine={false}
              tickLine={false}
              tickFormatter={(v) => `₹${Math.round(v / 1000)}k`}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: '#16313D0A' }} />
            <Bar dataKey="amount" fill="#2F6F5E" radius={[6, 6, 0, 0]} maxBarSize={56} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </section>
  )
}
