## Why

CoResearcher needs clearer runtime policy around context pressure and research subagent routing before the context builder and deep research director become harder to change. The current design records compression levels but does not yet define intuitive occupancy thresholds, and the deep research design allows code-based reproduction work without a strict opt-in boundary.

## What Changes

- Define context window occupancy as `used_context_tokens / configured_context_window`, not as a ratio against an internal overflow budget.
- Set pressure thresholds at 50%, 70%, and 90%, with the highest compression mechanism starting at 90% occupancy.
- Treat any context pack that still exceeds the configured window after maximum compression as invalid, not as a normal higher compression level.
- Preserve the latest user message as authoritative, non-compressible context rendered as the final user message.
- Prefer reversible omission under maximum compression for long papers, long documents, web pages, full tool outputs, and other recoverable context.
- Require code/reproduction/coding subagents to be explicit opt-in, launched only when the user clearly asks for code execution, experiment reproduction, benchmarking, or implementation-based verification.
- Treat coding subagent results as bounded execution observations with environment and limitation metadata, not as authoritative research conclusions.

## Capabilities

### New Capabilities

- `context-compression-policy`: Defines context occupancy thresholds, maximum compression behavior, latest-user-message protection, and invalid over-window handling.
- `research-subagent-routing-policy`: Defines explicit opt-in rules for coding/reproduction subagents and how their outputs are weighted in research synthesis.

### Modified Capabilities

- None. Existing repo-local specs have not yet been archived into `openspec/specs/`; this change captures policy refinements as standalone capabilities that constrain subsequent context-management and research-orchestration implementation.

## Impact

- Affects backend context budgeting and context pack rendering under `backend/coresearcher/context/`.
- Affects research director and subagent routing behavior for deep research workflows.
- Affects tests for compression-level selection, prompt ordering, maximum-compression fallback, and coding subagent delegation.
- Does not add new external dependencies or provider-specific execution backends.
