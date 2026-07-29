const CATEGORY_META = {
  hotel: { label: 'Hotel', icon: '🏨' },
  food: { label: 'Food', icon: '🍴' },
  transport: { label: 'Transport', icon: '🚕' },
  attractions: { label: 'Attractions', icon: '🎫' },
  shopping: { label: 'Shopping', icon: '🛍' },
  emergency: { label: 'Emergency', icon: '🛡' },
}

function formatINR(amount) {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount)
}

function formatLocal(amount, info) {
  if (!info || info.currency_code === 'INR') return ''
  const localVal = amount / info.rate_to_inr
  try {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: info.currency_code,
      maximumFractionDigits: 0,
    }).format(localVal)
  } catch (e) {
    return `${info.currency_symbol}${Math.round(localVal)}`
  }
}
export default function ExpenseBreakdown({ breakdown, currencyInfo }) {
  if (!breakdown) return null
  const total = Object.values(breakdown).reduce((a, b) => a + b, 0)

  return (
    <section>
      <div className="flex items-baseline justify-between mb-4">
        <h2 className="font-display text-2xl text-ink">Expense Breakdown</h2>
        <span className="font-mono text-xs text-ink-light uppercase tracking-widest">
          by category
        </span>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {Object.entries(breakdown).map(([key, value]) => {
          const meta = CATEGORY_META[key] || { label: key, icon: '💰' }
          const pct = total > 0 ? Math.round((value / total) * 100) : 0
          return (
            <div
              key={key}
              className="card-lift bg-white rounded-2xl border border-ink/10 shadow-card p-4 relative overflow-hidden"
            >
              <div className="flex items-center gap-2 text-sm text-ink-light mb-2">
                <span className="text-xl leading-none">{meta.icon}</span>
                <span className="font-medium">{meta.label}</span>
              </div>
              <p className="font-mono text-xl font-semibold text-ink">
                {formatINR(value)}
              </p>
              {currencyInfo && currencyInfo.currency_code !== 'INR' && (
                <p className="font-mono text-[11px] text-ink-light/60 mt-1 select-none">
                  ~{formatLocal(value, currencyInfo)} {currencyInfo.currency_code}
                </p>
              )}
              <div className="mt-3 h-1.5 w-full bg-ink/5 rounded-full overflow-hidden">
                <div
                  className="h-full bg-rupee rounded-full"
                  style={{ width: `${pct}%` }}
                />
              </div>
              <span className="absolute top-3 right-4 font-mono text-[10px] text-ink-light/60">
                {pct}%
              </span>
            </div>
          )
        })}
      </div>
    </section>
  )
}
