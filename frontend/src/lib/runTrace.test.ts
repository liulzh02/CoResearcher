import { describe, expect, it } from 'vitest'
import { deriveRunView } from './runTrace'
import type { ResearchEvent } from './types'

const baseEvent = {
  id: 'evt_1',
  thread_id: 'thread_1',
  run_id: 'run_1',
  created_at: '2026-07-07T09:00:00.000Z',
  payload: {},
} satisfies Omit<ResearchEvent, 'type'>

describe('deriveRunView', () => {
  it('separates assistant deltas from trace steps', () => {
    const view = deriveRunView([
      {
        ...baseEvent,
        type: 'run.started',
        phase: 'run',
        status: 'running',
        title: 'Run started',
      },
      {
        ...baseEvent,
        id: 'evt_2',
        type: 'final.response.delta',
        phase: 'assistant',
        status: 'running',
        payload: { content: 'Hel', is_assistant_delta: true },
      },
      {
        ...baseEvent,
        id: 'evt_3',
        type: 'final.response.delta',
        phase: 'assistant',
        status: 'running',
        payload: { content: 'lo', is_assistant_delta: true },
      },
      {
        ...baseEvent,
        id: 'evt_4',
        type: 'run.completed',
        phase: 'run',
        status: 'completed',
        title: 'Run completed',
      },
    ])

    expect(view.assistantDraft).toBe('Hello')
    expect(view.steps.map((step) => step.type)).toEqual(['run.started', 'run.completed'])
    expect(view.metrics.deltaCount).toBe(2)
    expect(view.status).toBe('completed')
    expect(view.rawEvents).toHaveLength(4)
  })

  it('maps enriched event metadata into readable steps', () => {
    const view = deriveRunView([
      {
        ...baseEvent,
        type: 'model.selected',
        phase: 'model',
        status: 'completed',
        title: 'Model selected',
        message: 'DeepSeek is ready.',
        sequence: 3,
        payload: { model_name: 'deepseek-v4-pro' },
      },
    ])

    expect(view.steps[0]).toMatchObject({
      phase: 'model',
      status: 'completed',
      title: 'Model selected',
      message: 'DeepSeek is ready.',
      sequence: 3,
    })
    expect(view.metrics.modelName).toBe('deepseek-v4-pro')
  })

  it('captures failed run errors while retaining raw events', () => {
    const view = deriveRunView([
      {
        ...baseEvent,
        type: 'run.failed',
        phase: 'run',
        status: 'failed',
        title: 'Run failed',
        message: 'Provider unavailable.',
        payload: { error: 'ProviderFailure', detail: 'Provider unavailable.' },
      },
    ])

    expect(view.status).toBe('failed')
    expect(view.error).toEqual({
      error: 'ProviderFailure',
      detail: 'Provider unavailable.',
    })
    expect(view.rawEvents[0].type).toBe('run.failed')
  })
})
