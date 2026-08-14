import { useState, type FormEvent } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { api } from '../lib/api'

export default function RegisterPage() {
  const navigate = useNavigate()
  const [form, setForm] = useState({ full_name: '', email: '', password: '', role: 'Reporter' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

 async function handleSubmit(e: FormEvent) {
  e.preventDefault()
  setError('')
  setLoading(true)

  try {
    await api.post('/api/auth/register', form)
    navigate('/login')
  } catch (err: any) {
    console.log(err)
    console.log(err.response)
    console.log(err.response?.data)

    setError(
      err.response?.data?.detail
        ? JSON.stringify(err.response.data.detail)
        : 'Unable to register'
    )
  } finally {
    setLoading(false)
  }
}

  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4">
      <div className="w-full max-w-md rounded-[2rem] border border-border bg-card p-8 shadow-glow">
        <h2 className="text-3xl font-bold text-foreground">Create your account</h2>
        <p className="mt-2 text-sm text-muted-foreground">Join BugFlow and start tracking issues with AI-assisted workflows.</p>
        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
          <input className="w-full rounded-3xl border border-border bg-background px-4 py-3 text-foreground outline-none focus:border-primary" placeholder="Full name" value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} />
          <input className="w-full rounded-3xl border border-border bg-background px-4 py-3 text-foreground outline-none focus:border-primary" placeholder="Email" type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
          <input className="w-full rounded-3xl border border-border bg-background px-4 py-3 text-foreground outline-none focus:border-primary" placeholder="Password" type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
          <select className="w-full rounded-3xl border border-border bg-background px-4 py-3 text-foreground outline-none focus:border-primary" value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}>
            <option value="Reporter">Reporter</option>
            <option value="Developer">Developer</option>
            <option value="QA Tester">QA Tester</option>
            <option value="Project Manager">Project Manager</option>
          </select>
          {error && <p className="text-sm text-rose-400">{error}</p>}
          <button className="w-full rounded-3xl bg-primary px-4 py-3 text-sm font-semibold text-foreground transition hover:bg-accent" disabled={loading}>{loading ? 'Creating account...' : 'Register'}</button>
        </form>
        <p className="mt-4 text-sm text-muted-foreground">Already have an account? <Link to="/login" className="text-accent">Login</Link></p>
      </div>
    </div>
  )
}
