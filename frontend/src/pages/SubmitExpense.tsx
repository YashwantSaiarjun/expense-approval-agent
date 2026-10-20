import { useState } from 'react'
import axios from 'axios'

const API = 'http://localhost:8000'

const STATUS_STYLES: Record<string, { bg: string; color: string; label: string }> = {
  auto_approved:      { bg: '#ECFDF5', color: '#059669', label: '✅ Auto Approved' },
  auto_rejected:      { bg: '#FEF2F2', color: '#DC2626', label: '❌ Auto Rejected' },
  confident_approved: { bg: '#ECFDF5', color: '#059669', label: '✅ AI Approved' },
  confident_rejected: { bg: '#FEF2F2', color: '#DC2626', label: '❌ AI Rejected' },
  pending_human_review: { bg: '#FFFBEB', color: '#D97706', label: '⏳ Pending Human Review' },
}

export default function SubmitExpense() {
  const [form, setForm] = useState({
    employee_id: '', amount: '', category: 'meals',
    description: '', expense_date: '', receipt_url: ''
  })
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setResult(null)
    try {
      const res = await axios.post(`${API}/expenses`, {
        ...form,
        amount: parseFloat(form.amount)
      })
      setResult(res.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Submission failed')
    }
    setLoading(false)
  }

  const inputStyle = {
    width: '100%', padding: '10px 14px',
    border: '1.5px solid var(--gray-200)',
    borderRadius: '8px', fontSize: '14px',
    outline: 'none', background: 'white'
  }

  const labelStyle = {
    display: 'block', fontSize: '13px',
    fontWeight: '600', color: 'var(--gray-600)',
    marginBottom: '6px'
  }

  return (
    <div>
      {/* PAGE HEADER */}
      <div style={{ marginBottom: '28px' }}>
        <h1 style={{ fontSize: '24px', fontWeight: '700', color: 'var(--navy)' }}>
          Submit Expense
        </h1>
        <p style={{ color: 'var(--gray-400)', fontSize: '14px', marginTop: '4px' }}>
          Submit your expense for automated policy review
        </p>
      </div>

      {/* FORM CARD */}
      <div style={{
        background: 'white', borderRadius: '12px',
        border: '1px solid var(--gray-200)', padding: '32px'
      }}>
        <form onSubmit={handleSubmit}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>

            <div>
              <label style={labelStyle}>Employee ID</label>
              <input style={inputStyle} placeholder="e.g. emp_001" value={form.employee_id}
                onChange={e => setForm({ ...form, employee_id: e.target.value })} required />
            </div>

            <div>
              <label style={labelStyle}>Amount ($)</label>
              <input style={inputStyle} type="number" placeholder="0.00" value={form.amount}
                onChange={e => setForm({ ...form, amount: e.target.value })} required />
            </div>

            <div>
              <label style={labelStyle}>Category</label>
              <select style={inputStyle} value={form.category}
                onChange={e => setForm({ ...form, category: e.target.value })}>
                {['meals', 'travel', 'office_supplies', 'software', 'client_entertainment', 'other']
                  .map(c => <option key={c} value={c}>{c.replace('_', ' ')}</option>)}
              </select>
            </div>

            <div>
              <label style={labelStyle}>Expense Date</label>
              <input style={inputStyle} type="date" value={form.expense_date}
                onChange={e => setForm({ ...form, expense_date: e.target.value })} required />
            </div>

            <div style={{ gridColumn: '1 / -1' }}>
              <label style={labelStyle}>Description</label>
              <textarea style={{ ...inputStyle, height: '80px', resize: 'vertical' }}
                placeholder="Describe the business purpose clearly..."
                value={form.description}
                onChange={e => setForm({ ...form, description: e.target.value })} required />
            </div>

            <div style={{ gridColumn: '1 / -1' }}>
              <label style={labelStyle}>Receipt URL <span style={{ color: 'var(--gray-400)', fontWeight: 400 }}>(optional)</span></label>
              <input style={inputStyle} placeholder="http://..." value={form.receipt_url}
                onChange={e => setForm({ ...form, receipt_url: e.target.value })} />
            </div>

          </div>

          <button type="submit" disabled={loading} style={{
            marginTop: '24px', padding: '12px 32px',
            background: loading ? 'var(--gray-400)' : 'var(--orange)',
            color: 'white', border: 'none', borderRadius: '8px',
            fontSize: '15px', fontWeight: '600', width: '100%',
            transition: 'background 0.15s'
          }}>
            {loading ? 'Submitting...' : 'Submit Expense'}
          </button>
        </form>
      </div>

      {/* ERROR */}
      {error && (
        <div style={{ marginTop: '16px', padding: '14px', background: '#FEF2F2',
          border: '1px solid #FECACA', borderRadius: '8px', color: '#DC2626', fontSize: '14px' }}>
          {error}
        </div>
      )}

      {/* RESULT */}
      {result && (() => {
        const s = STATUS_STYLES[result.status] || { bg: '#F3F4F6', color: '#4B5563', label: result.status }
        return (
          <div style={{ marginTop: '16px', padding: '20px', background: s.bg,
            border: `1px solid ${s.color}33`, borderRadius: '12px' }}>
            <div style={{ fontSize: '18px', fontWeight: '700', color: s.color }}>{s.label}</div>
            <div style={{ marginTop: '8px', fontSize: '14px', color: 'var(--gray-600)' }}>{result.message}</div>
            <div style={{ marginTop: '8px', fontSize: '12px', color: 'var(--gray-400)' }}>
              Expense ID: <code style={{ background: 'white', padding: '2px 6px', borderRadius: '4px' }}>{result.id}</code>
            </div>
          </div>
        )
      })()}
    </div>
  )
}