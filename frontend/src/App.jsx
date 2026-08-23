import { Routes, Route, Navigate, NavLink } from 'react-router-dom'
import CitizenIntake from './pages/CitizenIntake.jsx'
import Dashboard from './pages/Dashboard.jsx'

export default function App() {
  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <span className="brand-glyph" aria-hidden="true">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              <path d="M3 17c2-4 4-6 9-6s7 2 9 6" stroke="#241704" strokeWidth="2.2" strokeLinecap="round" />
              <path d="M6 17v3M18 17v3M3 20h18" stroke="#241704" strokeWidth="2.2" strokeLinecap="round" />
            </svg>
          </span>
          <span className="brand-mark">जनसेतु</span>
          <span className="brand-name">JanSetu</span>
        </div>
        <nav className="topnav">
          <NavLink to="/citizen" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
            Report an issue
          </NavLink>
          <NavLink to="/dashboard" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
            Policymaker view
          </NavLink>
        </nav>
      </header>

      <main className="app-main">
        <Routes>
          <Route path="/" element={<Navigate to="/citizen" replace />} />
          <Route path="/citizen" element={<CitizenIntake />} />
          <Route path="/dashboard" element={<Dashboard />} />
        </Routes>
      </main>
    </div>
  )
}
