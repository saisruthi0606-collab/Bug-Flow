import { useEffect, useState, type FormEvent } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import Layout from '../components/Layout'
import { api } from '../lib/api'
import type { Activity, AiInvestigation, Attachment, Comment, Issue, MissingInfoWarning, Recommendation, UserListItem } from '../lib/types'

const NEXT: Record<string, string | undefined> = {
  'Open': 'In Progress',
  'Assigned': 'In Progress',
  'In Progress': 'In Review',
  'In Review': 'Resolved',
  'Resolved': 'Verified',
  'Verified': 'Closed',
}

export default function IssueDetailPage() {
  const { id } = useParams()
  const nav = useNavigate()
  const qc = useQueryClient()
  const { data: issue, refetch } = useQuery<Issue>({ queryKey: ['issue', id], queryFn: async () => (await api.get(`/api/issues/${id}`)).data })
  const { data: comments = [], refetch: refetchComments } = useQuery<Comment[]>({ queryKey: ['comments', id], queryFn: async () => (await api.get(`/api/issues/${id}/comments`)).data })
  const { data: attachments = [], refetch: refetchAttachments } = useQuery<Attachment[]>({ queryKey: ['attachments', id], queryFn: async () => (await api.get(`/api/issues/${id}/attachments`)).data })
  const { data: activities = [], refetch: refetchActivities } = useQuery<Activity[]>({ queryKey: ['activities', id], queryFn: async () => (await api.get(`/api/issues/${id}/activities`)).data })
  const { data: users = [] } = useQuery<UserListItem[]>({ queryKey: ['users'], queryFn: async () => (await api.get('/api/users')).data })
  const [comment, setComment] = useState('')
  const [editingComment, setEditingComment] = useState<number | null>(null)
  const [editingBody, setEditingBody] = useState('')
  const [form, setForm] = useState<any>(null)
  const [originalForm, setOriginalForm] = useState<any>(null)
  const [me, setMe] = useState<any>(null)
  const [assignee, setAssignee] = useState<number | ''>('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  // AI states
  const [recommendation, setRecommendation] = useState<Recommendation | null>(null)
  const [recLoading, setRecLoading] = useState(false)
  const [recError, setRecError] = useState('')
  const [analysis, setAnalysis] = useState<any>(null)
  const [analysisLoading, setAnalysisLoading] = useState(false)
  const [analysisError, setAnalysisError] = useState('')
  const [missingInfo, setMissingInfo] = useState<MissingInfoWarning[]>([])
  const [missingLoading, setMissingLoading] = useState(false)
  const [investigation, setInvestigation] = useState<AiInvestigation | null>(null)
  const [investigationLoading, setInvestigationLoading] = useState(false)
  const [investigationError, setInvestigationError] = useState('')

  useEffect(() => {
    api.get('/api/users/me').then((r) => setMe(r.data)).catch(() => setMe(null))
  }, [])

  useEffect(() => {
    if (issue) {
      const initialForm = {
        title: issue.title,
        description: issue.description || '',
        priority: issue.priority,
        severity: issue.severity,
        category: issue.category || ''
      }
      setForm(initialForm)
      setOriginalForm(initialForm)
      setAssignee(issue.assigned_to ?? '')
    }
  }, [issue])

  // Load missing-info warnings
  useEffect(() => {
    if (!issue) return
    setMissingLoading(true)
    api.get(`/api/issues/${issue.id}/missing-info`)
      .then((r) => setMissingInfo(r.data.warnings || []))
      .catch(() => setMissingInfo([]))
      .finally(() => setMissingLoading(false))
  }, [issue?.id])

  if (!issue || !form) return <Layout title="Issue Detail"><p>Loading...</p></Layout>

  const flash = (msg: string, isError = false) => {
    if (isError) { setError(msg); setSuccess('') }
    else { setSuccess(msg); setError('') }
    setTimeout(() => { setError(''); setSuccess('') }, 3000)
  }

  const save = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    try {
      await api.put(`/api/issues/${id}`, form)
      refetch(); qc.invalidateQueries({ queryKey: ['issues'] }); qc.invalidateQueries({ queryKey: ['dashboard'] })
      flash('Issue saved')
    } catch (err: any) {
      flash(err?.response?.data?.detail || 'Unable to save issue', true)
    }
  }

  const transition = async (next: string) => {
    setError('')
    try {
      await api.put(`/api/issues/${id}`, { status: next })
      refetch(); qc.invalidateQueries({ queryKey: ['issues'] }); qc.invalidateQueries({ queryKey: ['dashboard'] }); qc.invalidateQueries({ queryKey: ['sprints'] })
      flash(`Status changed to ${next}`)
    } catch (err: any) {
      flash(err?.response?.data?.detail || 'Invalid transition', true)
    }
  }

  const saveAssignee = async () => {
    setError('')
    try {
      await api.put(`/api/issues/${id}`, { assigned_to: assignee === '' ? null : Number(assignee) })
      refetch(); qc.invalidateQueries({ queryKey: ['issues'] }); qc.invalidateQueries({ queryKey: ['dashboard'] })
      flash('Assignee updated')
    } catch (err: any) {
      flash(err?.response?.data?.detail || 'Unable to update assignee', true)
    }
  }

  const deleteIssue = async () => {
    if (!confirm('Delete this issue? This will permanently remove the issue and its comments, attachments, activity and notifications.')) return
    setError('')
    try {
      await api.delete(`/api/issues/${id}`)
      qc.invalidateQueries({ queryKey: ['issues'] }); qc.invalidateQueries({ queryKey: ['dashboard'] })
      nav('/issues')
    } catch (err: any) {
      flash(err?.response?.data?.detail || 'Unable to delete issue', true)
    }
  }

  const addComment = async (e: FormEvent) => {
    e.preventDefault()
    if (!comment.trim()) return
    setError('')
    try {
      await api.post(`/api/issues/${id}/comments`, { body: comment.trim() })
      setComment('')
      refetchComments(); refetchActivities(); qc.invalidateQueries({ queryKey: ['activities'] }); qc.invalidateQueries({ queryKey: ['notifications'] })
    } catch (err: any) {
      flash(err?.response?.data?.detail || 'Unable to add comment', true)
    }
  }

  const startEditComment = (c: Comment) => { setEditingComment(c.id); setEditingBody(c.body) }
  const saveEditComment = async () => {
    if (!editingComment) return
    await api.put(`/api/issues/${id}/comments/${editingComment}`, { body: editingBody })
    setEditingComment(null); setEditingBody('')
    refetchComments(); refetchActivities()
  }
  const cancelEditComment = () => { setEditingComment(null); setEditingBody('') }
  const deleteComment = async (c: Comment) => {
    if (!confirm('Delete comment?')) return
    await api.delete(`/api/issues/${id}/comments/${c.id}`)
    refetchComments(); refetchActivities()
  }

  const upload = async (e: any) => {
    const file = e.target.files?.[0]
    if (!file) return
    setError('')
    try {
      const data = new FormData(); data.append('file', file)
      await api.post(`/api/issues/${id}/attachments`, data)
      refetchAttachments(); refetchActivities(); qc.invalidateQueries({ queryKey: ['activities'] }); qc.invalidateQueries({ queryKey: ['notifications'] })
    } catch (err: any) {
      flash(err?.response?.data?.detail || 'Upload failed', true)
    }
  }

  const downloadAttachment = (a: Attachment) => {
    window.open(`/api/issues/${id}/attachments/${a.id}/download`, '_blank')
  }

  const deleteAttachment = async (a: Attachment) => {
    if (!confirm('Delete attachment?')) return
    await api.delete(`/api/issues/${id}/attachments/${a.id}`)
    refetchAttachments(); refetchActivities(); qc.invalidateQueries({ queryKey: ['notifications'] })
  }

  const loadRecommendation = async () => {
    setRecLoading(true); setRecError(''); setRecommendation(null)
    try {
      const r = await api.get(`/api/issues/${id}/recommendation`)
      setRecommendation(r.data)
    } catch (e: any) {
      setRecError('No AI recommendation available yet. Try running AI analysis.')
    } finally {
      setRecLoading(false)
    }
  }

  const runAnalysis = async () => {
    setAnalysisLoading(true); setAnalysisError(''); setAnalysis(null)
    try {
      const r = await api.post('/api/ai/enhance', { description: `${issue.title}. ${issue.description || ''}`, issue_id: Number(id) })
      setAnalysis(r.data)
      qc.invalidateQueries({ queryKey: ['activities'] }); qc.invalidateQueries({ queryKey: ['notifications'] })
    } catch (e: any) {
      setAnalysisError('AI analysis failed. Please try again.')
    } finally {
      setAnalysisLoading(false)
    }
  }

  const loadInvestigation = async () => {
    setInvestigationLoading(true); setInvestigationError(''); setInvestigation(null)
    try {
      const r = await api.get(`/api/issues/${id}/ai-investigation`)
      setInvestigation(r.data)
    } catch (e: any) {
      setInvestigationError('AI investigation failed. Please try again.')
    } finally {
      setInvestigationLoading(false)
    }
  }

  const canDelete = me && (me.role === 'Admin' || me.role === 'Project Manager' || me.id === issue.reporter)
  const canAssign = me && (me.role === 'Admin' || me.role === 'Project Manager' || me.id === issue.reporter || me.id === issue.assigned_to)
  const canTransition = (target: string) => {
    if (!me) return false
    if (me.role === 'Admin' || me.role === 'Project Manager') return true
    if (target === 'Verified' || target === 'Closed') return me.role === 'QA Tester'
    if (target === 'Open' && issue.status === 'Closed') return me.role === 'QA Tester' || me.role === 'Reporter'
    return me.role === 'Developer' || me.role === 'QA Tester'
  }

  return (
    <Layout title="Issue Detail">
      <div className="grid gap-6 xl:grid-cols-[1fr_.75fr]">
        <div className="space-y-6">
          <section className="rounded-xl border border-border bg-card p-6">
            <div className="flex items-start justify-between">
              <div>
                <h1 className="text-2xl font-semibold">{issue.title}</h1>
                <div className="text-sm text-muted-foreground">{issue.project_name} · {issue.sprint_name || 'No sprint'}</div>
              </div>
              <div className="space-y-2 text-right">
                <div className="text-sm">Status: <span className="font-medium">{issue.status}</span></div>
                <div className="flex flex-wrap justify-end gap-2">
                  {NEXT[issue.status] && canTransition(NEXT[issue.status]!) && <button onClick={() => transition(NEXT[issue.status]!)} className="rounded-xl bg-primary px-3 py-2 text-sm">Move to {NEXT[issue.status]}</button>}
                  {issue.status === 'Closed' && canTransition('Open') && <button onClick={() => transition('Open')} className="rounded-xl border border-border px-3 py-2 text-sm">Reopen</button>}
                </div>
              </div>
            </div>

            {error && <div className="mt-3 rounded-xl border border-rose-500/40 bg-rose-500/10 p-3 text-sm text-rose-500">{error}</div>}
            {success && <div className="mt-3 rounded-xl border border-emerald-500/40 bg-emerald-500/10 p-3 text-sm text-emerald-500">{success}</div>}

            <form onSubmit={save} className="mt-4 space-y-3">
              <textarea className="w-full rounded-xl border border-border bg-background p-3" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
              <div className="grid grid-cols-2 gap-3">
                <select value={form.priority} onChange={(e) => setForm({ ...form, priority: e.target.value })} className="rounded-xl border border-border bg-background p-3">
                  {['High', 'Medium', 'Low'].map((p) => <option key={p} value={p}>{p}</option>)}
                </select>
                <select value={form.severity} onChange={(e) => setForm({ ...form, severity: e.target.value })} className="rounded-xl border border-border bg-background p-3">
                  {['Critical', 'High', 'Medium', 'Low'].map((s) => <option key={s} value={s}>{s}</option>)}
                </select>
              </div>
              <div className="flex gap-2">
                <button type="submit" className="rounded-xl bg-primary px-4 py-2">Save</button>
                <button type="button" onClick={() => { if (originalForm) setForm({ ...originalForm }) }} className="rounded-xl border border-border px-4 py-2">Reset</button>
                <button type="button" onClick={() => nav('/issues')} className="rounded-xl border border-border px-4 py-2">Back</button>
                {canDelete && <button type="button" onClick={deleteIssue} className="rounded-xl border border-rose-500/40 px-4 py-2 text-rose-500">Delete Issue</button>}
              </div>
            </form>

            {/* Assignee */}
            <div className="mt-6 rounded-xl border border-border bg-background p-4">
              <h4 className="font-semibold">Assignee</h4>
              <div className="mt-2 flex items-center gap-2">
                <select value={assignee} onChange={(e) => setAssignee(e.target.value === '' ? '' : Number(e.target.value))} disabled={!canAssign} className="flex-1 rounded-xl border border-border bg-background p-2">
                  <option value="">Unassigned</option>
                  {users.filter((u) => u.role === 'Developer').map((u) => <option key={u.id} value={u.id}>{u.full_name} (Developer)</option>)}
                </select>
                {canAssign && <button onClick={saveAssignee} className="rounded-xl bg-primary px-3 py-2 text-sm">Assign</button>}
              </div>
              <div className="mt-2 text-sm text-muted-foreground">Current: {issue.assignee_name || 'Unassigned'}</div>
            </div>

            <div className="mt-6">
              <h4 className="font-semibold">Attachments</h4>
              <div className="mt-2 space-y-2">
                {attachments.length === 0 && <div className="text-sm text-muted-foreground">No attachments</div>}
                {attachments.map((a) => {
                  const isImage = /image\/(png|jpe?g|gif|webp|bmp)/i.test(a.content_type || '') || /\.(png|jpe?g|gif|webp|bmp)$/i.test(a.original_filename || '')
                  const previewUrl = `/api/issues/${id}/attachments/${a.id}/download`
                  return (
                    <div key={a.id} className="rounded-xl border border-border bg-background p-3">
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex items-start gap-3">
                          {isImage ? (
                            <img src={previewUrl} alt={a.original_filename} className="h-16 w-16 rounded-md object-cover border border-border" />
                          ) : (
                            <div className="flex h-16 w-16 items-center justify-center rounded-md border border-border bg-secondary text-xs text-muted-foreground">FILE</div>
                          )}
                          <div>
                            <div className="font-medium">{a.original_filename}</div>
                            <div className="text-xs text-muted-foreground">{a.uploader_name} · {new Date(a.created_at).toLocaleString()}</div>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <button onClick={() => downloadAttachment(a)} className="text-sm text-primary">Open</button>
                          {me && (me.id === a.uploaded_by || me.role === 'Admin') && <button onClick={() => deleteAttachment(a)} className="text-sm text-rose-500">Delete</button>}
                        </div>
                      </div>
                    </div>
                  )
                })}
                <div className="mt-2">
                  <input type="file" onChange={upload} />
                </div>
              </div>
            </div>

          </section>

          <section className="rounded-xl border border-border bg-card p-6">
            <h3 className="text-lg font-semibold">Comments</h3>
            <form onSubmit={addComment} className="mt-3 space-y-3">
              <textarea value={comment} onChange={(e) => setComment(e.target.value)} placeholder="Write a comment" className="w-full rounded-xl border border-border bg-background p-3" />
              <div className="flex gap-2"><button className="rounded-xl bg-primary px-4 py-2">Add Comment</button></div>
            </form>

            <div className="mt-4 space-y-3">
              {comments.length === 0 && <div className="text-sm text-muted-foreground">No comments yet</div>}
              {comments.map((c) => (
                <div key={c.id} className="rounded-xl border border-border bg-background p-3">
                  <div className="flex justify-between">
                    <div>
                      <div className="font-medium">{c.author_name || `User ${c.author_id}`}</div>
                      <div className="text-xs text-muted-foreground">{new Date(c.created_at).toLocaleString()}</div>
                    </div>
                    <div className="flex items-center gap-2">
                      {me && (me.id === c.author_id || me.role === 'Admin') && (
                        <>
                          <button onClick={() => startEditComment(c)} className="text-sm text-primary">Edit</button>
                          <button onClick={() => deleteComment(c)} className="text-sm text-rose-500">Delete</button>
                        </>
                      )}
                    </div>
                  </div>
                  <div className="mt-2 text-sm">{editingComment === c.id ? (
                    <div>
                      <textarea className="w-full rounded-xl border border-border bg-background p-2" value={editingBody} onChange={(e) => setEditingBody(e.target.value)} />
                      <div className="flex gap-2 mt-2"><button onClick={saveEditComment} className="rounded-xl bg-primary px-3 py-2 text-sm">Save</button><button onClick={cancelEditComment} className="rounded-xl border border-border px-3 py-2 text-sm">Cancel</button></div>
                    </div>
                  ) : (
                    <div>{c.body}</div>
                  )}</div>
                </div>
              ))}
            </div>
          </section>

        </div>

        <aside className="space-y-6">
          <section className="rounded-xl border border-border bg-card p-6">
            <h3 className="text-lg font-semibold">Activity</h3>
            <div className="mt-3 space-y-3 max-h-96 overflow-y-auto">
              {activities.length === 0 && <div className="text-sm text-muted-foreground">No activity</div>}
              {activities.map((a) => (
                <div key={a.id} className="rounded-xl border border-border bg-background p-3">
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="text-sm"><strong>{a.actor_name || `User ${a.actor_id}`}</strong> <span className="text-muted-foreground">{a.action}</span></div>
                      {a.details && <div className="text-xs text-muted-foreground mt-1">{a.details}</div>}
                    </div>
                    <div className="text-xs text-muted-foreground">{new Date(a.created_at).toLocaleString()}</div>
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* Missing information warnings */}
          <section className="rounded-xl border border-border bg-card p-6">
            <h3 className="text-lg font-semibold">Missing Information</h3>
            <div className="mt-3 text-sm">
              {missingLoading && <p className="text-muted-foreground">Checking...</p>}
              {!missingLoading && missingInfo.length === 0 && <p className="text-emerald-500">No missing information detected.</p>}
              {!missingLoading && missingInfo.length > 0 && (
                <ul className="space-y-2">
                  {missingInfo.map((w) => (
                    <li key={w.field} className="rounded-xl border border-amber-500/40 bg-amber-500/10 p-2 text-amber-600">{w.message}</li>
                  ))}
                </ul>
              )}
            </div>
          </section>

          {/* AI Analysis */}
          <section className="rounded-xl border border-border bg-card p-6">
            <h3 className="text-lg font-semibold">AI Analysis</h3>
            <div className="mt-3 text-sm">
              <button onClick={runAnalysis} disabled={analysisLoading} className="rounded-xl bg-primary px-3 py-2 disabled:opacity-50">{analysisLoading ? 'Analyzing...' : 'Run AI Analysis'}</button>
              {analysisError && <p className="mt-2 text-rose-500">{analysisError}</p>}
              {analysis && (
                <div className="mt-3 space-y-2 rounded-xl border border-border bg-background p-3">
                  <div><strong>Category:</strong> {analysis.category}</div>
                  <div><strong>Severity:</strong> {analysis.severity}</div>
                  <div><strong>Priority:</strong> {analysis.priority}</div>
                  <div><strong>Root cause:</strong> {analysis.root_cause}</div>
                  <div><strong>Suggested fix:</strong> {analysis.resolution}</div>
                  <div><strong>Confidence:</strong> {analysis.confidence}</div>
                  <div className="pt-1 text-xs text-muted-foreground">AI-generated suggestion — verify before acting.</div>
                </div>
              )}
            </div>
          </section>

          {/* AI Recommendation */}
          <section className="rounded-xl border border-border bg-card p-6">
            <h3 className="text-lg font-semibold">AI Recommendation</h3>
            <div className="mt-3 text-sm">
              <button onClick={loadRecommendation} disabled={recLoading} className="rounded-xl border border-border px-3 py-2 disabled:opacity-50">{recLoading ? 'Loading...' : 'View AI Recommendation'}</button>
              {recError && <p className="mt-2 text-rose-500">{recError}</p>}
              {recommendation && (
                <div className="mt-3 space-y-2 rounded-xl border border-border bg-background p-3">
                  <div><strong>Category:</strong> {recommendation.category || '—'}</div>
                  <div><strong>Severity:</strong> {recommendation.severity || '—'}</div>
                  <div><strong>Priority:</strong> {recommendation.priority || '—'}</div>
                  <div><strong>Root cause:</strong> {recommendation.root_cause || '—'}</div>
                  <div><strong>Suggested resolution:</strong> {recommendation.suggested_resolution || '—'}</div>
                  <div><strong>Confidence:</strong> {recommendation.confidence_score}%</div>
                  {recommendation.reasoning && <div><strong>Reasoning:</strong> {recommendation.reasoning}</div>}
                  <div className="pt-1 text-xs text-muted-foreground">AI-generated suggestion — verify before acting.</div>
                </div>
              )}
            </div>
          </section>

          {/* AI Investigation / Debugging */}
          <section className="rounded-xl border border-border bg-card p-6">
            <h3 className="text-lg font-semibold">AI Debugging Assistant</h3>
            <div className="mt-3 text-sm">
              <button onClick={loadInvestigation} disabled={investigationLoading} className="rounded-xl border border-border px-3 py-2 disabled:opacity-50">{investigationLoading ? 'Investigating...' : 'Run AI Investigation'}</button>
              {investigationError && <p className="mt-2 text-rose-500">{investigationError}</p>}
              {investigation && (
                <div className="mt-3 space-y-3 rounded-xl border border-border bg-background p-3">
                  <div><strong>Category:</strong> {investigation.category}</div>
                  <div>
                    <strong>Possible root causes:</strong>
                    <ul className="mt-1 list-disc pl-4 space-y-1">{investigation.root_causes.map((r, i) => <li key={i}>{r}</li>)}</ul>
                  </div>
                  <div>
                    <strong>Debugging steps:</strong>
                    <ol className="mt-1 list-decimal pl-4 space-y-1">{investigation.debugging_steps.map((s, i) => <li key={i}>{s}</li>)}</ol>
                  </div>
                  <div>
                    <strong>Relevant modules:</strong>
                    <ul className="mt-1 list-disc pl-4 space-y-1">{investigation.modules.map((m, i) => <li key={i}>{m}</li>)}</ul>
                  </div>
                  <div><strong>Fix direction:</strong> {investigation.fix_direction}</div>
                  <div><strong>Recommended next action:</strong> {investigation.next_action}</div>
                  {investigation.similar_issues && investigation.similar_issues.length > 0 && (
                    <div>
                      <strong>Similar previous issues:</strong>
                      <ul className="mt-1 space-y-1">
                        {investigation.similar_issues.map((s) => (
                          <li key={s.id}><a className="text-primary" href={`/issues/${s.id}`}>{s.title}</a> <span className="text-muted-foreground">({s.similarity}%)</span></li>
                        ))}
                      </ul>
                    </div>
                  )}
                  <div className="pt-1 text-xs text-muted-foreground">{investigation.disclaimer}</div>
                </div>
              )}
            </div>
          </section>
        </aside>
      </div>
    </Layout>
  )
}