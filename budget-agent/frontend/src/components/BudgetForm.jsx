import { useEffect, useState } from 'react'
import { getDestinations } from '../services/api'

const STYLES = [
  { value: 'Budget', label: 'Budget', desc: 'Hostels, buses, local thalis' },
  { value: 'Standard', label: 'Standard', desc: '3★ hotels, taxis, mid-range dining' },
  { value: 'Luxury', label: 'Luxury', desc: '5★ stays, private cabs, fine dining' },
]

export default function BudgetForm({ onSubmit, loading }) {
  const [destinations, setDestinations] = useState([])
  const [form, setForm] = useState({
    destination: '',
    days: 4,
    travelers: 2,
    budget: 25000,
    travel_style: 'Standard',
  })
  const [error, setError] = useState('')
  const [customSectors, setCustomSectors] = useState(false)
  const [sectors, setSectors] = useState({
    hotel: 10000,
    food: 6000,
    transport: 4000,
    attractions: 2000,
    shopping: 1500,
    emergency: 1500,
  })

  useEffect(() => {
    getDestinations()
      .then((list) => {
        setDestinations(list)
      })
      .catch(() => setError('Could not reach the backend. Is it running on port 8000?'))
  }, [])

  const update = (key, value) => setForm((f) => ({ ...f, [key]: value }))

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!form.destination) {
      setError('Please choose a destination.')
      return
    }
    setError('')
    const finalBudget = customSectors
      ? Object.values(sectors).reduce((a, b) => a + b, 0)
      : form.budget
    
    onSubmit({
      ...form,
      budget: finalBudget,
      sector_budgets: customSectors ? sectors : null,
    })
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="bg-white rounded-3xl border border-ink/10 shadow-card p-8 space-y-6"
    >
      <div>
        <h2 className="font-display text-2xl text-ink mb-1">Plan your trip budget</h2>
        <p className="text-sm text-ink-light">
          Tell us the shape of your trip — we'll build the full ledger.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
        <label className="block">
          <span className="font-mono text-xs uppercase tracking-widest text-ink-light">
            Destination
          </span>
          <input
            type="text"
            list="destinations-list"
            placeholder="e.g. Paris, Tokyo, Ooty..."
            className="mt-1.5 w-full rounded-xl border border-ink/15 bg-paper/40 px-3 py-2.5 text-ink focus:border-rupee outline-none"
            value={form.destination}
            onChange={(e) => update('destination', e.target.value)}
          />
          <datalist id="destinations-list">
            {destinations.map((d) => (
              <option key={d} value={d} />
            ))}
          </datalist>
        </label>

        <label className="block">
          <span className="font-mono text-xs uppercase tracking-widest text-ink-light">
            Number of Days
          </span>
          <input
            type="number"
            min={1}
            max={30}
            className="mt-1.5 w-full rounded-xl border border-ink/15 bg-paper/40 px-3 py-2.5 text-ink focus:border-rupee outline-none font-mono"
            value={form.days}
            onChange={(e) => update('days', Number(e.target.value))}
          />
        </label>

        <label className="block">
          <span className="font-mono text-xs uppercase tracking-widest text-ink-light">
            Number of Travelers
          </span>
          <input
            type="number"
            min={1}
            max={20}
            className="mt-1.5 w-full rounded-xl border border-ink/15 bg-paper/40 px-3 py-2.5 text-ink focus:border-rupee outline-none font-mono"
            value={form.travelers}
            onChange={(e) => update('travelers', Number(e.target.value))}
          />
        </label>

        <label className="block">
          <span className="font-mono text-xs uppercase tracking-widest text-ink-light">
            Total Budget (₹)
          </span>
          <input
            type="number"
            min={1000}
            step={500}
            disabled={customSectors}
            className={`mt-1.5 w-full rounded-xl border border-ink/15 px-3 py-2.5 text-ink focus:border-rupee outline-none font-mono ${
              customSectors ? 'bg-ink/5 border-dashed cursor-not-allowed' : 'bg-paper/40'
            }`}
            value={customSectors ? Object.values(sectors).reduce((a, b) => a + b, 0) : form.budget}
            onChange={(e) => update('budget', Number(e.target.value))}
          />
        </label>
      </div>

      <div className="flex items-center gap-2.5 py-1">
        <input
          type="checkbox"
          id="custom-sectors-checkbox"
          className="rounded text-rupee focus:ring-rupee w-4 h-4 cursor-pointer"
          checked={customSectors}
          onChange={(e) => setCustomSectors(e.target.checked)}
        />
        <label htmlFor="custom-sectors-checkbox" className="text-sm font-medium text-ink cursor-pointer select-none">
          Allocate budget per sector (Hotel, Food, Transport, Attractions, Shopping, Emergency)
        </label>
      </div>

      {customSectors && (
        <div className="bg-paper/40 border border-ink/10 rounded-2xl p-5 space-y-4">
          <div>
            <h3 className="font-semibold text-sm text-ink">Custom Sector Budgets</h3>
            <p className="text-xs text-ink-light mt-0.5">Specify how much budget you want to allocate to each sector.</p>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
            {Object.entries(sectors).map(([key, val]) => (
              <label key={key} className="block">
                <span className="font-mono text-[10px] uppercase tracking-wider text-ink-light capitalize">
                  {key} (₹)
                </span>
                <input
                  type="number"
                  min={0}
                  step={100}
                  className="mt-1 w-full rounded-lg border border-ink/15 bg-white px-2.5 py-1.5 text-sm text-ink focus:border-rupee outline-none font-mono"
                  value={val}
                  onChange={(e) => setSectors(prev => ({ ...prev, [key]: Number(e.target.value) }))}
                />
              </label>
            ))}
          </div>
        </div>
      )}

      <div>
        <span className="font-mono text-xs uppercase tracking-widest text-ink-light">
          Travel Style
        </span>
        <div className="mt-2 grid grid-cols-1 sm:grid-cols-3 gap-3">
          {STYLES.map((s) => (
            <button
              type="button"
              key={s.value}
              onClick={() => update('travel_style', s.value)}
              className={`text-left rounded-xl border px-4 py-3 transition-colors ${
                form.travel_style === s.value
                  ? 'border-rupee bg-rupee/10'
                  : 'border-ink/15 hover:border-ink/30'
              }`}
            >
              <p className="font-semibold text-ink text-sm">{s.label}</p>
              <p className="text-xs text-ink-light mt-0.5">{s.desc}</p>
            </button>
          ))}
        </div>
      </div>

      {error && (
        <p className="text-sm text-coral bg-coral-light rounded-lg px-3 py-2">{error}</p>
      )}

      <button
        type="submit"
        disabled={loading}
        className="w-full sm:w-auto bg-ink text-paper font-medium rounded-xl px-6 py-3 hover:bg-ink-light transition-colors disabled:opacity-50"
      >
        {loading ? 'Calculating…' : 'Calculate Budget'}
      </button>
    </form>
  )
}
