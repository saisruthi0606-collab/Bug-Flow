import { useEffect, useState, type FormEvent } from 'react'
import Layout from '../components/Layout'
import { api } from '../lib/api'
const API_URL = 'http://localhost:8000'
export default function ProfilePage() {
  const [user, setUser] = useState<any>(null)
  const [form, setForm] = useState({ full_name: '', avatar_url: '' })
  const [message, setMessage] = useState('')
  const [preview, setPreview] = useState<string | null>(null)

  useEffect(() => {
    api.get('/api/users/me').then(r => {
      setUser(r.data)
      setForm({ full_name: r.data.full_name, avatar_url: r.data.avatar_url || '' })
      setPreview(
  r.data.avatar_url
    ? `${API_URL}${r.data.avatar_url}`
    : null
)
    })
  }, [])

  const save = async (e: FormEvent) => {
    e.preventDefault()
    const r = await api.put('/api/users/me', form)
    setUser(r.data)
    setMessage('Profile saved')
    setTimeout(() => setMessage(''), 2000)
  }

  const uploadAvatar = async (e: any) => {
    const file = e.target.files?.[0]
    if (!file) return
    const fd = new FormData()
    fd.append('file', file)
    const r = await api.post('/api/users/me/avatar', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
   setForm({
  full_name: r.data.full_name,
  avatar_url: r.data.avatar_url || ''
})
    setPreview(`${API_URL}${r.data.avatar_url}`)
  }

  if (!user) return <Layout title="Profile"><p>Loading...</p></Layout>

  return (
    <Layout title="Profile">
      <div className="grid gap-6 lg:grid-cols-[.8fr_1.2fr]">
        <section className="rounded-3xl border border-border bg-card p-6 shadow-glow">
          <div className="flex items-center gap-4">
            <div className="h-16 w-16 overflow-hidden rounded-full bg-primary/15 text-2xl text-primary flex items-center justify-center">
              {preview ? <img src={preview} alt="avatar" className="h-full w-full object-cover" /> : user.full_name[0]}
            </div>
            <div>
              <h2 className="text-xl font-semibold">{user.full_name}</h2>
              <p className="text-sm text-muted-foreground">{user.role}</p>
            </div>
          </div>
          <div className="mt-6 space-y-3 text-sm">
            <p><span className="text-muted-foreground">Email</span><br />{user.email}</p>
            <p><span className="text-muted-foreground">Member since</span><br />{new Date(user.created_at).toLocaleDateString()}</p>
            <p><span className="text-muted-foreground">Last login</span><br />{user.last_login_at ? new Date(user.last_login_at).toLocaleString() : 'Not recorded'}</p>
          </div>
        </section>

        <section className="rounded-3xl border border-border bg-card p-6 shadow-glow">
          <div className="grid gap-4 sm:grid-cols-3">
            {[['Projects', user.projects], ['Assigned Issues', user.assigned_issues], ['Resolved Issues', user.resolved_issues]].map(([label, value]) => (
              <div key={String(label)} className="rounded-xl bg-background p-4">
                <p className="text-sm text-muted-foreground">{label}</p>
                <p className="mt-2 text-2xl font-semibold">{value}</p>
              </div>
            ))}
          </div>

          <form onSubmit={save} className="mt-6 space-y-3">
            <h3 className="text-lg font-semibold">Edit Profile</h3>
            <input className="w-full rounded-xl border border-border bg-background p-3" value={form.full_name} onChange={e => setForm({ ...form, full_name: e.target.value })} />
            <div>
              <label className="text-sm text-muted-foreground">Avatar</label>
              <input type="file" accept="image/*" onChange={uploadAvatar} className="mt-2" />
            </div>
            <div className="flex gap-2">
              <button className="rounded-xl bg-primary px-4 py-2">Save</button>
              <button type="button" onClick={() => { setForm({ full_name: user.full_name, avatar_url: user.avatar_url || '' }); setPreview(user.avatar_url || null); }} className="rounded-xl border border-border px-4 py-2">Cancel</button>
            </div>
            {message && <div className="text-sm text-success">{message}</div>}
          </form>
        </section>
      </div>
    </Layout>
  )
}
