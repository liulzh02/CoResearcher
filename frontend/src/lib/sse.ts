import type { ResearchEvent } from './types'

export type SseFrame = {
  event: string
  data: string
}

export type StreamCallbacks = {
  onFrame?: (frame: SseFrame) => void
  onEvent?: (event: ResearchEvent, frame: SseFrame) => void
  onError?: (error: Error) => void
}

export function parseSseFrames(input: string): SseFrame[] {
  const frames: SseFrame[] = []
  const chunks = input.replace(/\r\n/g, '\n').split('\n\n')

  for (const chunk of chunks) {
    if (!chunk.trim()) continue
    let event = 'message'
    const data: string[] = []

    for (const line of chunk.split('\n')) {
      if (line.startsWith('event:')) {
        event = line.slice('event:'.length).trim()
      } else if (line.startsWith('data:')) {
        data.push(line.slice('data:'.length).trimStart())
      }
    }

    frames.push({ event, data: data.join('\n') })
  }

  return frames
}

export async function streamResearchRun(
  url: string,
  message: string,
  callbacks: StreamCallbacks = {},
  fetcher: typeof fetch = fetch,
): Promise<void> {
  const response = await fetcher(url, {
    method: 'POST',
    headers: {
      accept: 'text/event-stream',
      'content-type': 'application/json',
    },
    body: JSON.stringify({ message }),
  })

  if (!response.ok) {
    callbacks.onError?.(new Error(`Stream request failed: ${response.status}`))
    return
  }

  if (!response.body) {
    callbacks.onError?.(new Error('Stream response did not include a body'))
    return
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  for (;;) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const boundary = buffer.lastIndexOf('\n\n')
    if (boundary === -1) continue

    const ready = buffer.slice(0, boundary + 2)
    buffer = buffer.slice(boundary + 2)
    emitFrames(ready, callbacks)
  }

  buffer += decoder.decode()
  emitFrames(buffer, callbacks)
}

function emitFrames(input: string, callbacks: StreamCallbacks): void {
  for (const frame of parseSseFrames(input)) {
    callbacks.onFrame?.(frame)
    try {
      const parsed = JSON.parse(frame.data) as Partial<ResearchEvent> & Record<string, unknown>
      const event =
        typeof parsed.type === 'string'
          ? (parsed as ResearchEvent)
          : ({
              id: `client_${Date.now()}`,
              type: frame.event,
              thread_id: '',
              run_id: '',
              payload: parsed,
              created_at: new Date().toISOString(),
              phase: frame.event === 'error.structured' ? 'error' : undefined,
              status: frame.event === 'error.structured' ? 'failed' : undefined,
              title: frame.event,
              message: typeof parsed.detail === 'string' ? parsed.detail : undefined,
            } satisfies ResearchEvent)
      callbacks.onEvent?.(event, frame)
    } catch (error) {
      callbacks.onError?.(error instanceof Error ? error : new Error(String(error)))
    }
  }
}
