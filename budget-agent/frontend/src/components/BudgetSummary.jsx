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
export default function BudgetSummary({ totalCost, budget, remaining, isOverBudget, currencyInfo }) {
  return (
    <section className="bg-ink text-paper rounded-3xl p-8 shadow-card relative overflow-hidden">
      <div
        className="absolute inset-0 opacity-[0.06] pointer-events-none"
        style={{
          backgroundImage:
            'repeating-linear-gradient(45deg, #EAF0EE 0, #EAF0EE 1px, transparent 1px, transparent 12px)',
        }}
      />
      <div className="relative grid grid-cols-1 sm:grid-cols-3 gap-6">
        <div>
          <p className="font-mono text-xs uppercase tracking-widest text-paper/60 mb-1">
            Estimated Cost
          </p>
          <p className="font-display text-3xl">{formatINR(totalCost)}</p>
          {currencyInfo && currencyInfo.currency_code !== 'INR' && (
            <p className="font-mono text-[11px] text-paper/70 mt-1 select-none">
              ~{formatLocal(totalCost, currencyInfo)} {currencyInfo.currency_code}
            </p>
          )}
        </div>
        <div>
          <p className="font-mono text-xs uppercase tracking-widest text-paper/60 mb-1">
            Budget
          </p>
          <p className="font-display text-3xl">{formatINR(budget)}</p>
           {currencyInfo && currencyInfo.currency_code !== 'INR' && (
            <p className="font-mono text-[11px] text-paper/70 mt-1 select-none">
              ~{formatLocal(budget, currencyInfo)} {currencyInfo.currency_code}
            </p>
          )}
        </div>
        <div>
          <p className="font-mono text-xs uppercase tracking-widest text-paper/60 mb-1">
            {isOverBudget ? 'Over By' : 'Remaining'}
          </p>
          <p
            className={`font-display text-3xl ${
              isOverBudget ? 'text-coral' : 'text-saffron'
            }`}
          >
            {formatINR(Math.abs(remaining))}
          </p>
          {currencyInfo && currencyInfo.currency_code !== 'INR' && (
            <p className="font-mono text-[11px] text-paper/70 mt-1 select-none">
              ~{formatLocal(Math.abs(remaining), currencyInfo)} {currencyInfo.currency_code}
            </p>
          )}
        </div>
      </div>

      <div className="relative mt-6 flex justify-start">
        <span
          className={`stamp-badge ${
            isOverBudget ? 'text-coral' : 'text-rupee-light'
          }`}
          style={{ backgroundColor: isOverBudget ? '#F0E4E122' : '#3E8C7722' }}
        >
          {isOverBudget ? '⚠ Over Budget' : '✓ On Budget'}
        </span>
      </div>
    </section>
  )
}
