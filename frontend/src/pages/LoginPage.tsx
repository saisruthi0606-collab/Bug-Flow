import { useState, type FormEvent } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { api, setAuthToken } from '../lib/api'
import { Eye, EyeOff } from 'lucide-react'

export default function LoginPage() {
  const navigate = useNavigate()
  const [form, setForm] = useState({ email: '', password: '', remember: false })
  const [error, setError] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const res = await api.post('/api/auth/login', { email: form.email, password: form.password })
      setAuthToken(res.data.access_token, form.remember)
      navigate('/dashboard')
    } catch {
      setError('Invalid email or password')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4 py-10">
      <div className="w-full max-w-xl space-y-8 rounded-[2rem] border border-border bg-card p-10 shadow-glow md:p-14">
        <div className="space-y-3 text-center">
          <p className="text-sm uppercase tracking-[0.3em] text-primary/80">BugFlow</p>
          <h1 className="text-4xl font-semibold text-foreground">Welcome back</h1>
          <p className="text-sm text-muted-foreground">Log in to access your AI-powered defect lifecycle dashboard.</p>
        </div>
        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="space-y-2">
            <label className="text-sm font-medium text-foreground">Email</label>
            <input className="w-full rounded-3xl border border-border bg-card px-5 py-4 text-foreground outline-none transition focus:border-primary" placeholder="you@example.com" type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required />
          </div>
          <div className="space-y-2">
            <div className="flex items-center justify-between gap-3">
              <label className="text-sm font-medium text-foreground">Password</label>
              <button type="button" className="text-sm text-accent" onClick={() => setShowPassword((current) => !current)}>{showPassword ? 'Hide' : 'Show'}</button>
            </div>
            <div className="relative">
              <input className="w-full rounded-3xl border border-border bg-card px-5 py-4 text-foreground outline-none transition focus:border-primary" placeholder="Enter your password" type={showPassword ? 'text' : 'password'} value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required />
              <div className="pointer-events-none absolute right-4 top-1/2 -translate-y-1/2 text-muted-foreground">{showPassword ? <EyeOff size={18} /> : <Eye size={18} />}</div>
            </div>
          </div>
          <label className="flex items-center gap-2 text-sm text-muted-foreground">
            <input type="checkbox" className="h-4 w-4 rounded border-border bg-card text-primary" checked={form.remember} onChange={(e) => setForm({ ...form, remember: e.target.checked })} />
            Remember me
          </label>
          {error && <p className="text-sm text-rose-400">{error}</p>}
          <button type="submit" className="w-full rounded-3xl bg-primary px-5 py-4 text-sm font-semibold text-foreground transition hover:bg-accent" disabled={loading}>{loading ? 'Signing in...' : 'Login'}</button>
        </form>
        <p className="text-center text-sm text-muted-foreground">New to BugFlow? <Link to="/register" className="text-accent">Create an account</Link></p>
      </div>
    </div>
  )
}
