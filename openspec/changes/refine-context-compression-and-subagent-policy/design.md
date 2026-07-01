## Context

The current context builder already renders stable rules first and the latest user message as the final user message, and it records a `CompressionLevel` in build metadata. However, the level selection thresholds are difficult to reason about and can exceed normal window semantics. The builder also does not yet use the selected level to drive materially different rendering policies.

The deep research assistant design includes a coding/reproduction-oriented subagent. That capability is useful, but code-based reproduction is fragile in research workflows: a failed local run can reflect environment, dependency, data, or parameter mismatch rather than a flaw in the paper or method. The director should not launch that class of subagent unless the user explicitly asks for execution-based validation.

## Goals / Non-Goals

**Goals:**

- Define context occupancy as `used_context_tokens / configured_context_window`.
- Use 50%, 70%, and 90% as the user-facing pressure thresholds.
- Start maximum compression at 90% occupancy.
- Preserve the latest user message verbatim and render it as the final user message.
- Prefer reversible omission over lossy summaries whenever source locators can recover the omitted content.
- Make coding/reproduction subagents explicit opt-in and limit the authority of their conclusions.

**Non-Goals:**

- Do not implement semantic memory conflict detection in this change.
- Do not implement general multi-subagent claim conflict synthesis in this change.
- Do not introduce Docker, AIO, E2B, or other isolated execution providers.
- Do not make coding/reproduction results sufficient to prove or disprove research claims.

## Decisions

### Decision: Occupancy Uses the Configured Context Window

Context pressure SHALL be computed as:

```text
occupancy = used_context_tokens / configured_context_window
```

The configured context window is the maximum prompt/context budget selected for the current run. Internal intermediate estimates can exceed the window while the builder is still compressing, but user-facing compression levels MUST NOT model normal states above 100%.

Alternatives considered:

- Use available prompt budget after completion reserve: rejected because it makes the threshold harder to explain and can mix policy semantics with provider-specific allocation.
- Use overflow tiers above 100%: rejected because a context pack above the configured window is not a valid final state.

### Decision: 50/70/90 Thresholds Drive Compression Policy

The runtime SHALL use these pressure bands:

```text
0-50%    relaxed
50-70%   moderate compression
70-90%   aggressive compression
>=90%    maximum compression
```

At 90% occupancy, the builder MUST switch to maximum compression. If the result still exceeds the configured window, the builder MUST continue dropping recoverable context or fail gracefully instead of producing an over-window prompt.

Alternatives considered:

- Keep the existing 75/110/155/225/320 thresholds: rejected because they are not intuitive and normalize overflow as a level.
- Add many fine-grained bands: rejected for now because the design needs clear operational behavior more than extra labels.

### Decision: Latest User Message Is Non-Compressible

The latest user message SHALL remain verbatim and SHALL be rendered as the final user message in the prompt. Recalled memory, historical conversation, tool output, evidence, documents, and skill metadata remain background context and MUST NOT override the latest user message.

This preserves recency and authority:

```text
system: stable rules
user:   runtime/background context
user:   latest user message
```

### Decision: Maximum Compression Is Locator-First

At maximum compression, recoverable content SHALL be represented by locators and compact summaries instead of full text whenever possible. This includes long papers, long web pages, document bodies, full tool outputs, transcripts, logs, and artifact contents.

The omitted-context record SHOULD preserve enough recovery metadata to reload the source later:

```text
source type
path or URL
artifact/log/message/tool-call id
page or line range when available
estimated omitted tokens
omission reason
```

### Decision: Coding Subagents Are Explicit Opt-In

The research director MUST NOT automatically launch a coding, experiment, benchmark, or reproduction subagent during normal deep research. It may launch one only when the user clearly requests execution-based validation, such as asking to reproduce a result, run code, benchmark an approach, inspect an implementation, or explicitly use the coding subagent.

Coding subagent outputs SHALL be modeled as execution observations, not authoritative research conclusions. They need enough context to interpret the result:

```text
commands run
environment
inputs or dataset sample
observed output
failure logs when relevant
limitations
confidence
```

## Risks / Trade-offs

- [Risk] Maximum compression can omit context the model would have used for nuance. -> Preserve source locators and omitted-context records so the model or director can reload specific sources later.
- [Risk] Occupancy estimates are approximate because token counting may be heuristic. -> Use conservative thresholds and re-estimate after rendering.
- [Risk] Not auto-launching coding subagents can miss useful reproduction signals. -> Allow explicit user opt-in and director clarification when code execution would materially help.
- [Risk] Coding observations may still be over-weighted by synthesis. -> Require limitation metadata and prohibit direct promotion of a coding observation into a final research conclusion without corroborating evidence.

## Migration Plan

1. Update context budgeting to compute and expose occupancy against the configured context window.
2. Replace current compression-level thresholds with 50/70/90 pressure bands.
3. Make rendering policies consume the selected pressure band.
4. Add tests for threshold boundaries, latest-message ordering, maximum-compression locator behavior, and over-window handling.
5. Update research director routing so coding/reproduction subagents require explicit user intent.
6. Add tests that default research plans do not include coding subagents unless requested.

Rollback is straightforward: retain the existing ContextBuilder interfaces and revert to the previous threshold selection and director routing behavior if needed.

## Open Questions

- Should the public metadata expose both a named pressure band and the numeric occupancy percentage?
- Should maximum compression fail hard when over-window, or return a structured "needs retrieval" state for the director to ask for a narrower task?
- Which exact phrases should count as explicit coding/reproduction opt-in in non-English user requests?
