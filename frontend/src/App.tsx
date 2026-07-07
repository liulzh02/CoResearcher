import { useCallback, useEffect, useMemo, useState } from 'react'
import './App.css'
import { CoResearcherApi, DEFAULT_BACKEND_URL } from './lib/api'
import { getRuntimeStatus } from './lib/runtime'
import { streamResearchRun, type SseFrame } from './lib/sse'
import type { ApiRecord, HealthResponse, ModelsResponse, ResearchThread } from './lib/types'

function App() {
  const api = useMemo(() => new CoResearcherApi(DEFAULT_BACKEND_URL), [])
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [healthError, setHealthError] = useState('')
  const [threads, setThreads] = useState<ResearchThread[]>([])
  const [selectedThread, setSelectedThread] = useState<ResearchThread | null>(null)
  const [question, setQuestion] = useState('')
  const [message, setMessage] = useState('')
  const [streaming, setStreaming] = useState(false)
  const [streamingResponse, setStreamingResponse] = useState('')
  const [events, setEvents] = useState<SseFrame[]>([])
  const [panel, setPanel] = useState<'state' | 'evidence' | 'artifacts' | 'registries' | 'memory'>(
    'state',
  )
  const [panelData, setPanelData] = useState<unknown>(null)
  const [panelError, setPanelError] = useState('')
  const [modelsResponse, setModelsResponse] = useState<ModelsResponse>({
    default_model: 'fake',
    role_overrides: {},
    models: [{ name: 'fake', ready: true, missing_secret_env_vars: [] }],
  })
  const [registries, setRegistries] = useState<Record<string, ApiRecord[]>>({})

  const refreshHealth = useCallback(async () => {
    setHealthError('')
    try {
      setHealth(await api.health())
    } catch (error) {
      setHealth(null)
      setHealthError(error instanceof Error ? error.message : String(error))
    }
  }, [api])

  const refreshThreads = useCallback(async () => {
    const response = await api.listThreads()
    setThreads(response.threads)
    setSelectedThread((current) => current ?? response.threads[0] ?? null)
  }, [api])

  const refreshRegistries = useCallback(async () => {
    const [models, tools, subagents] = await Promise.allSettled([
      api.models(),
      api.tools(),
      api.subagents(),
    ])
    const modelPayload =
      models.status === 'fulfilled'
        ? models.value
        : { default_model: 'fake', role_overrides: {}, models: [] }
    setModelsResponse(modelPayload)
    setRegistries({
      models: modelPayload.models,
      tools: tools.status === 'fulfilled' ? tools.value.tools : [],
      subagents: subagents.status === 'fulfilled' ? subagents.value.subagents : [],
    })
  }, [api])

  const loadPanel = useCallback(
    async (nextPanel: typeof panel, thread: ResearchThread) => {
      setPanelError('')
      try {
        if (nextPanel === 'state') setPanelData(thread.state)
        if (nextPanel === 'evidence') setPanelData(await api.getEvidence(thread.id))
        if (nextPanel === 'artifacts') setPanelData(thread.state.artifacts ?? [])
        if (nextPanel === 'registries') setPanelData(registries)
        if (nextPanel === 'memory') {
          const [globalMemory, researchMemory, candidates] = await Promise.allSettled([
            api.getGlobalMemory(),
            api.getResearchMemory(thread.id),
            api.getResearchCandidates(thread.id),
          ])
          setPanelData({
            global: globalMemory.status === 'fulfilled' ? globalMemory.value : null,
            research: researchMemory.status === 'fulfilled' ? researchMemory.value : null,
            candidates: candidates.status === 'fulfilled' ? candidates.value : null,
          })
        }
      } catch (error) {
        setPanelError(error instanceof Error ? error.message : String(error))
        setPanelData(null)
      }
    },
    [api, registries],
  )

  useEffect(() => {
    void refreshHealth()
    void refreshThreads()
    void refreshRegistries()
  }, [refreshHealth, refreshRegistries, refreshThreads])

  useEffect(() => {
    if (!selectedThread) return
    void loadPanel(panel, selectedThread)
  }, [loadPanel, panel, selectedThread])

  async function createThread() {
    if (!question.trim()) return
    const response = await api.createThread(question.trim())
    setThreads((items) => [response.thread, ...items.filter((item) => item.id !== response.thread.id)])
    setSelectedThread(response.thread)
    setQuestion('')
    setEvents([])
  }

  async function selectThread(threadId: string) {
    const response = await api.getThread(threadId)
    setSelectedThread(response.thread)
    setEvents([])
  }

  async function runSelectedThread() {
    if (!selectedThread || !message.trim()) return
    const nextMessage = message.trim()
    setMessage('')
    setStreaming(true)
    setStreamingResponse('')
    setEvents([])
    await streamResearchRun(api.streamUrl(selectedThread.id), nextMessage, {
      onFrame: (frame) => setEvents((items) => [...items, frame]),
      onEvent: (event) => {
        if (event.type === 'final.response.delta') {
          const content = event.payload.content
          if (typeof content === 'string') {
            setStreamingResponse((current) => current + content)
          }
        }
        if (event.type === 'final.response' || event.type === 'run.completed') {
          void selectThread(selectedThread.id)
        }
      },
      onError: (error) =>
        setEvents((items) => [...items, { event: 'client.error', data: error.message }]),
    })
    setStreaming(false)
    setStreamingResponse('')
    await selectThread(selectedThread.id)
  }

  const messageCount = selectedThread?.messages.length ?? 0
  const evidenceCount = selectedThread?.state.evidence_items?.length ?? 0
  const artifactCount = selectedThread?.state.artifacts?.length ?? 0
  const runtime = getRuntimeStatus(modelsResponse)

  return (
    <main className="workbench">
      <aside className="sidebar">
        <div className="brand">
          <span className="mark">CR</span>
          <div>
            <h1>CoResearcher</h1>
            <p>Research workbench</p>
          </div>
        </div>

        <div className={`status ${health ? 'ok' : 'bad'}`}>
          <span></span>
          <strong>{health ? `Backend ${health.version}` : 'Backend offline'}</strong>
          <button type="button" onClick={() => void refreshHealth()}>
            Retry
          </button>
        </div>
        {healthError ? <p className="inline-error">{healthError}</p> : null}

        <div className={`runtime ${runtime.configured ? 'ready' : 'blocked'}`}>
          <strong>{runtime.label}</strong>
          <p>{runtime.detail}</p>
        </div>

        <section className="composer">
          <label htmlFor="question">New thread</label>
          <textarea
            id="question"
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Frame a research question..."
          />
          <button type="button" onClick={() => void createThread()}>
            Create
          </button>
        </section>

        <section className="thread-list" aria-label="Research threads">
          {threads.length === 0 ? (
            <p className="empty">No threads yet.</p>
          ) : (
            threads.map((thread) => (
              <button
                type="button"
                className={thread.id === selectedThread?.id ? 'selected' : ''}
                key={thread.id}
                onClick={() => void selectThread(thread.id)}
              >
                <strong>{thread.title || thread.id}</strong>
                <span>{thread.messages.length} messages</span>
              </button>
            ))
          )}
        </section>
      </aside>

      <section className="runway">
        <header>
          <div>
            <p className="eyebrow">Selected thread</p>
            <h2>{selectedThread?.title || 'Create a thread to begin'}</h2>
          </div>
          <div className="stats">
            <span>{messageCount} messages</span>
            <span>{evidenceCount} evidence</span>
            <span>{artifactCount} artifacts</span>
          </div>
        </header>

        <div className="timeline">
          {!selectedThread ? <p className="empty">The workbench is ready for the first thread.</p> : null}
          {selectedThread?.messages.map((item) => (
            <article className={`message ${item.role}`} key={item.id}>
              <span>{item.role}</span>
              <p>{item.content}</p>
            </article>
          ))}
          {streamingResponse ? (
            <article className="message assistant">
              <span>assistant</span>
              <p>{streamingResponse}</p>
            </article>
          ) : null}
          {events.map((event, index) => (
            <article className="event" key={`${event.event}-${index}`}>
              <span>{event.event}</span>
              <pre>{event.data}</pre>
            </article>
          ))}
        </div>

        <footer className="run-composer">
          <textarea
            value={message}
            disabled={!selectedThread || streaming || !runtime.configured}
            onChange={(event) => setMessage(event.target.value)}
            placeholder={
              runtime.configured
                ? 'Ask the research director to continue...'
                : 'Configure a real model provider and API key before launching research.'
            }
          />
          <button
            type="button"
            disabled={!selectedThread || !message.trim() || streaming || !runtime.configured}
            onClick={() => void runSelectedThread()}
          >
            {streaming ? 'Running' : 'Run'}
          </button>
        </footer>
      </section>

      <aside className="inspector">
        <nav aria-label="Inspection panels">
          {(['state', 'evidence', 'artifacts', 'registries', 'memory'] as const).map((item) => (
            <button
              type="button"
              className={panel === item ? 'selected' : ''}
              key={item}
              onClick={() => setPanel(item)}
            >
              {item}
            </button>
          ))}
        </nav>
        {panelError ? <p className="inline-error">{panelError}</p> : null}
        <pre className="panel">{formatPanel(panelData)}</pre>
      </aside>
    </main>
  )
}

function formatPanel(value: unknown): string {
  if (value === null || value === undefined) return 'No data yet.'
  return JSON.stringify(value, null, 2)
}

export default App
