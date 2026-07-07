import { describe, expect, it, vi } from 'vitest'
import { CoResearcherApi } from './api'

describe('CoResearcherApi', () => {
  it('normalizes the backend base URL and reads health', async () => {
    const fetcher = vi.fn(async () =>
      new Response(JSON.stringify({ status: 'ok', version: '0.1.0' }), {
        status: 200,
        headers: { 'content-type': 'application/json' },
      }),
    )
    const api = new CoResearcherApi('http://localhost:8000/', fetcher)

    await expect(api.health()).resolves.toEqual({ status: 'ok', version: '0.1.0' })
    expect(fetcher).toHaveBeenCalledWith('http://localhost:8000/health', {
      headers: { accept: 'application/json' },
    })
  })

  it('does not call fetch with the API instance as this', async () => {
    const fetcher = vi.fn(function (this: unknown) {
      if (this) {
        throw new TypeError('Illegal invocation')
      }
      return Promise.resolve(
        new Response(JSON.stringify({ status: 'ok', version: '0.1.0' }), {
          status: 200,
          headers: { 'content-type': 'application/json' },
        }),
      )
    })
    const api = new CoResearcherApi('http://localhost:8000', fetcher)

    await expect(api.health()).resolves.toEqual({ status: 'ok', version: '0.1.0' })
  })

  it('throws readable errors for failed backend requests', async () => {
    const fetcher = vi.fn(async () =>
      new Response(JSON.stringify({ detail: 'Research thread not found' }), {
        status: 404,
        headers: { 'content-type': 'application/json' },
      }),
    )
    const api = new CoResearcherApi('http://localhost:8000', fetcher)

    await expect(api.getThread('missing')).rejects.toThrow(
      'GET /research/threads/missing failed: Research thread not found',
    )
  })
})
