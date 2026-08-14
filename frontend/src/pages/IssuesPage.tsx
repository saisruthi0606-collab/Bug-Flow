import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import Layout from '../components/Layout'
import { api } from '../lib/api'
import type { Issue, Project, Sprint, UserListItem } from '../lib/types'
const severityClass: Record<string,string> = { Critical:'bg-rose-500/15 text-rose-500', High:'bg-orange-500/15 text-orange-500', Medium:'bg-amber-500/15 text-amber-500', Low:'bg-sky-500/15 text-sky-500' }
export default function IssuesPage() {
  const [filters,setFilters]=useState({search:'',status:'',priority:'',severity:'',sprint_id:'',project_id:'',assigned_to:'',category:'',sort:'newest',semantic:false})
  const {data: sprints=[]}=useQuery<Sprint[]>({queryKey:['sprints'],queryFn:async()=> (await api.get('/api/sprints')).data})
  const {data: projects=[]}=useQuery<Project[]>({queryKey:['projects'],queryFn:async()=> (await api.get('/api/projects')).data})
  const {data: users=[]}=useQuery<UserListItem[]>({queryKey:['users'],queryFn:async()=> (await api.get('/api/users')).data})
  const {data:issues=[],isLoading,refetch}=useQuery<Issue[]>({queryKey:['issues',filters],queryFn:async()=> {
    // ensure we send only non-empty params to api
    const params: Record<string, any> = {}
    Object.entries(filters).forEach(([k,v]) => { if (v !== '' && v !== null && v !== undefined && v !== false) params[k] = v })
    const res = await api.get('/api/issues',{params})
    return res.data
  }})
  const update=(key:string,value:string|boolean)=>setFilters(x=>({...x,[key]:value}))
  return (
    <Layout title="Issues">
      <div className="rounded-3xl border border-border bg-card p-6 shadow-glow">
        <div className="flex flex-wrap gap-3">
          <input className="flex-1 rounded-xl border border-border bg-background px-3 py-2" placeholder="Search issues" value={filters.search} onChange={e=>update('search',e.target.value)}/>
          <label className="flex items-center gap-2 rounded-xl border border-border bg-background px-3 py-2 text-sm">
            <input type="checkbox" checked={filters.semantic} onChange={e=>update('semantic',e.target.checked)} />
            Semantic
          </label>
          {[['status',['Open','Assigned','In Progress','In Review','Resolved','Verified','Closed']],['severity',['Critical','High','Medium','Low']],['priority',['High','Medium','Low']],['sort',['newest','oldest','highest_severity','highest_priority']]].map(([key,values])=> (
            <select key={String(key)} className="rounded-xl border border-border bg-background px-3 py-2" value={(filters as any)[String(key)]} onChange={e=>update(String(key),e.target.value)}>
              <option value="">All {key}</option>
              {(values as string[]).map(v=> <option key={v} value={v}>{v.replace('_',' ')}</option>)}
            </select>
          ))}
          <select className="rounded-xl border border-border bg-background px-3 py-2" value={filters.sprint_id} onChange={e=>update('sprint_id',e.target.value)}>
            <option value="">All sprints</option>
            {sprints.map(s=> <option key={s.id} value={s.id}>{s.name}</option>)}
          </select>
          <select className="rounded-xl border border-border bg-background px-3 py-2" value={filters.project_id} onChange={e=>update('project_id',e.target.value)}>
            <option value="">All projects</option>
            {projects.map(p=> <option key={p.id} value={p.id}>{p.project_name}</option>)}
          </select>
          <select className="rounded-xl border border-border bg-background px-3 py-2" value={filters.assigned_to} onChange={e=>update('assigned_to',e.target.value)}>
            <option value="">All assignees</option>
            {users.filter(u=>u.role==='Developer').map(u=> <option key={u.id} value={u.id}>{u.full_name}</option>)}
          </select>
          <button onClick={()=>refetch()} className="rounded-xl bg-primary px-4 py-2 font-semibold text-foreground">Apply</button>
        </div>

        <div className="mt-5 space-y-3">
          {isLoading && <p>Loading issues...</p>}
          {!isLoading && issues.map(issue => (
            <div key={issue.id} className="rounded-xl border border-border bg-background p-4">
              <div className="flex justify-between items-start gap-4">
                <div>
                  <h3 className="font-semibold text-lg">{issue.title}</h3>
                  <p className="mt-1 text-sm text-muted-foreground">{issue.description || issue.category || 'Uncategorized'}</p>
                  <div className="mt-3 text-sm text-muted-foreground">
                    <span>Reporter: {issue.reporter_name ?? issue.reporter}</span>
                    <span className="mx-2">•</span>
                    <span>Assignee: {issue.assignee_name ?? 'Unassigned'}</span>
                    <span className="mx-2">•</span>
                    <span>Project: {issue.project_name}</span>
                    <span className="mx-2">•</span>
                    <span>Sprint: {issue.sprint_name ?? '—'}</span>
                  </div>
                </div>
                <div className="flex flex-col items-end gap-2">
                  <div className="flex gap-2">
                    <span className="rounded-full bg-primary/10 px-3 py-1 text-sm text-primary">{issue.status}</span>
                    <span className={`rounded-full px-3 py-1 text-sm ${severityClass[issue.severity]}`}>{issue.severity}</span>
                    <span className="rounded-full bg-accent/10 px-3 py-1 text-sm text-accent">{issue.priority}</span>
                  </div>
                  <div className="text-sm text-muted-foreground">
                    <div>AI Score: {issue.ai_score ?? '—'}</div>
                    <div>Attachments: {issue.attachment_count ?? 0} • Comments: {issue.comment_count ?? 0}</div>
                    <div className="mt-1">Created: {new Date(issue.created_at).toLocaleString()}</div>
                    <div>Updated: {new Date(issue.updated_at).toLocaleString()}</div>
                  </div>
                  <div className="mt-2 flex gap-2">
                    <a className="rounded-md bg-background px-3 py-1 text-sm" href={`/issues/${issue.id}`}>View</a>
                    <a className="rounded-md bg-background px-3 py-1 text-sm" href={`/issues/${issue.id}/edit`}>Edit</a>
                  </div>
                </div>
              </div>
            </div>
          ))}
          {!isLoading && !issues.length && <p className="text-muted-foreground">No issues found.</p>}
        </div>
      </div>
    </Layout>
  )
}