import { describe, expect, it } from 'vitest'
import { getRuntimeStatus } from './runtime'

describe('getRuntimeStatus', () => {
  it('blocks research runs when the backend reports the default model is not ready', () => {
    expect(
      getRuntimeStatus({
        default_model: 'researcher',
        role_overrides: {},
        models: [
          {
            name: 'researcher',
            display_name: 'Researcher model',
            ready: false,
            missing_secret_env_vars: ['OPENAI_API_KEY'],
          },
        ],
      }),
    ).toEqual({
      configured: false,
      label: 'Model not configured',
      detail: 'Default model researcher is missing: OPENAI_API_KEY.',
    })
  })

  it('allows research runs when the backend reports the default model is ready', () => {
    expect(
      getRuntimeStatus({
        default_model: 'researcher',
        role_overrides: {},
        models: [
          {
            name: 'researcher',
            display_name: 'Researcher model',
            ready: true,
            missing_secret_env_vars: [],
          },
        ],
      }),
    ).toEqual({
      configured: true,
      label: 'Model ready',
      detail: 'Default model researcher is ready.',
    })
  })

  it('matches the backend default model by config id when provider model name differs', () => {
    expect(
      getRuntimeStatus({
        default_model: 'deepseek',
        role_overrides: {},
        models: [
          { id: 'fake', name: 'fake', ready: true, missing_secret_env_vars: [] },
          {
            id: 'deepseek',
            name: 'deepseek-v4-pro',
            display_name: 'deepseek-v4-pro',
            ready: true,
            missing_secret_env_vars: [],
          },
        ],
      }),
    ).toEqual({
      configured: true,
      label: 'Model ready',
      detail: 'Default model deepseek-v4-pro is ready.',
    })
  })

  it('keeps fake-only runtime blocked for real research', () => {
    expect(
      getRuntimeStatus({
        default_model: 'fake',
        role_overrides: {},
        models: [{ name: 'fake', ready: true, missing_secret_env_vars: [] }],
      }),
    ).toEqual({
      configured: false,
      label: 'Model not configured',
      detail: 'Only the fake local test model is selected. Configure a real provider before launching research.',
    })
  })
})
