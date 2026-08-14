import { Navigate, Route, Routes } from 'react-router-dom'
import { useEffect, useState, type ReactNode } from 'react'
import LandingPage from './pages/LandingPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DashboardPage from './pages/DashboardPage'
import ProjectsPage from './pages/ProjectsPage'
import IssuesPage from './pages/IssuesPage'
import CreateIssuePage from './pages/CreateIssuePage'
import IssueDetailPage from './pages/IssueDetailPage'
import ProfilePage from './pages/ProfilePage'
import AnalyticsPage from './pages/AnalyticsPage'
import SettingsPage from './pages/SettingsPage'
import SprintsPage from './pages/SprintsPage'
import NotFoundPage from './pages/NotFoundPage'
import { api, clearAuthToken, getAuthToken } from './lib/api'

function ProtectedRoute({ children }: { children: ReactNode }) {
  const token = getAuthToken()
  return token ? <>{children}</> : <Navigate to="/login" replace />
}

function App() {
  const [user, setUser] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = getAuthToken()
    if (!token) {
      setLoading(false)
      return
    }
    api.get('/api/auth/me')
      .then((res) => setUser(res.data))
      .catch(() => clearAuthToken())
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="flex min-h-screen items-center justify-center bg-background">Loading...</div>

  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/dashboard" element={<ProtectedRoute><DashboardPage user={user} /></ProtectedRoute>} />
      <Route path="/projects" element={<ProtectedRoute><ProjectsPage /></ProtectedRoute>} />
      <Route path="/issues" element={<ProtectedRoute><IssuesPage /></ProtectedRoute>} />
      <Route path="/sprints" element={<ProtectedRoute><SprintsPage /></ProtectedRoute>} />
      <Route path="/issues/new" element={<ProtectedRoute><CreateIssuePage /></ProtectedRoute>} />
      <Route path="/issues/:id" element={<ProtectedRoute><IssueDetailPage /></ProtectedRoute>} />
      <Route path="/issues/:id/edit" element={<ProtectedRoute><IssueDetailPage /></ProtectedRoute>} />
      <Route path="/profile" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
      <Route path="/analytics" element={<ProtectedRoute><AnalyticsPage /></ProtectedRoute>} />
      <Route path="/settings" element={<ProtectedRoute><SettingsPage /></ProtectedRoute>} />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  )
}

export default App

