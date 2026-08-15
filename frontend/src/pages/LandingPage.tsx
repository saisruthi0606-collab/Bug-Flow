import { Link } from 'react-router-dom'
import {
  ArrowRight,
  Bug,
  ShieldCheck,
  Cpu,
  MessageCircle,
  FolderKanban,
  BarChart3,
} from 'lucide-react'
import { motion } from 'framer-motion'
import FeatureCard from '../components/FeatureCard'

const features = [
  {
    icon: <Cpu size={20} />,
    title: 'AI Defect Enhancement',
    description:
      'Transform raw issue text into clear, professional defect reports with intelligence.',
  },
  {
    icon: <Bug size={20} />,
    title: 'Smart Issue Tracking',
    description:
      'Search, filter, and triage issues with confidence across your backlog.',
  },
  {
    icon: <FolderKanban size={20} />,
    title: 'Project Management',
    description:
      'Organize work by project, progress, and team ownership.',
  },
  {
    icon: <BarChart3 size={20} />,
    title: 'Analytics Dashboard',
    description:
      'Visualize defect trends, priority distribution, and resolution performance.',
  },
  {
    icon: <MessageCircle size={20} />,
    title: 'Team Collaboration',
    description:
      'Keep stakeholders aligned with modern notes, assignments, and updates.',
  },
  {
    icon: <ShieldCheck size={20} />,
    title: 'Secure Authentication',
    description:
      'JWT-powered sign-in with role controls and enterprise-ready workflows.',
  },
]

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <nav className="mx-auto flex max-w-7xl items-center justify-between px-6 py-6 lg:px-10">
        <div className="flex items-center gap-3 text-xl font-semibold text-foreground">
          <div className="rounded-2xl bg-accent/15 p-2 text-accent">
            <Bug size={24} />
          </div>
          <span>BugFlow</span>
        </div>

        <div className="flex items-center gap-3">
          <Link
            to="/login"
            className="rounded-2xl border border-border px-4 py-2 text-sm text-muted-foreground transition hover:bg-card"
          >
            Login
          </Link>

          <Link
            to="/register"
            className="rounded-2xl bg-primary px-5 py-2.5 text-sm font-semibold text-foreground transition hover:bg-accent"
          >
            Get Started
          </Link>
        </div>
      </nav>

      <main className="mx-auto flex max-w-7xl flex-col gap-10 px-6 pb-16 pt-12 lg:flex-row lg:items-center lg:justify-between lg:gap-16">
        <motion.section
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="max-w-2xl"
        >
          <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-accent/30 bg-accent/10 px-4 py-2 text-sm text-accent">
            Intelligent Software Defect Tracking System
          </div>

          <h1 className="text-6xl font-bold leading-tight text-foreground sm:text-7xl lg:text-8xl">
            BugFlow
          </h1>

          <h2 className="mt-4 text-2xl font-semibold text-muted-foreground sm:text-3xl">
            AI-Powered Defect Lifecycle Management Platform
          </h2>

          <p className="mt-6 max-w-xl text-base text-muted-foreground sm:text-lg">
            AI-powered defect lifecycle management that helps software teams
            detect, track, prioritize, and resolve issues faster with
            intelligent workflows.
          </p>

          <p className="mt-6 text-2xl font-semibold text-accent sm:text-3xl">
            detect.debug.deliver
          </p>

          <div className="mt-10 flex flex-wrap gap-4">
            <Link
              to="/register"
              className="inline-flex items-center gap-2 rounded-3xl bg-primary px-6 py-3 text-sm font-semibold text-foreground transition hover:bg-accent"
            >
              Get Started
              <ArrowRight size={16} />
            </Link>

            <Link
              to="/login"
              className="inline-flex items-center gap-2 rounded-3xl border border-border px-6 py-3 text-sm text-foreground transition hover:bg-card"
            >
              Login
            </Link>
          </div>
        </motion.section>

        <motion.div
          initial={{ opacity: 0, scale: 0.96 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
          className="relative flex-1 overflow-hidden rounded-[2rem] border border-accent/10 bg-card p-8 shadow-glow"
        >
          <div className="absolute right-4 top-4 h-16 w-16 rounded-full bg-accent/20 blur-3xl" />
          <div className="absolute -left-10 top-20 h-24 w-24 rounded-full bg-border/20 blur-3xl" />

          <div className="relative overflow-hidden rounded-[1.75rem] border border-border bg-card p-8 shadow-2xl">
            <div className="flex items-center justify-between gap-4 text-foreground">
              <div>
                <p className="text-sm uppercase tracking-[0.3em] text-accent/80">
                  AI Defect Assistant
                </p>

                <h2 className="mt-4 text-3xl font-semibold">
                  Intelligent defect workflow
                </h2>
              </div>

              <div className="rounded-3xl bg-background px-4 py-3 text-xs uppercase tracking-[0.32em] text-accent">
                Live
              </div>
            </div>

            <div className="mt-8 grid gap-4 sm:grid-cols-2">
              <div className="rounded-3xl border border-border bg-background p-5">
                <p className="text-sm text-muted-foreground">Status</p>
                <p className="mt-3 text-2xl font-semibold text-foreground">
                  Live workflows
                </p>
              </div>

              <div className="rounded-3xl border border-border bg-background p-5">
                <p className="text-sm text-muted-foreground">Focus</p>
                <p className="mt-3 text-2xl font-semibold text-foreground">
                  Fast resolution
                </p>
              </div>
            </div>
          </div>
        </motion.div>
      </main>

      <section className="mx-auto max-w-7xl px-6 pb-20">
        <div className="grid gap-6 md:grid-cols-3">
          {features.map((feature) => (
            <FeatureCard
              key={feature.title}
              icon={feature.icon}
              title={feature.title}
              description={feature.description}
            />
          ))}
        </div>
      </section>

      <footer className="border-t border-border bg-card px-6 py-10 text-muted-foreground sm:px-10">
        <div className="mx-auto flex max-w-7xl flex-col gap-8 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p className="text-xl font-semibold text-foreground">
              BugFlow
            </p>

            <p className="mt-2 max-w-lg text-sm text-muted-foreground">
              AI-enhanced defect tracking for engineering teams who ship with
              confidence.
            </p>
          </div>

          <div className="grid gap-4 sm:grid-cols-3">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.25em] text-muted-foreground">
                Company
              </p>
              <p className="mt-3 text-sm">About</p>
              <p className="mt-2 text-sm">Privacy Policy</p>
            </div>

            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.25em] text-muted-foreground">
                Resources
              </p>
              <p className="mt-3 text-sm">Features</p>
              <p className="mt-2 text-sm">Documentation</p>
            </div>

            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.25em] text-muted-foreground">
                Support
              </p>
              <p className="mt-3 text-sm">Contact</p>
              <p className="mt-2 text-sm">GitHub</p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}