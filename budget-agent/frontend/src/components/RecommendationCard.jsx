export default function RecommendationCard({ suggestions = [], aiRecommendation }) {
  const source = aiRecommendation?.source
  return (
    <section className="grid grid-cols-1 lg:grid-cols-5 gap-6">
      <div className="lg:col-span-2 bg-white rounded-2xl border border-ink/10 shadow-card p-6">
        <h3 className="font-display text-xl text-ink mb-4">Savings Suggestions</h3>
        <ul className="space-y-3">
          {suggestions.length === 0 && (
            <li className="text-sm text-ink-light">No suggestions needed — you're in great shape.</li>
          )}
          {suggestions.map((s, i) => (
            <li key={i} className="flex items-start gap-2 text-sm text-ink">
              <span className="text-rupee mt-0.5">{s.startsWith('⚠') ? '' : ''}</span>
              <span>{s}</span>
            </li>
          ))}
        </ul>
      </div>

      <div className="lg:col-span-3 bg-gradient-to-br from-saffron/10 to-rupee/10 rounded-2xl border border-saffron/30 shadow-card p-6 relative">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-display text-xl text-ink">AI Recommendation</h3>
          <span className="font-mono text-[10px] uppercase tracking-widest text-ink-light/70 bg-white/60 px-2 py-1 rounded-full">
            {source === 'gemini' ? '✨ Gemini 2.5 Flash' : 'Rule-based'}
          </span>
        </div>
        <p className="text-ink leading-relaxed text-[15px]">
          {aiRecommendation?.text || 'Recommendation will appear here after calculating your budget.'}
        </p>
        {aiRecommendation?.note && (
          <p className="mt-3 font-mono text-[11px] text-ink-light/70 italic">
            {aiRecommendation.note}
          </p>
        )}
      </div>
    </section>
  )
}
