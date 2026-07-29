import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import BudgetForm from '../components/BudgetForm'
import { calculateBudget, getHistory, getHistoryDetail } from '../services/api'

export default function Home() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [history, setHistory] = useState([])
  const [historyLoading, setHistoryLoading] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    setHistoryLoading(true)
    getHistory()
      .then((list) => setHistory(list || []))
      .catch(() => {})
      .finally(() => setHistoryLoading(false))
  }, [])

  const handleSubmit = async (form) => {
    setLoading(true)
    setError('')
    try {
      const result = await calculateBudget(form)
      navigate('/dashboard', { state: { result, form } })
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          'Something went wrong reaching the budget engine. Is the backend running?'
      )
    } finally {
      setLoading(false)
    }
  }

  const handleLoadHistoryItem = async (item) => {
    setLoading(true)
    setError('')
    try {
      const fullResult = await getHistoryDetail(item.id)
      navigate('/dashboard', { 
        state: { 
          result: fullResult, 
          form: {
            destination: fullResult.destination,
            days: fullResult.days,
            travelers: fullResult.travelers,
            budget: fullResult.budget,
            travel_style: fullResult.travel_style
          } 
        } 
      })
    } catch (err) {
      setError('Could not load the history details. Database connection error.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen">
      <section className="max-w-5xl mx-auto px-6 pt-16 pb-10">
        <p className="font-mono text-xs uppercase tracking-[0.2em] text-rupee mb-3">
          Budget Agent · AI Travel Planner
        </p>
        <h1 className="font-display text-4xl sm:text-5xl text-ink leading-tight max-w-2xl">
          Know your trip's real cost{' '}
          <span className="italic text-saffron-dark">before</span> you book it.
        </h1>
        <p className="mt-4 text-ink-light max-w-xl text-[15px] leading-relaxed">
          Enter your destination and budget — the agent pulls hotel, food, transport,
          and attraction data to build a full daily ledger, then tells you exactly
          where to save if you're over.
        </p>
      </section>

      <section className="max-w-5xl mx-auto px-6 pb-24 grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="md:col-span-2">
          {error && (
            <div className="mb-4 text-sm text-coral bg-coral-light rounded-lg px-4 py-3">
              {error}
            </div>
          )}
          <BudgetForm onSubmit={handleSubmit} loading={loading} />
        </div>
        
        <div className="bg-white rounded-3xl border border-ink/10 shadow-card p-6 flex flex-col gap-4 self-start">
          <div>
            <h2 className="font-display font-medium text-lg text-ink">Recent Calculations</h2>
            <p className="text-xs text-ink-light">Reload your past travel ledgers</p>
          </div>
          
          {historyLoading ? (
            <div className="text-center py-6 text-xs text-ink-light font-mono animate-pulse">Loading history...</div>
          ) : history.length === 0 ? (
            <div className="text-center py-6 text-xs text-ink-light font-mono bg-paper/50 rounded-2xl border border-dashed border-ink/10">No history found</div>
          ) : (
            <div className="flex flex-col gap-2 overflow-y-auto max-h-[400px] pr-1">
              {history.map((item) => (
                <button
                  key={item.id}
                  onClick={() => handleLoadHistoryItem(item)}
                  className="flex items-center justify-between p-3 rounded-xl border border-ink/5 hover:border-ink/15 hover:bg-paper/40 transition-all text-left group"
                >
                  <div className="min-w-0 flex-1 pr-2">
                    <span className="font-display font-medium text-sm text-ink block group-hover:text-rupee transition-colors truncate">
                      {item.destination}
                    </span>
                    <span className="font-mono text-[10px] text-ink-light/80 block mt-0.5">
                      {item.days} day{item.days > 1 ? 's' : ''} · {item.travelers} traveler{item.travelers > 1 ? 's' : ''}
                    </span>
                  </div>
                  <div className="text-right flex-shrink-0">
                    <span className="font-mono text-xs font-semibold text-ink block">
                      {new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(item.total_estimated_cost)}
                    </span>
                    <span className="font-mono text-[9px] text-ink-light/60 block mt-0.5">
                      Budget: {new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(item.budget)}
                    </span>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      </section>
    </main>
  )
}
