import { useState, type FormEvent } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import Layout from '../components/Layout'
import { api } from '../lib/api'

export default function ProjectsPage() {
  const queryClient = useQueryClient()
  const [form, setForm] = useState({ project_name: '', description: '' })
  const [editingId, setEditingId] = useState<number | null>(null)

  const { data: projects = [], isLoading } = useQuery<any[]>({
    queryKey: ['projects'],
    queryFn: async () => {
      const response = await api.get('/api/projects')
      return response.data
    },
  })

  const resetForm = () => {
    setForm({ project_name: '', description: '' })
    setEditingId(null)
  }

  const handleCreateOrUpdate = async (e: FormEvent) => {
    e.preventDefault()
    if (editingId) {
      await api.put(`/api/projects/${editingId}`, form)
    } else {
      await api.post('/api/projects', form)
    }
    resetForm()
    await queryClient.invalidateQueries({ queryKey: ['projects'] })
    await queryClient.invalidateQueries({ queryKey: ['dashboard'] })
    await queryClient.invalidateQueries({ queryKey: ['analytics'] })
  }

  const handleEdit = (project: any) => {
    setEditingId(project.id)
    setForm({ project_name: project.project_name, description: project.description || '' })
  }

  const handleDelete = async (projectId: number) => {
    await api.delete(`/api/projects/${projectId}`)
    await queryClient.invalidateQueries({ queryKey: ['projects'] })
    await queryClient.invalidateQueries({ queryKey: ['dashboard'] })
    await queryClient.invalidateQueries({ queryKey: ['analytics'] })
  }

  return (
    <Layout title="Projects">
      <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <div className="rounded-3xl border border-border bg-card p-6 shadow-glow">
          <h3 className="text-xl font-semibold text-foreground">Project List</h3>
          <div className="mt-4 space-y-3">
            {isLoading ? (
              <p className="text-sm text-muted-foreground">Loading projects…</p>
            ) : projects.length === 0 ? (
              <p className="text-sm text-muted-foreground">No projects created yet.</p>
            ) : (
              projects.map((project: any) => (
                <div key={project.id} className="rounded-3xl border border-border bg-background p-4">
                  <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                    <div>
                      <h4 className="font-semibold text-foreground">{project.project_name}</h4>
                      <p className="mt-1 text-sm text-muted-foreground">{project.description || 'No description'}</p>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      <button type="button" onClick={() => handleEdit(project)} className="rounded-2xl border border-border bg-background px-3 py-2 text-sm text-primary transition hover:bg-primary/10">
                        Edit
                      </button>
                      <button type="button" onClick={() => handleDelete(project.id)} className="rounded-2xl border border-border bg-background px-3 py-2 text-sm text-rose-500 transition hover:bg-rose-500/10">
                        Delete
                      </button>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
        <form onSubmit={handleCreateOrUpdate} className="rounded-3xl border border-border bg-card p-6 shadow-glow">
          <h3 className="text-xl font-semibold text-foreground">{editingId ? 'Edit Project' : 'Create Project'}</h3>
          <div className="mt-4 space-y-4">
            <input className="w-full rounded-3xl border border-border bg-background px-4 py-3 text-foreground outline-none focus:border-primary" placeholder="Project name" value={form.project_name} onChange={(e) => setForm({ ...form, project_name: e.target.value })} required />
            <textarea className="w-full rounded-3xl border border-border bg-background px-4 py-3 text-foreground outline-none focus:border-primary" placeholder="Description" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} rows={6} />
            <div className="flex flex-col gap-3 sm:flex-row">
              <button type="submit" className="rounded-3xl bg-primary px-4 py-3 text-sm font-semibold text-foreground transition hover:bg-accent">
                {editingId ? 'Update Project' : 'Create Project'}
              </button>
              {editingId ? (
                <button type="button" onClick={resetForm} className="rounded-3xl border border-border bg-background px-4 py-3 text-sm text-foreground transition hover:bg-primary/10">
                  Cancel
                </button>
              ) : null}
            </div>
          </div>
        </form>
      </div>
    </Layout>
  )
}
