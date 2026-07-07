import { describe, expect, it } from 'vitest'
import { parseSseFrames } from './sse'

describe('parseSseFrames', () => {
  it('parses named events with multi-line data', () => {
    const frames = parseSseFrames(
      'event: run.progress\n' +
        'data: {"message":"first"}\n' +
        'data: {"message":"second"}\n\n',
    )

    expect(frames).toEqual([
      {
        event: 'run.progress',
        data: '{"message":"first"}\n{"message":"second"}',
      },
    ])
  })

  it('keeps structured error events explicit', () => {
    const frames = parseSseFrames(
      'event: error.structured\n' +
        'data: {"error":"ProviderFailure","detail":"provider unavailable"}\n\n',
    )

    expect(frames[0]).toEqual({
      event: 'error.structured',
      data: '{"error":"ProviderFailure","detail":"provider unavailable"}',
    })
  })
})
