import { useState } from 'react'

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

export default function DestinationDetails({ details, currencyInfo }) {
  const [activeTab, setActiveTab] = useState('hotels')

  if (!details) return null

  const { hotels = [], restaurants = [], transport = [], attractions = [] } = details

  const tabs = [
    { id: 'hotels', label: '🏨 Hotels & Stays', count: hotels.length },
    { id: 'restaurants', label: '🍴 Food & Dining', count: restaurants.length },
    { id: 'attractions', label: '🎟 Sightseeing', count: attractions.length },
    { id: 'transport', label: '🚕 Transport', count: transport.length },
  ]

  const isIntl = currencyInfo && currencyInfo.currency_code !== 'INR'

  const renderPrice = (inrPrice) => {
    if (isIntl) {
      return (
        <div className="text-right">
          <span className="font-mono font-semibold text-ink">{formatINR(inrPrice)}</span>
          <span className="block font-mono text-[10px] text-ink-light/75">
            ~{formatLocal(inrPrice, currencyInfo)}
          </span>
        </div>
      )
    }
    return <span className="font-mono font-semibold text-ink">{formatINR(inrPrice)}</span>
  }

  const renderHotels = () => (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {hotels.map((h, i) => (
        <div key={i} className="bg-paper/40 rounded-2xl border border-ink/5 p-5 flex flex-col justify-between hover:border-ink/10 transition-colors shadow-sm">
          <div>
            <div className="flex justify-between items-start gap-2 mb-2">
              <span className={`text-[10px] font-mono uppercase tracking-wider px-2 py-0.5 rounded-full ${
                h.category === 'Luxury' ? 'bg-saffron/10 text-saffron-dark' :
                h.category === 'Standard' ? 'bg-rupee/10 text-rupee-dark' : 'bg-ink/5 text-ink-light'
              }`}>
                {h.category}
              </span>
              <span className="text-xs text-amber-500 font-medium">★ {h.rating.toFixed(1)}</span>
            </div>
            <h4 className="font-display font-medium text-base text-ink mb-1">{h.hotel_name}</h4>
            <p className="text-xs text-ink-light mb-4">👥 Max occupancy: {h.max_occupancy} guests</p>
          </div>
          <div className="flex justify-between items-end border-t border-ink/5 pt-3">
            <span className="text-xs text-ink-light">Per Night</span>
            {renderPrice(h.price_per_night)}
          </div>
        </div>
      ))}
      {hotels.length === 0 && <p className="col-span-full text-center py-6 text-sm text-ink-light">No hotels available for this destination.</p>}
    </div>
  )

  const renderRestaurants = () => (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {restaurants.map((r, i) => (
        <div key={i} className="bg-paper/40 rounded-2xl border border-ink/5 p-5 flex flex-col justify-between hover:border-ink/10 transition-colors shadow-sm">
          <div>
            <div className="flex justify-between items-start gap-2 mb-2">
              <span className={`text-[10px] font-mono uppercase tracking-wider px-2 py-0.5 rounded-full ${
                r.category === 'Luxury' ? 'bg-saffron/10 text-saffron-dark' :
                r.category === 'Standard' ? 'bg-rupee/10 text-rupee-dark' : 'bg-ink/5 text-ink-light'
              }`}>
                {r.category}
              </span>
              <span className="text-[10px] font-mono uppercase tracking-wider bg-ink/5 px-2 py-0.5 rounded-full text-ink-light">
                {r.meal_type}
              </span>
            </div>
            <h4 className="font-display font-medium text-base text-ink mb-1">{r.restaurant_name}</h4>
            <p className="text-xs text-ink-light mb-4">🍳 Cuisine: {r.cuisine}</p>
          </div>
          <div className="flex justify-between items-end border-t border-ink/5 pt-3">
            <span className="text-xs text-ink-light">Avg Person Cost</span>
            {renderPrice(r.avg_price_per_person)}
          </div>
        </div>
      ))}
      {restaurants.length === 0 && <p className="col-span-full text-center py-6 text-sm text-ink-light">No dining choices available for this destination.</p>}
    </div>
  )

  const renderAttractions = () => (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {attractions.map((a, i) => (
        <div key={i} className="bg-paper/40 rounded-2xl border border-ink/5 p-5 flex flex-col justify-between hover:border-ink/10 transition-colors shadow-sm">
          <div>
            <div className="flex justify-between items-start gap-2 mb-2">
              <span className={`text-[10px] font-mono uppercase tracking-wider px-2 py-0.5 rounded-full ${
                a.type === 'free' ? 'bg-emerald-500/10 text-emerald-700' : 'bg-coral/10 text-coral-dark'
              }`}>
                {a.type}
              </span>
              <span className="text-xs text-ink-light">⏱ {a.recommended_hours}h rec.</span>
            </div>
            <h4 className="font-display font-medium text-base text-ink mb-4">{a.attraction_name}</h4>
          </div>
          <div className="flex justify-between items-end border-t border-ink/5 pt-3">
            <span className="text-xs text-ink-light">Entry Fee</span>
            {renderPrice(a.entry_fee)}
          </div>
        </div>
      ))}
      {attractions.length === 0 && <p className="col-span-full text-center py-6 text-sm text-ink-light">No sightseeing options listed for this destination.</p>}
    </div>
  )

  const renderTransport = () => (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {transport.map((t, i) => (
        <div key={i} className="bg-paper/40 rounded-2xl border border-ink/5 p-5 flex flex-col justify-between hover:border-ink/10 transition-colors shadow-sm">
          <div>
            <div className="flex justify-between items-start gap-2 mb-2">
              <span className={`text-[10px] font-mono uppercase tracking-wider px-2 py-0.5 rounded-full ${
                t.category === 'Luxury' ? 'bg-saffron/10 text-saffron-dark' :
                t.category === 'Standard' ? 'bg-rupee/10 text-rupee-dark' : 'bg-ink/5 text-ink-light'
              }`}>
                {t.category}
              </span>
            </div>
            <h4 className="font-display font-medium text-base text-ink mb-1">{t.transport_mode}</h4>
            {t.fuel_price_per_litre > 0 && (
              <p className="text-xs text-ink-light mb-4">
                ⛽ Fuel Price: <span className="font-mono">{formatINR(t.fuel_price_per_litre)}/L</span>
                {isIntl && <span className="text-[10px] text-ink-light/75 ml-1">({formatLocal(t.fuel_price_per_litre, currencyInfo)}/L)</span>}
              </p>
            )}
          </div>
          <div className="flex justify-between items-end border-t border-ink/5 pt-3">
            <span className="text-xs text-ink-light">Daily Rental</span>
            {renderPrice(t.price_per_day)}
          </div>
        </div>
      ))}
      {transport.length === 0 && <p className="col-span-full text-center py-6 text-sm text-ink-light">No transport options listed for this destination.</p>}
    </div>
  )

  return (
    <section className="bg-white rounded-3xl border border-ink/10 shadow-card p-6 md:p-8 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-ink/10 pb-4">
        <div>
          <h2 className="font-display text-2xl text-ink">Local Destination Directory</h2>
          <p className="text-xs text-ink-light">Real catalog prices & options for stays, meals, transport, and visits</p>
        </div>
        <div className="flex flex-wrap gap-1 bg-ink/5 p-1 rounded-xl">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                activeTab === tab.id
                  ? 'bg-white text-ink shadow-sm'
                  : 'text-ink-light hover:text-ink hover:bg-white/50'
              }`}
            >
              {tab.label} <span className="text-[10px] opacity-60">({tab.count})</span>
            </button>
          ))}
        </div>
      </div>

      <div className="pt-2">
        {activeTab === 'hotels' && renderHotels()}
        {activeTab === 'restaurants' && renderRestaurants()}
        {activeTab === 'attractions' && renderAttractions()}
        {activeTab === 'transport' && renderTransport()}
      </div>
    </section>
  )
}