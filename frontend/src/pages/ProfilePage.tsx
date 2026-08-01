import Layout from '../components/Layout'
import { useEffect, useState } from 'react'
import { api } from '../lib/api'

export default function ProfilePage() {
  const [user, setUser] = useState<any>(null)

  useEffect(() => {
    api.get('/api/auth/me').then((res) => setUser(res.data))
  }, [])

  return (
    <Layout title="Profile">
      <div className="rounded-2xl border border-border bg-card p-6">
        {user ? <div className="space-y-3">
          <p className="text-sm text-muted-foreground">Full Name</p>
          <h3 className="text-2xl font-semibold text-foreground">{user.full_name}</h3>
          <p className="text-sm text-muted-foreground">Email</p>
          <p className="font-medium text-foreground">{user.email}</p>
          <p className="text-sm text-muted-foreground">Role</p>
          <p className="font-medium text-foreground">{user.role}</p>
        </div> : <p>Loading...</p>}
      </div>
    </Layout>
  )
}
