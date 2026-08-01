import type { ReactNode } from 'react'

export default function FeatureCard({ icon, title, description }: { icon: ReactNode; title: string; description: string }) {
  return (
    <div className="rounded-3xl border border-border bg-card p-6 shadow-glow transition hover:-translate-y-1 hover:border-accent/30">
      <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-3xl bg-accent/10 text-accent">
        {icon}
      </div>
      <h3 className="text-lg font-semibold text-foreground">{title}</h3>
      <p className="mt-3 text-sm leading-6 text-muted-foreground">{description}</p>
    </div>
  )
}
