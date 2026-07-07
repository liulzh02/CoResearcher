import type { ResearchEvent, StructuredError } from './types'

export type RunTraceStep = {
  id: string
  type: string
  phase: string
  status: string
  title: string
  message: string
  sequence: number
  created_at: string
  duration_ms?: number | null
}

export type RunTraceMetrics = {
  runId: string | null
  startedAt: string | null
  firstTokenAt: string | null
  completedAt: string | null
  deltaCount: number
  modelName: string | null
  elapsedMs: number | null
}

export type RunViewState = {
  assistantDraft: string
  steps: RunTraceStep[]
  rawEvents: ResearchEvent[]
  metrics: RunTraceMetrics
  error: StructuredError | null
  status: 'idle' | 'running' | 'completed' | 'failed'
}

export function deriveRunView(events: ResearchEvent[]): RunViewState {
  let assistantDraft = ''
  let startedAt: string | null = null
  let firstTokenAt: string | null = null
  let completedAt: string | null = null
  let runId: string | null = null
  let modelName: string | null = null
  let deltaCount = 0
  let error: StructuredError | null = null
  const steps: RunTraceStep[] = []

  for (const event of events) {
    runId = event.run_id || runId
    if (event.type === 'run.started') startedAt = event.created_at
    if (event.type === 'model.first_token') firstTokenAt = event.created_at
    if (event.type === 'run.completed' || event.type === 'run.failed') completedAt = event.created_at

    const payloadModel = event.payload.model_name ?? event.payload.model
    if (typeof payloadModel === 'string') modelName = payloadModel

    if (isAssistantDelta(event)) {
      const content = event.payload.content
      if (typeof content === 'string') {
        assistantDraft += content
        deltaCount += 1
      }
      continue
    }

    if (event.type === 'error.structured' || event.type === 'run.failed') {
      error = {
        error: String(event.payload.error ?? event.title ?? 'RunError'),
        detail: String(event.payload.detail ?? event.message ?? 'The run failed.'),
      }
    }

    steps.push(toTraceStep(event))
  }

  const finalEvent = events.findLast((event) => event.type === 'final.response')
  if (!assistantDraft && typeof finalEvent?.payload.content === 'string') {
    assistantDraft = finalEvent.payload.content
  }

  return {
    assistantDraft,
    steps,
    rawEvents: events,
    metrics: {
      runId,
      startedAt,
      firstTokenAt,
      completedAt,
      deltaCount,
      modelName,
      elapsedMs: elapsedMs(startedAt, completedAt),
    },
    error,
    status: resolveStatus(events),
  }
}

function isAssistantDelta(event: ResearchEvent): boolean {
  return event.type === 'final.response.delta' || event.payload.is_assistant_delta === true
}

function toTraceStep(event: ResearchEvent): RunTraceStep {
  return {
    id: event.id,
    type: event.type,
    phase: event.phase || fallbackPhase(event.type),
    status: event.status || fallbackStatus(event.type),
    title: event.title || fallbackTitle(event.type),
    message: event.message || fallbackMessage(event),
    sequence: event.sequence ?? 0,
    created_at: event.created_at,
    duration_ms: event.duration_ms,
  }
}

function resolveStatus(events: ResearchEvent[]): RunViewState['status'] {
  if (events.some((event) => event.type === 'run.failed' || event.type === 'error.structured')) {
    return 'failed'
  }
  if (events.some((event) => event.type === 'run.completed')) return 'completed'
  if (events.length > 0) return 'running'
  return 'idle'
}

function fallbackPhase(type: string): string {
  if (type.startsWith('final.')) return 'assistant'
  return type.split('.')[0] || 'run'
}

function fallbackStatus(type: string): string {
  if (type.endsWith('.started') || type.endsWith('.progress') || type.endsWith('.delta')) return 'running'
  if (type.endsWith('.failed') || type === 'error.structured') return 'failed'
  return 'completed'
}

function fallbackTitle(type: string): string {
  return type
    .split('.')
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ')
}

function fallbackMessage(event: ResearchEvent): string {
  for (const key of ['message', 'detail', 'summary', 'result_summary', 'final_response']) {
    const value = event.payload[key]
    if (typeof value === 'string') return value
  }
  if (event.type === 'final.response') return 'Assistant response is complete.'
  return fallbackTitle(event.type)
}

function elapsedMs(startedAt: string | null, completedAt: string | null): number | null {
  if (!startedAt || !completedAt) return null
  const elapsed = Date.parse(completedAt) - Date.parse(startedAt)
  return Number.isFinite(elapsed) ? elapsed : null
}
