import { useLocation, useNavigate } from 'react-router-dom'
import BudgetSummary from '../components/BudgetSummary'
import ExpenseBreakdown from '../components/ExpenseBreakdown'
import DestinationDetails from '../components/DestinationDetails'
import DailyExpenseChart from '../components/DailyExpenseChart'
import RecommendationCard from '../components/RecommendationCard'

export default function Dashboard() {
  const { state } = useLocation()
  const navigate = useNavigate()

  if (!state?.result) {
    return (
      <main className="min-h-screen flex flex-col items-center justify-center gap-4 px-6 text-center">
        <p className="font-display text-2xl text-ink">No trip calculated yet</p>
        <p className="text-ink-light text-sm max-w-sm">
          Head back and fill in your destination, days, travelers, and budget to see
          your ledger here.
        </p>
        <button
          onClick={() => navigate('/')}
          className="mt-2 bg-ink text-paper rounded-xl px-5 py-2.5 font-medium hover:bg-ink-light transition-colors"
        >
          Plan a trip
        </button>
      </main>
    )
  }

  const { result } = state
  const {
    destination,
    days,
    travelers,
    travel_style,
    budget,
    breakdown,
    total_estimated_cost,
    remaining,
    is_over_budget,
    daily_breakdown,
    savings_suggestions,
    ai_recommendation,
    currency_info,
  } = result

  return (
    <main className="min-h-screen">
      <div className="max-w-5xl mx-auto px-6 pt-12 pb-24 space-y-8">
        <div className="flex items-center justify-between">
          <div>
            <p className="font-mono text-xs uppercase tracking-[0.2em] text-rupee mb-1">
              {travel_style} Trip
            </p>
            <h1 className="font-display text-3xl text-ink">
              {destination} · {days} day{days > 1 ? 's' : ''} · {travelers} traveler
              {travelers > 1 ? 's' : ''}
            </h1>
          </div>
          <button
            onClick={() => navigate('/')}
            className="font-mono text-xs uppercase tracking-widest text-ink-light hover:text-ink border border-ink/15 rounded-full px-4 py-2 transition-colors"
          >
            ← New Trip
          </button>
        </div>
        {currency_info && currency_info.currency_code !== 'INR' && (
          <div className="bg-rupee/5 border border-rupee/20 rounded-2xl px-5 py-3 text-sm text-ink-light flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-lg">💱</span>
              <span>
                <strong>Money Conversion:</strong> Calculated in {currency_info.currency_code} and converted to INR.
              </span>
            </div>
            <span className="font-mono text-xs bg-white px-2 py-0.5 rounded-md shadow-sm">
              1 {currency_info.currency_code} = {currency_info.rate_to_inr} INR
            </span>
          </div>
        )}
        <BudgetSummary
          totalCost={total_estimated_cost}
          budget={budget}
          remaining={remaining}
          isOverBudget={is_over_budget}
          currencyInfo={currency_info}
        />

        <hr className="ledger-divider" />

        <ExpenseBreakdown breakdown={breakdown} currencyInfo={currency_info} />
        <DailyExpenseChart daily={daily_breakdown} />
        <DestinationDetails details={result.details} currencyInfo={currency_info} />

        <RecommendationCard
          suggestions={savings_suggestions}
          aiRecommendation={ai_recommendation}
        />
      </div>
    </main>
  )
}
