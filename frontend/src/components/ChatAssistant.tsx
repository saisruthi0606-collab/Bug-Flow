import { useEffect, useRef, useState, type FormEvent } from 'react'
import { Bot, Plus, Send, ThumbsDown, ThumbsUp, X } from 'lucide-react'
import { Link } from 'react-router-dom'
import { api } from '../lib/api'

type Source = { issue_id: number; title: string; similarity?: number }
type Reply = { id: number; answer: string; sources: Source[] }
type ChatMessage = { id: string | number; role: 'user' | 'assistant'; content: string; sources?: Source[] }

const initialGreeting: ChatMessage = {
  id: 'initial-greeting',
  role: 'assistant',
  content: 'Hello! How can I help you today?',
}

export default function ChatAssistant() {
  const [open, setOpen] = useState(false)
  const [message, setMessage] = useState('')
  const [reply, setReply] = useState<Reply | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [feedback, setFeedback] = useState('')
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const historyRequestId = useRef(0)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const activeConversationId = useRef(localStorage.getItem('bugflow_active_chat_conversation'))

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
    const chatMessages = document.querySelector<HTMLElement>('.max-h-80')
    if (chatMessages) chatMessages.scrollTop = chatMessages.scrollHeight
  }, [messages, open])

  useEffect(() => {
    const requestId = historyRequestId.current
    const params = activeConversationId.current ? { conversation_id: activeConversationId.current } : undefined
    api.get<Array<{ id: number; message: string; response: string }>>('/api/chat/history', { params })
      .then(response => {
        const historyMessages = response.data.slice().reverse().flatMap(item => [
          { id: `${item.id}-user`, role: 'user' as const, content: item.message },
          { id: `${item.id}-assistant`, role: 'assistant' as const, content: item.response },
        ])
        if (historyRequestId.current === requestId) {
          setMessages(current => current.length > 0
            ? [...historyMessages, ...current]
            : (historyMessages.length ? historyMessages : [initialGreeting]))
        }
      })
      .catch(() => {
        if (historyRequestId.current === requestId) setMessages([initialGreeting])
      })
  }, [])

  const ask = async (event: FormEvent) => {
    event.preventDefault()
    const submittedMessage = message.trim()
    if (!submittedMessage) return
    const conversationId = historyRequestId.current
    const activeId = activeConversationId.current
    setMessages(current => [...current, { id: `pending-${Date.now()}`, role: 'user', content: submittedMessage }])
    setMessage('')
    setLoading(true); setError(''); setFeedback('')
    try {
      const response = await api.post<Reply>('/api/chat/ask', { message: submittedMessage, conversation_id: activeId })
      if (historyRequestId.current === conversationId && activeConversationId.current === activeId) {
        setReply(response.data)
        setMessages(current => [...current, { id: response.data.id, role: 'assistant', content: response.data.answer, sources: response.data.sources }])
      }
    } catch (requestError: any) {
      const detail = requestError?.response?.data?.detail
      setError(typeof detail === 'string' ? detail : 'AI service is temporarily unavailable. Please try again.')
    } finally { setLoading(false) }
  }

  const startNewChat = () => {
    historyRequestId.current += 1
    const newConversationId = crypto.randomUUID()
    activeConversationId.current = newConversationId
    localStorage.setItem('bugflow_active_chat_conversation', newConversationId)
    setOpen(true)
    setMessages(() => [initialGreeting])
    setMessage('')
    setReply(null)
    setLoading(false)
    setError('')
    setFeedback('')
  }

  const sendFeedback = async (feedback_type: 'helpful' | 'not_helpful') => {
    if (!reply) return
    try {
      await api.post('/api/ai/feedback', { feedback_type, source: 'chat', message_ref: String(reply.id) })
      setFeedback('Thanks for your feedback.')
    } catch { setFeedback('Unable to save feedback.') }
  }

  return (
    <div className="fixed bottom-4 left-4 z-50">
      {open && <section className="mb-3 w-[min(24rem,calc(100vw-2rem))] rounded-3xl border border-border bg-card p-4 shadow-glow">
        <div className="flex items-center justify-between"><div className="flex items-center gap-2 font-semibold"><Bot size={18} className="text-primary" /> BugFlow Assistant</div><div className="flex items-center gap-2"><button type="button" onClick={startNewChat} className="flex items-center gap-1 text-xs font-medium text-primary hover:underline"><Plus size={14} /> New Chat</button><button aria-label="Close assistant" onClick={() => setOpen(false)} className="text-muted-foreground"><X size={18} /></button></div></div>
        <p className="mt-2 text-xs text-muted-foreground">Ask about issues, previous resolutions, risk, or project trends.</p>
        {messages.length > 0 && <div className="mt-3 max-h-80 space-y-3 overflow-y-auto">{messages.map(item => <div key={item.id} className={`rounded-xl border border-border p-3 text-sm whitespace-pre-wrap ${item.role === 'user' ? 'ml-6 bg-primary/10' : 'mr-6 bg-background'}`}><p className="mb-1 text-xs font-medium text-muted-foreground">{item.role === 'user' ? 'You' : 'Assistant'}</p>{item.content}{item.role === 'assistant' && item.sources && item.sources.length > 0 && <div className="mt-3 border-t border-border pt-2"><p className="text-xs font-medium text-muted-foreground">Sources</p>{item.sources.map(source => <Link key={source.issue_id} to={`/issues/${source.issue_id}`} className="mt-1 block text-xs text-primary hover:underline">BUG-{source.issue_id} — {source.title}</Link>)}</div>}</div>)}</div>}
        {reply && <div className="mt-3 flex items-center gap-2"><button onClick={() => sendFeedback('helpful')} className="rounded-lg border border-border p-1.5" aria-label="Helpful"><ThumbsUp size={14} /></button><button onClick={() => sendFeedback('not_helpful')} className="rounded-lg border border-border p-1.5" aria-label="Not helpful"><ThumbsDown size={14} /></button><span className="text-xs text-muted-foreground">{feedback}</span></div>}
        {error && <p className="mt-3 text-sm text-rose-400">{error}</p>}
        <form onSubmit={ask} className="mt-3 flex gap-2"><input value={message} onChange={event => setMessage(event.target.value)} maxLength={4000} placeholder="Ask BugFlow AIâ€¦" className="min-w-0 flex-1 rounded-xl border border-border bg-background px-3 py-2 text-sm" /><button disabled={loading} className="rounded-xl bg-primary px-3 disabled:opacity-60" aria-label="Ask assistant"><Send size={16} /></button></form>
         <div ref={messagesEndRef} />
       </section>}
      <button onClick={() => setOpen(!open)} className="flex h-12 w-12 items-center justify-center rounded-full bg-primary text-foreground shadow-glow" aria-label="Open BugFlow assistant"><Bot size={22} /></button>
    </div>
  )
}
