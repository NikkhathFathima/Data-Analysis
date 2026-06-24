import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import toast from 'react-hot-toast'
import API, { useAuth } from '../api/auth'

export default function Register() {
  const [form, setForm] = useState({ name: '', email: '', password: '' })
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const submit = async e => {
    e.preventDefault()
    setLoading(true)
    try {
      const { data } = await API.post('/auth/register', form)
      login(data.token, data.user)
      toast.success(`Account created! Welcome, ${data.user.name}!`)
      navigate('/dashboard')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-wrapper">
      <div className="auth-card">
        <div className="auth-logo">
          <h1>📊 SalesIQ</h1>
          <p>Sales Intelligence Platform</p>
        </div>
        <h2>Create Account</h2>
        <form onSubmit={submit}>
          <div className="form-group">
            <label>Full Name</label>
            <input type="text" value={form.name} required
              onChange={e => setForm({...form, name: e.target.value})}
              placeholder="John Doe" />
          </div>
          <div className="form-group">
            <label>Email</label>
            <input type="email" value={form.email} required
              onChange={e => setForm({...form, email: e.target.value})}
              placeholder="you@company.com" />
          </div>
          <div className="form-group">
            <label>Password</label>
            <input type="password" value={form.password} required minLength={6}
              onChange={e => setForm({...form, password: e.target.value})}
              placeholder="Min 6 characters" />
          </div>
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Creating...' : 'Create Account'}
          </button>
        </form>
        <div className="auth-link">
          Already have an account? <Link to="/login">Sign in</Link>
        </div>
      </div>
    </div>
  )
}
