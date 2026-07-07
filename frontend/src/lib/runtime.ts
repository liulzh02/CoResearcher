import type { ModelsResponse } from './types'

export type RuntimeStatus = {
  configured: boolean
  label: string
  detail: string
}

export function getRuntimeStatus(response: ModelsResponse): RuntimeStatus {
  const selected = response.models.find(
    (model) => (model.id ?? model.name) === response.default_model || model.name === response.default_model,
  )
  const selectedId = selected?.id ?? selected?.name

  if (!selected || selectedId?.toLowerCase() === 'fake') {
    return {
      configured: false,
      label: 'Model not configured',
      detail:
        'Only the fake local test model is selected. Configure a real provider before launching research.',
    }
  }

  if (!selected.ready) {
    return {
      configured: false,
      label: 'Model not configured',
      detail: `Default model ${selected.name} is missing: ${selected.missing_secret_env_vars.join(', ')}.`,
    }
  }

  return {
    configured: true,
    label: 'Model ready',
    detail: `Default model ${selected.name} is ready.`,
  }
}
