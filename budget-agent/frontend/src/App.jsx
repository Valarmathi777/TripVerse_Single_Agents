import { Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import Dashboard from './pages/Dashboard'

export default function App() {
  return (
    <div className="min-h-screen bg-paper">
      <header className="max-w-5xl mx-auto px-6 pt-8 flex items-center gap-2">
        <span className="text-xl">🧭</span>
        <span className="font-display text-lg text-ink tracking-tight">Budget Agent</span>
      </header>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/dashboard" element={<Dashboard />} />
      </Routes>
      <footer className="max-w-5xl mx-auto px-6 pb-10 pt-4">
        <p className="font-mono text-[11px] text-ink-light/60 uppercase tracking-widest">
          Budget Agent · Estimates from local datasets + live APIs, refined by AI
        </p>
      </footer>
    </div>
  )
}
