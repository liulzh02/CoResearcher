import type {
  ArtifactResponse,
  EvidenceResponse,
  HealthResponse,
  MemoryCandidatesResponse,
  MemoryInspectResponse,
  MemoryResponse,
  ModelsResponse,
  RunEventsResponse,
  RegistryResponse,
  RunResearchResponse,
  ThreadListResponse,
  ThreadResponse,
} from './types'

type Fetcher = typeof fetch

type JsonBody = Record<string, unknown>

export class CoResearcherApi {
  private readonly baseUrl: string
  private readonly fetcher: Fetcher

  constructor(baseUrl: string, fetcher: Fetcher = fetch) {
    this.baseUrl = baseUrl.replace(/\/+$/, '')
    this.fetcher = fetcher
  }

  health(): Promise<HealthResponse> {
    return this.get('/health')
  }

  models(): Promise<ModelsResponse> {
    return this.get('/models')
  }

  tools(): Promise<RegistryResponse<'tools'>> {
    return this.get('/tools')
  }

  subagents(): Promise<RegistryResponse<'subagents'>> {
    return this.get('/subagents')
  }

  createThread(initialMessage: string, title?: string): Promise<ThreadResponse> {
    return this.post('/research/threads', {
      initial_message: initialMessage,
      title,
    })
  }

  listThreads(): Promise<ThreadListResponse> {
    return this.get('/research/threads')
  }

  getThread(threadId: string): Promise<ThreadResponse> {
    return this.get(`/research/threads/${encodeURIComponent(threadId)}`)
  }

  getMessages(threadId: string): Promise<{ messages: unknown[] }> {
    return this.get(`/research/threads/${encodeURIComponent(threadId)}/messages`)
  }

  getRunEvents(runId: string): Promise<RunEventsResponse> {
    return this.get(`/research/runs/${encodeURIComponent(runId)}/events`)
  }

  runResearch(threadId: string, message: string): Promise<RunResearchResponse> {
    return this.post(`/research/threads/${encodeURIComponent(threadId)}/runs`, { message })
  }

  getEvidence(threadId: string): Promise<EvidenceResponse> {
    return this.get(`/research/threads/${encodeURIComponent(threadId)}/evidence`)
  }

  getArtifact(threadId: string, artifactId: string): Promise<ArtifactResponse> {
    return this.get(
      `/research/threads/${encodeURIComponent(threadId)}/artifacts/${encodeURIComponent(artifactId)}`,
    )
  }

  getGlobalMemory(): Promise<MemoryResponse> {
    return this.get('/memory/global')
  }

  getResearchMemory(researchId: string): Promise<MemoryResponse> {
    return this.get(`/memory/research/${encodeURIComponent(researchId)}`)
  }

  getResearchCandidates(researchId: string): Promise<MemoryCandidatesResponse> {
    return this.get(`/memory/research/${encodeURIComponent(researchId)}/candidates`)
  }

  inspectMemory(researchId: string, query = ''): Promise<MemoryInspectResponse> {
    const params = new URLSearchParams({ query })
    return this.get(`/memory/research/${encodeURIComponent(researchId)}/inspect?${params}`)
  }

  streamUrl(threadId: string): string {
    return `${this.baseUrl}/research/threads/${encodeURIComponent(threadId)}/runs/stream`
  }

  private get<T>(path: string): Promise<T> {
    return this.request<T>('GET', path)
  }

  private post<T>(path: string, body: JsonBody): Promise<T> {
    return this.request<T>('POST', path, body)
  }

  private async request<T>(method: 'GET' | 'POST', path: string, body?: JsonBody): Promise<T> {
    const fetcher = this.fetcher
    const response = await fetcher(`${this.baseUrl}${path}`, {
      method: method === 'GET' ? undefined : method,
      headers: {
        accept: 'application/json',
        ...(body ? { 'content-type': 'application/json' } : {}),
      },
      ...(body ? { body: JSON.stringify(body) } : {}),
    })

    if (!response.ok) {
      throw new Error(`${method} ${path} failed: ${await readErrorDetail(response)}`)
    }

    return response.json() as Promise<T>
  }
}

export const DEFAULT_BACKEND_URL = import.meta.env.VITE_CORESEARCHER_API_URL || '/api'

async function readErrorDetail(response: Response): Promise<string> {
  try {
    const payload = (await response.json()) as { detail?: unknown; error?: unknown }
    if (typeof payload.detail === 'string') return payload.detail
    if (typeof payload.error === 'string') return payload.error
  } catch {
    // Fall back to status text below.
  }
  return response.statusText || `HTTP ${response.status}`
}
