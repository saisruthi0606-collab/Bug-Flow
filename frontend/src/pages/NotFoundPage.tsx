import { Link } from 'react-router-dom'

export default function NotFoundPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4">
      <div className="rounded-3xl border border-border bg-card p-12 text-center shadow-glow">
        <h1 className="text-6xl font-semibold text-accent">404</h1>
        <p className="mt-4 text-xl text-muted-foreground">The page you’re looking for doesn’t exist.</p>
        <Link to="/" className="mt-6 inline-block rounded-xl bg-primary px-5 py-3 font-semibold text-foreground">Go Home</Link>
      </div>
    </div>
  )
}
