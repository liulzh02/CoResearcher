export type HealthResponse = {
  status: string
  version: string
}

export type ApiRecord = Record<string, unknown>

export type ChatMessage = {
  id: string
  role: string
  content: string
  created_at: string
}

export type ResearchState = {
  question?: ApiRecord
  scope?: ApiRecord
  hypotheses?: ApiRecord[]
  papers?: ApiRecord[]
  evidence_items?: ApiRecord[]
  claims?: ApiRecord[]
  open_questions?: ApiRecord[]
  decisions?: ApiRecord[]
  critique_notes?: ApiRecord[]
  artifacts?: ApiRecord[]
  todos?: ApiRecord[]
  knowledge_base_links?: Record<string, string[]>
  updated_at?: string
}

export type ResearchThread = {
  id: string
  user_id: string
  title: string | null
  messages: ChatMessage[]
  state: ResearchState
  created_at: string
  updated_at: string
}

export type ThreadResponse = {
  thread: ResearchThread
}

export type ThreadListResponse = {
  threads: ResearchThread[]
}

export type RunResearchResponse = {
  thread: ResearchThread
  run_id: string | null
  final_response: string | null
}

export type RegistryResponse<TName extends string> = Record<TName, ApiRecord[]>

export type ModelStatus = ApiRecord & {
  id?: string
  name: string
  display_name?: string | null
  ready: boolean
  missing_secret_env_vars: string[]
}

export type ModelsResponse = {
  default_model: string
  role_overrides: Record<string, string>
  models: ModelStatus[]
}

export type EvidenceResponse = {
  evidence_items: ApiRecord[]
  claims: ApiRecord[]
}

export type ArtifactResponse = {
  content: string
}

export type MemoryResponse = {
  memory: unknown
}

export type MemoryCandidatesResponse = {
  candidates: ApiRecord[]
}

export type MemoryInspectResponse = Record<string, unknown>

export type StructuredError = {
  error: string
  detail: string
}

export type ResearchEvent = {
  id: string
  type: string
  thread_id: string
  run_id: string
  payload: Record<string, unknown>
  created_at: string
  phase?: string | null
  level?: string
  status?: string | null
  title?: string | null
  message?: string | null
  parent_id?: string | null
  sequence?: number | null
  duration_ms?: number | null
}

export type RunEventsResponse = {
  events: ResearchEvent[]
}
