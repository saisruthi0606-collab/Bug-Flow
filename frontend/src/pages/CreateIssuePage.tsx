import { useEffect, useState, type FormEvent, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import Layout from '../components/Layout'
import { api } from '../lib/api'
import type { Project, Sprint, UserListItem } from '../lib/types'

export default function CreateIssuePage() {
  const nav = useNavigate()
  const qc = useQueryClient()
  const [form, setForm] = useState<any>({
    title: '',
    description: '',
    priority: 'Medium',
    severity: 'Medium',
    project_id: 0,
    sprint_id: '',
    assigned_to: '',
    confirm_duplicate: false,
  })
  const [duplicates, setDuplicates] = useState<any[]>([])
  const [error, setError] = useState('')
  const [ai, setAi] = useState<any>(null)
  const [attachments, setAttachments] = useState<File[]>([])
  const [missingInfo, setMissingInfo] = useState<any[]>([])
  const dropRef = useRef<HTMLDivElement | null>(null)

  const { data: projects = [] } = useQuery<Project[]>({
    queryKey: ['projects'],
    queryFn: async () => (await api.get('/api/projects')).data,
  })
  const { data: sprints = [] } = useQuery<Sprint[]>({
    queryKey: ['sprints'],
    queryFn: async () => (await api.get('/api/sprints')).data,
  })
  const { data: users = [] } = useQuery<UserListItem[]>({
    queryKey: ['users'],
    queryFn: async () => (await api.get('/api/users')).data,
  })

  useEffect(() => {
    if (!form.project_id && projects[0]) setForm((x: any) => ({ ...x, project_id: projects[0].id }))
  }, [projects, form.project_id])

  const checkDuplicates = async () => {
    if (!form.title) return
    try {
      const res = await api.post('/api/issues/duplicates-check', {
        title: form.title,
        description: form.description,
        project_id: form.project_id,
      })
      setDuplicates(res.data || [])
    } catch (e: any) {
      // ignore transient errors for duplicate check
    }
  }

  const checkMissingInfo = async () => {
    if (!form.title) return
    try {
      const r = await api.post('/api/ai/missing-info', { title: form.title, description: form.description })
      setMissingInfo(r.data.warnings || [])
    } catch (e: any) {
      setMissingInfo([])
    }
  }

  const submit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    try {
      const payload = { ...form, sprint_id: form.sprint_id || null, assigned_to: form.assigned_to || null }
      const issueRes = await api.post('/api/issues', payload)
      const issueId = issueRes.data.id

      // upload attachments
      for (const f of attachments) {
        const fd = new FormData()
        fd.append('file', f)
        await api.post(`/api/issues/${issueId}/attachments`, fd, {
          headers: { 'Content-Type': 'multipart/form-data' },
        })
      }

      await qc.invalidateQueries({ queryKey: ['issues'] })
      await qc.invalidateQueries({ queryKey: ['dashboard'] })
      nav('/issues')
    } catch (err: any) {
      if (err?.response?.status === 409) {
        setDuplicates(err.response.data.detail.duplicates || [])
        setError('Possible duplicates found. Review and confirm to create.')
      } else {
        setError('Unable to create issue. Check input and try again.')
      }
    }
  }

  const enhance = async () => {
    setError('')
    try {
      const r = await api.post('/api/ai/enhance', { title: form.title, description: form.description })
      setAi(r.data)
      // Populate the enhanced description into the form so the user can review/edit it,
      // but do NOT auto-submit. Keep all other fields intact.
      setForm((x: any) => ({
        ...x,
        description: r.data.enhanced_description,
        priority: r.data.priority,
        severity: r.data.severity,
        category: r.data.category,
      }))
    } catch (e: any) {
      setError('AI enhancement failed. Try again.')
    }
  }

  const onFiles = (files: FileList | null) => {
    if (!files) return
    const allowedRe = /\.(png|jpg|jpeg|pdf|txt|docx|zip)$/i
    const maxSize = 10 * 1024 * 1024
    const arr = Array.from(files).filter((f) => allowedRe.test(f.name) && f.size <= maxSize)
    setAttachments((prev) => [...prev, ...arr])
  }

  // drag & drop handlers
  useEffect(() => {
    const el = dropRef.current
    if (!el) return
    const onDragOver = (e: DragEvent) => { e.preventDefault(); el.classList.add('ring-2', 'ring-dashed') }
    const onDragLeave = () => { el.classList.remove('ring-2', 'ring-dashed') }
    const onDrop = (e: DragEvent) => {
      e.preventDefault()
      el.classList.remove('ring-2', 'ring-dashed')
      const dt = e.dataTransfer
      if (dt?.files) onFiles(dt.files)
    }
    el.addEventListener('dragover', onDragOver)
    el.addEventListener('dragleave', onDragLeave)
    el.addEventListener('drop', onDrop)
    return () => {
      el.removeEventListener('dragover', onDragOver)
      el.removeEventListener('dragleave', onDragLeave)
      el.removeEventListener('drop', onDrop)
    }
  }, [dropRef.current])

  return (
    <Layout title="Create Issue">
      <div className="grid gap-6 xl:grid-cols-[1fr_.65fr]">
        <form onSubmit={submit} className="space-y-4 rounded-xl border border-border bg-card p-6">
          <input
            required
            className="w-full rounded-xl border border-border bg-background p-3"
            placeholder="Issue title"
            value={form.title}
            onBlur={() => { checkDuplicates(); checkMissingInfo() }}
            onChange={(e) => setForm({ ...form, title: e.target.value })}
          />

          <textarea
            required
            className="min-h-48 w-full rounded-xl border border-border bg-background p-3"
            placeholder="Describe the issue"
            value={form.description}
            onBlur={() => { checkDuplicates(); checkMissingInfo() }}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
          />

          <div className="grid gap-3 sm:grid-cols-2">
            <select
              className="rounded-xl border border-border bg-background p-3"
              value={form.priority}
              onChange={(e) => setForm({ ...form, priority: e.target.value })}
            >
              {['High', 'Medium', 'Low'].map((p) => (
                <option key={p} value={p}>{p}</option>
              ))}
            </select>

            <select
              className="rounded-xl border border-border bg-background p-3"
              value={form.severity}
              onChange={(e) => setForm({ ...form, severity: e.target.value })}
            >
              {['Critical', 'High', 'Medium', 'Low'].map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>

            <select
              className="rounded-xl border border-border bg-background p-3"
              value={form.project_id}
              onChange={(e) => setForm({ ...form, project_id: Number(e.target.value) })}
            >
              {projects.map((p) => (
                <option key={p.id} value={p.id}>{p.project_name}</option>
              ))}
            </select>

            <select
              className="rounded-xl border border-border bg-background p-3"
              value={form.sprint_id}
              onChange={(e) => setForm({ ...form, sprint_id: e.target.value })}
            >
              <option value="">No sprint</option>
              {sprints.filter((s) => s.project_id === form.project_id).map((s) => (
                <option key={s.id} value={s.id}>{s.name}</option>
              ))}
            </select>

            <select
              className="rounded-xl border border-border bg-background p-3"
              value={form.assigned_to}
              onChange={(e) => setForm({ ...form, assigned_to: e.target.value })}
            >
              <option value="">Unassigned</option>
              {users.filter((u) => u.role === 'Developer').map((u) => (
                <option key={u.id} value={u.id}>{u.full_name} (Developer)</option>
              ))}
            </select>
          </div>

          <label className="block">
            <span className="text-sm text-muted-foreground">Attachments (png,jpg,jpeg,pdf,docx,txt,zip) — max 10MB each</span>
            <div ref={dropRef} className="mt-2 rounded-md border border-border p-3">
              <input type="file" multiple onChange={(e) => onFiles(e.target.files)} className="w-full" />
              {attachments.length > 0 ? (
                <div className="mt-2 space-y-1 text-sm">
                  {attachments.map((f, i) => (
                    <div key={i} className="flex items-center justify-between">
                      <span>{f.name}</span>
                      <div className="flex items-center gap-2">
                        <span className="text-muted-foreground text-xs">{Math.round(f.size / 1024)} KB</span>
                        <button type="button" className="text-rose-500 text-xs" onClick={() => setAttachments((prev) => prev.filter((_, idx) => idx !== i))}>Remove</button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="mt-2 text-sm text-muted-foreground">Drag & drop files here or click to select.</p>
              )}
            </div>
          </label>

          {missingInfo.length > 0 && (
            <div className="rounded-xl border border-amber-500/40 bg-amber-500/10 p-3 text-sm">
              <div className="font-medium">Missing information</div>
              <ul className="mt-2 space-y-1">
                {missingInfo.map((w: any) => (
                  <li key={w.field} className="text-amber-600">{w.message}</li>
                ))}
              </ul>
              <p className="mt-2 text-xs text-muted-foreground">You can still create the issue and add details later.</p>
            </div>
          )}

          {duplicates.length > 0 && (
            <div className="rounded-xl border border-amber-500/40 bg-amber-500/10 p-3 text-sm">
              <div className="font-medium">Possible duplicates</div>
              <div className="mt-2">
                {duplicates.map((d: any) => (
                  <div key={d.id} className="py-1">
                    <a className="text-primary" href={`/issues/${d.id}`}>{d.title}</a>
                    <div className="text-muted-foreground text-xs">Similarity: {Math.round(d.similarity * 100)}%</div>
                  </div>
                ))}
              </div>
              <label className="mt-2 flex items-center gap-2 text-sm">
                <input type="checkbox" checked={form.confirm_duplicate} onChange={(e) => setForm({ ...form, confirm_duplicate: e.target.checked })} />
                Create anyway
              </label>
            </div>
          )}

          {error && <p className="text-rose-500">{error}</p>}

          <div className="flex items-center gap-3">
            <button className="rounded-xl bg-primary px-5 py-3 font-semibold">Create Issue</button>
            <button type="button" onClick={enhance} className="rounded-xl border border-border px-4 py-3">Improve with AI</button>
          </div>
        </form>

        <aside className="space-y-4 rounded-xl border border-border bg-card p-6">
          <h3 className="text-lg font-semibold">AI Report</h3>
          {ai ? (
            <div className="space-y-3 text-sm">
              <div><strong>Title suggestion:</strong> {ai.title || '—'}</div>
              <div><strong>Category:</strong> {ai.category || '—'}</div>
              <div><strong>Priority:</strong> {ai.priority || '—'}</div>
              <div><strong>Severity:</strong> {ai.severity || '—'}</div>
              <div><strong>Root cause:</strong> {ai.root_cause || '—'}</div>
              <div><strong>Suggested fix:</strong> {ai.resolution || '—'}</div>
              <div><strong>Confidence:</strong> {ai.confidence ?? '—'}</div>

              {ai.is_structured_report && (
                <>
                  <div className="pt-3 border-t border-border">
                    <div className="font-semibold text-primary">AI-ENHANCED ISSUE</div>
                    <div className="mt-2 rounded-md border border-border bg-background p-3 text-sm whitespace-pre-wrap">{ai.enhanced_description}</div>
                  </div>

                  <div className={ai.missing_information && ai.missing_information.length > 0 ? "rounded-xl border border-amber-500/40 bg-amber-500/10 p-3" : "rounded-xl border border-emerald-500/40 bg-emerald-500/10 p-3"}>
                    <div className="font-medium">{ai.missing_information && ai.missing_information.length > 0 ? 'MISSING INFORMATION' : 'Missing Information'}</div>
                    {ai.missing_information && ai.missing_information.length > 0 ? (
                      <ul className="mt-2 space-y-1">
                        {ai.missing_information.map((m: string, i: number) => (
                          <li key={i} className="text-amber-600">- {m}</li>
                        ))}
                      </ul>
                    ) : (
                      <p className="mt-2 text-emerald-600">No critical information is missing.</p>
                    )}
                  </div>
                </>
              )}

              <div className="pt-2"><strong>Full analysis:</strong><div className="rounded-md border border-border bg-background p-3 mt-2 text-sm whitespace-pre-wrap">{ai.analysis || ai.enhanced_description}</div></div>
            </div>
          ) : (
            <p className="text-muted-foreground">Click "Improve with AI" to generate an AI report. The enhanced description will populate the description field when applied.</p>
          )}
        </aside>
      </div>
    </Layout>
  )
}