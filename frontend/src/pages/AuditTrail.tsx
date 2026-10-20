import { useState } from 'react'
import axios from 'axios'

const API = 'http://localhost:8000'

const STATUS_COLORS: Record<string, string> = {
  auto_approved: '#059669',
  auto_rejected: '#DC2626',
  confident_approved: '#059669',
  confident_rejected: '#DC2626',
  pending_human_review: '#D97706',
  human_approved: '#059669',
  human_rejected: '#DC2626',
  ai_review: '#6366F1',
}

export default function AuditTrail() {
  const [expenseId, setExpenseId] = useState('')
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const fetchAudit = async () => {
    if (!expenseId.trim()) return
    setLoading(true)
    setError('')
    setData(null)
    try {
      const res = await axios.get(`${API}/expenses/${expenseId}/audit`)
      setData(res.data)
    } catch {
      setError('Expense not found. Check the ID and try again.')
    }
    setLoading(false)
  }

  return (
    <div>
      <div style={{ marginBottom: '28px' }}>
        <h1 style={{ fontSize: '24px', fontWeight: '700', color: 'var(--navy)' }}>Audit Trail</h1>
        <p style={{ color: 'var(--gray-400)', fontSize: '14px', marginTop: '4px' }}>
          Full decision history for any expense
        </p>
      </div>

      {/* SEARCH */}
      <div style={{
        background: 'white', borderRadius: '12px',
        border: '1px solid var(--gray-200)', padding: '24px',
        marginBottom: '24px'
      }}>
        <label style={{ display: 'block', fontSize: '13px', fontWeight: '600',
          color: 'var(--gray-600)', marginBottom: '8px' }}>
          Expense ID
        </label>
        <div style={{ display: 'flex', gap: '12px' }}>
          <input
            value={expenseId}
            onChange={e => setExpenseId(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && fetchAudit()}
            placeholder="Paste expense ID here..."
            style={{
              flex: 1, padding: '10px 14px',
              border: '1.5px solid var(--gray-200)',
              borderRadius: '8px', fontSize: '14px', outline: 'none'
            }}
          />
          <button onClick={fetchAudit} style={{
            padding: '10px 24px', background: 'var(--orange)',
            color: 'white', border: 'none', borderRadius: '8px',
            fontWeight: '600', fontSize: '14px'
          }}>
            {loading ? 'Loading...' : 'Search'}
          </button>
        </div>
      </div>

      {error && (
        <div style={{ padding: '14px', background: '#FEF2F2',
          border: '1px solid #FECACA', borderRadius: '8px',
          color: '#DC2626', fontSize: '14px' }}>
          {error}
        </div>
      )}

      {data && (
        <div style={{
          background: 'white', borderRadius: '12px',
          border: '1px solid var(--gray-200)', padding: '24px'
        }}>
          <div style={{ marginBottom: '20px', display: 'flex', justifyContent: 'space-between' }}>
            <div>
              <div style={{ fontSize: '13px', color: 'var(--gray-400)' }}>Expense ID</div>
              <code style={{ fontSize: '13px', color: 'var(--navy)' }}>{data.expense_id}</code>
            </div>
            <div style={{
              padding: '6px 14px',
              background: `${STATUS_COLORS[data.current_status] || '#6366F1'}22`,
              color: STATUS_COLORS[data.current_status] || '#6366F1',
              borderRadius: '20px', fontWeight: '600', fontSize: '13px'
            }}>
              {data.current_status.replace(/_/g, ' ').toUpperCase()}
            </div>
          </div>

          {/* TIMELINE */}
          <div style={{ position: 'relative' }}>
            {data.history.map((entry: any, i: number) => (
              <div key={i} style={{ display: 'flex', gap: '16px', marginBottom: '20px' }}>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                  <div style={{
                    width: '12px', height: '12px', borderRadius: '50%',
                    background: STATUS_COLORS[entry.to] || 'var(--orange)',
                    flexShrink: 0, marginTop: '4px'
                  }} />
                  {i < data.history.length - 1 && (
                    <div style={{ width: '2px', flex: 1, background: 'var(--gray-200)', marginTop: '4px' }} />
                  )}
                </div>
                <div style={{ flex: 1, paddingBottom: '8px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                    <span style={{ fontWeight: '600', fontSize: '14px', color: 'var(--navy)' }}>
                      {entry.to.replace(/_/g, ' ')}
                    </span>
                    <span style={{ fontSize: '12px', color: 'var(--gray-400)' }}>{entry.at}</span>
                  </div>
                  <div style={{ fontSize: '13px', color: 'var(--gray-600)', marginBottom: '2px' }}>
                    {entry.reason}
                  </div>
                  <div style={{ fontSize: '12px', color: 'var(--gray-400)' }}>
                    by {entry.actor}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}