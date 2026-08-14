import { useState } from 'react'
import { Bell, Bot, CheckCheck, CircleAlert, MessageSquare, TicketCheck, Trash } from 'lucide-react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useTranslation } from 'react-i18next'
import { api } from '../lib/api'

type Notification = { id:number; kind:string; title:string; message:string; is_read:boolean; created_at:string }
const icons: Record<string, any> = { 'Issue Resolved': TicketCheck, 'Comment Added': MessageSquare, 'Critical Bug Created': CircleAlert, 'AI Recommendation Generated': Bot }

export default function NotificationCenter(){
  const [open,setOpen]=useState(false)
  const { t } = useTranslation()
  const client = useQueryClient()
  const { data = { items: [], unread_count: 0 } } = useQuery<{ items: Notification[]; unread_count: number }>({
    queryKey: ['notifications'],
    queryFn: async () => (await api.get('/api/notifications')).data,
    refetchInterval: 30000,
  })

  const mark = async (id: number) => { await api.put(`/api/notifications/${id}/read`); client.invalidateQueries({ queryKey: ['notifications'] }) }
  const markAll = async () => { await api.put('/api/notifications/read-all'); client.invalidateQueries({ queryKey: ['notifications'] }) }
  const del = async (id: number) => { if (!confirm('Delete notification?')) return; await api.delete(`/api/notifications/${id}`); client.invalidateQueries({ queryKey: ['notifications'] }) }

  return (
    <div className="relative">
      <button aria-label={t('notifications')} onClick={() => setOpen(v => !v)} className="relative rounded-2xl border border-border bg-background p-2 text-foreground hover:bg-border/10">
        <Bell size={18} />
        {data.unread_count > 0 && <span className="absolute -right-1 -top-1 flex h-4 min-w-4 items-center justify-center rounded-full bg-rose-500 px-1 text-[10px] font-bold text-white">{data.unread_count>99?'99+':data.unread_count}</span>}
      </button>

      {open && (
        <div className="absolute right-0 z-50 mt-3 w-80 overflow-hidden rounded-2xl border border-border bg-card shadow-glow">
          <div className="flex items-center justify-between border-b border-border px-4 py-3">
            <p className="font-semibold">{t('notifications')}</p>
            <div className="flex items-center gap-2">
              <button onClick={markAll} className="inline-flex items-center gap-1 text-xs text-primary"><CheckCheck size={14} />{t('mark_all_read')}</button>
            </div>
          </div>

          <div className="max-h-96 overflow-y-auto">
            {data.items.length === 0 && <div className="p-4 text-sm text-muted-foreground">No notifications</div>}
            {data.items.map(item => {
              const Icon = icons[item.kind] || Bell
              return (
                <div key={item.id} className={`flex w-full gap-3 border-b border-border px-4 py-3 ${item.is_read ? 'opacity-65' : ''}`}>
                  <Icon className="mt-0.5 shrink-0 text-accent" size={17} />
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="block text-sm font-medium">{item.title}</div>
                        <div className="mt-1 block text-xs text-muted-foreground">{item.message}</div>
                      </div>
                      <div className="flex items-center gap-2">
                        {!item.is_read && <button onClick={() => mark(item.id)} className="text-xs text-primary">Mark</button>}
                        <button onClick={() => del(item.id)} className="text-xs text-rose-500"><Trash size={14} /></button>
                      </div>
                    </div>
                    <div className="mt-2 text-xs text-muted-foreground">{new Date(item.created_at).toLocaleString()}</div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}
