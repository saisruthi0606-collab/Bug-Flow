import { useState } from 'react'
import Layout from '../components/Layout'

export default function SettingsPage() {
  const [language] = useState('English')
  const [notifications] = useState(true)

  return (
    <Layout title="Settings">
      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-3xl border border-border bg-card p-6 shadow-glow">
          <h2 className="text-xl font-semibold text-foreground">Account</h2>
          <div className="mt-6 space-y-4">
            <div className="rounded-3xl border border-border bg-background p-4">
              <p className="text-sm text-muted-foreground">Language</p>
              <p className="mt-2 font-medium text-foreground">{language}</p>
            </div>
            <div className="rounded-3xl border border-border bg-background p-4">
              <p className="text-sm text-muted-foreground">Notifications</p>
              <p className="mt-2 font-medium text-foreground">{notifications ? 'Enabled' : 'Disabled'}</p>
            </div>
          </div>
        </div>
        <div className="rounded-3xl border border-border bg-card p-6 shadow-glow">
          <h2 className="text-xl font-semibold text-foreground">Security</h2>
          <div className="mt-6 space-y-4">
            <div className="rounded-3xl border border-border bg-background p-4">
              <p className="text-sm text-muted-foreground">Password</p>
              <p className="mt-2 font-medium text-foreground">Last updated 2 months ago</p>
            </div>
            <div className="rounded-3xl border border-border bg-background p-4">
              <p className="text-sm text-muted-foreground">Two-factor authentication</p>
              <p className="mt-2 font-medium text-foreground">Setup recommended for secure teams</p>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}
