import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom'
import SubmitExpense from './pages/SubmitExpense'
import ReviewQueue from './pages/ReviewQueue'
import AuditTrail from './pages/AuditTrail'
import './index.css'

function App() {
  return (
    <BrowserRouter>
      <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>

        <nav style={{
          background: '#0D1B2A',
          padding: '0 32px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          height: '64px',
          borderBottom: '3px solid #E85D04'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{
              width: '38px', height: '38px',
              background: '#E85D04',
              borderRadius: '8px',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontWeight: '800', fontSize: '18px', color: 'white'
            }}>P</div>
            <div>
              <div style={{ color: 'white', fontWeight: '700', fontSize: '18px', letterSpacing: '-0.3px' }}>
                Policy<span style={{ color: '#E85D04' }}>Pilot</span>
              </div>
              <div style={{ color: '#9CA3AF', fontSize: '11px' }}>
                Expense Intelligence Platform
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '4px' }}>
            {[
              { to: '/', label: 'Submit Expense' },
              { to: '/review', label: 'Review Queue' },
              { to: '/audit', label: 'Audit Trail' },
            ].map(({ to, label }) => (
              <NavLink key={to} to={to} end style={({ isActive }) => ({
                padding: '8px 16px',
                borderRadius: '6px',
                fontSize: '14px',
                fontWeight: '500',
                color: isActive ? 'white' : '#9CA3AF',
                background: isActive ? '#E85D04' : 'transparent',
                transition: 'all 0.15s'
              })}>
                {label}
              </NavLink>
            ))}
          </div>
        </nav>

        <main style={{ flex: 1, padding: '32px', maxWidth: '900px', margin: '0 auto', width: '100%' }}>
          <Routes>
            <Route path="/" element={<SubmitExpense />} />
            <Route path="/review" element={<ReviewQueue />} />
            <Route path="/audit" element={<AuditTrail />} />
          </Routes>
        </main>

        <footer style={{
          background: '#0D1B2A',
          color: '#9CA3AF',
          textAlign: 'center',
          padding: '16px',
          fontSize: '12px'
        }}>
          PolicyPilot — Intelligent expense approvals. Every decision, traceable.
        </footer>

      </div>
    </BrowserRouter>
  )
}

export default App