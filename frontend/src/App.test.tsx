// @vitest-environment jsdom

import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import App from './App'

const thread = {
  id: 'thread_1',
  user_id: 'local-user',
  title: null,
  messages: [
    {
      id: 'msg_1',
      role: 'user',
      content: 'Observable trace test',
      created_at: '2026-07-07T09:00:00.000Z',
    },
  ],
  state: {
    evidence_items: [],
    claims: [],
    artifacts: [],
  },
  created_at: '2026-07-07T09:00:00.000Z',
  updated_at: '2026-07-07T09:00:00.000Z',
}

const completedThread = {
  ...thread,
  messages: [
    ...thread.messages,
    {
      id: 'msg_2',
      role: 'assistant',
      content: 'OK',
      created_at: '2026-07-07T09:00:02.000Z',
    },
  ],
}

const runEvents = [
  event('evt_1', 'run.started', 'run', 'running', 'Run started', { message: 'go' }),
  event('evt_2', 'model.selected', 'model', 'completed', 'Model selected', {
    model_name: 'deepseek-v4-pro',
  }),
  event('evt_3', 'final.response.delta', 'assistant', 'running', 'Assistant response delta', {
    content: 'OK',
    is_assistant_delta: true,
  }),
  event('evt_4', 'run.completed', 'run', 'completed', 'Run completed', {
    final_response: 'OK',
  }),
]

describe('App run trace', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn(handleFetch))
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('renders streamed assistant output, readable trace, and raw debug events', async () => {
    render(<App />)

    await screen.findByText('Model ready')
    await userEvent.type(screen.getByPlaceholderText('Frame a research question...'), 'Observable trace test')
    await userEvent.click(screen.getByRole('button', { name: 'Create' }))
    await screen.findByText('thread_1')

    await userEvent.type(screen.getByPlaceholderText('Ask the research director to continue...'), 'go')
    await userEvent.click(screen.getByRole('button', { name: 'Run' }))

    await waitFor(() => expect(screen.getAllByText('Model selected').length).toBeGreaterThan(0))
    await waitFor(() => expect(document.body.textContent).toContain('deepseek-v4-pro'))
    await screen.findByText('OK')

    await userEvent.click(screen.getByRole('button', { name: 'raw' }))
    await waitFor(() => expect(screen.getByText(/final.response.delta/)).toBeTruthy())
  })
})

function event(
  id: string,
  type: string,
  phase: string,
  status: string,
  title: string,
  payload: Record<string, unknown>,
) {
  return {
    id,
    type,
    thread_id: 'thread_1',
    run_id: 'run_1',
    payload,
    created_at: '2026-07-07T09:00:00.000Z',
    phase,
    status,
    title,
    message: title,
    sequence: Number(id.split('_')[1]),
  }
}

function sseResponse(events: typeof runEvents): Response {
  const encoder = new TextEncoder()
  const body = events
    .map((item) => `event: ${item.type}\ndata: ${JSON.stringify(item)}\n\n`)
    .join('')
  return new Response(
    new ReadableStream({
      start(controller) {
        controller.enqueue(encoder.encode(body))
        controller.close()
      },
    }),
    {
      status: 200,
      headers: { 'content-type': 'text/event-stream' },
    },
  )
}

async function handleFetch(input: RequestInfo | URL, init?: RequestInit): Promise<Response> {
  const url = String(input)
  const method = init?.method ?? 'GET'

  if (url.endsWith('/health')) return json({ status: 'ok', version: '0.1.0' })
  if (url.endsWith('/models')) {
    return json({
      default_model: 'deepseek',
      role_overrides: {},
      models: [{ id: 'deepseek', name: 'deepseek-v4-pro', ready: true, missing_secret_env_vars: [] }],
    })
  }
  if (url.endsWith('/tools')) return json({ tools: [] })
  if (url.endsWith('/subagents')) return json({ subagents: [] })
  if (url.endsWith('/research/threads') && method === 'POST') return json({ thread })
  if (url.endsWith('/research/threads') && method === 'GET') return json({ threads: [] })
  if (url.endsWith('/research/threads/thread_1')) return json({ thread: completedThread })
  if (url.endsWith('/research/threads/thread_1/runs/stream')) return sseResponse(runEvents)
  if (url.endsWith('/research/runs/run_1/events')) return json({ events: runEvents })

  return json({}, 404)
}

function json(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'content-type': 'application/json' },
  })
}
