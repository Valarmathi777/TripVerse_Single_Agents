export default function Loading({ label = 'Calculating your trip…' }) {
  return (
    <div className="flex flex-col items-center justify-center gap-4 py-20">
      <div className="relative w-14 h-14">
        <div className="absolute inset-0 rounded-full border-4 border-ink/10" />
        <div className="absolute inset-0 rounded-full border-4 border-rupee border-t-transparent animate-spin" />
      </div>
      <p className="font-mono text-sm text-ink-light tracking-wide">{label}</p>
    </div>
  )
}
