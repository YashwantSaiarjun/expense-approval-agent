import { useState, useEffect } from 'react'
import axios from 'axios'

const API = 'http://localhost:8000'

export default function ReviewQueue() {
  const [expenses, setExpenses] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [actionNote, setActionNote] = useState<Record<string, string>>({})
  const [processing, setProcessing] = useState<string | null>(null)

  const fetchPending = async () => {
    setLoading(true)
    try {
      const res = await axios.get(`${API}/review/pending`)
      setExpenses(res.data)
    } catch {}
    setLoading(false)
  }

  useEffect(() => { fetchPending() }, [])

  const handleAction = async (id: string, action: 'approve' | 'reject') => {
    setProcessing(id)
    try {
      await axios.post(`${API}/review/${id}/${action}`, {
        manager_id: 'manager_admin',
        note: actionNote[id] || undefined
      })
      await fetchPending()
    } catch {}
    setProcessing(null)
  }

  return (
    <div>
      <div style={{ marginBottom: '28px', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
        <div>
          <h1 style={{ fontSize: '24px', fontWeight: '700', color: 'var(--navy)' }}>Review Queue</h1>
          <p style={{ color: 'var(--gray-400)', fontSize: '14px', marginTop: '4px' }}>
            Expenses flagged for human review
          </p>
        </div>
        <button onClick={fetchPending} style={{
          padding: '8px 16px', background: 'var(--orange)', color: 'white',
          border: 'none', borderRadius: '8px', fontSize: '13px', fontWeight: '600'
        }}>Refresh</button>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '60px', color: 'var(--gray-400)' }}>Loading...</div>
      ) : expenses.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '60px', background: 'white',
          borderRadius: '12px', border: '1px solid var(--gray-200)' }}>
          <div style={{ fontSize: '40px', marginBottom: '12px' }}>✅</div>
          <div style={{ fontWeight: '600', color: 'var(--navy)' }}>Queue is empty</div>
          <div style={{ color: 'var(--gray-400)', fontSize: '14px', marginTop: '4px' }}>No expenses pending review</div>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {expenses.map((exp: any) => (
            <div key={exp.id} style={{
              background: 'white', borderRadius: '12px',
              border: '1px solid var(--gray-200)', padding: '24px'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px' }}>
                <div>
                  <div style={{ fontWeight: '700', fontSize: '16px', color: 'var(--navy)' }}>
                    ${exp.amount} — {exp.category.replace('_', ' ')}
                  </div>
                  <div style={{ color: 'var(--gray-600)', fontSize: '14px', marginTop: '4px' }}>
                    {exp.description}
                  </div>
                  <div style={{ color: 'var(--gray-400)', fontSize: '12px', marginTop: '4px' }}>
                    Employee: {exp.employee_id}
                  </div>
                </div>
                <div style={{
                  padding: '4px 12px', background: 'var(--amber-light)',
                  color: 'var(--amber)', borderRadius: '20px',
                  fontSize: '12px', fontWeight: '600', height: 'fit-content'
                }}>⏳ Pending</div>
              </div>

              {exp.llm_reason && (
                <div style={{
                  padding: '12px', background: 'var(--gray-50)',
                  borderRadius: '8px', marginBottom: '16px',
                  fontSize: '13px', color: 'var(--gray-600)',
                  borderLeft: '3px solid var(--orange)'
                }}>
                  <strong>AI Note:</strong> {exp.llm_reason}
                  {exp.llm_confidence && (
                    <span style={{ color: 'var(--gray-400)', marginLeft: '8px' }}>
                      (confidence: {(exp.llm_confidence * 100).toFixed(0)}%)
                    </span>
                  )}
                </div>
              )}

              <input
                placeholder="Add a note (optional)..."
                value={actionNote[exp.id] || ''}
                onChange={e => setActionNote({ ...actionNote, [exp.id]: e.target.value })}
                style={{
                  width: '100%', padding: '8px 12px', marginBottom: '12px',
                  border: '1.5px solid var(--gray-200)', borderRadius: '8px',
                  fontSize: '13px', outline: 'none'
                }}
              />

              <div style={{ display: 'flex', gap: '10px' }}>
                <button onClick={() => handleAction(exp.id, 'approve')}
                  disabled={processing === exp.id}
                  style={{
                    flex: 1, padding: '10px', background: '#059669',
                    color: 'white', border: 'none', borderRadius: '8px',
                    fontWeight: '600', fontSize: '14px'
                  }}>
                  {processing === exp.id ? '...' : '✅ Approve'}
                </button>
                <button onClick={() => handleAction(exp.id, 'reject')}
                  disabled={processing === exp.id}
                  style={{
                    flex: 1, padding: '10px', background: '#DC2626',
                    color: 'white', border: 'none', borderRadius: '8px',
                    fontWeight: '600', fontSize: '14px'
                  }}>
                  {processing === exp.id ? '...' : '❌ Reject'}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}