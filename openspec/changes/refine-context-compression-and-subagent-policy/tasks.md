## 1. Context Compression Policy

- [x] 1.1 Add tests for context occupancy calculation using `used_context_tokens / configured_context_window`.
- [x] 1.2 Replace existing compression threshold selection with 50%, 70%, and 90% pressure bands.
- [x] 1.3 Ensure occupancy at or above 90% selects maximum compression behavior.
- [x] 1.4 Ensure context above the configured window after maximum compression is treated as invalid or further reduced, not as a normal higher level.
- [x] 1.5 Preserve the latest user message verbatim and render it as the final user message under every compression band.

## 2. Locator-First Maximum Compression

- [x] 2.1 Add tests for long document and tool output handling under maximum compression.
- [x] 2.2 Apply locator-first rendering for recoverable long documents, papers, web content, tool outputs, logs, and artifacts under aggressive or maximum compression.
- [x] 2.3 Record omitted-context metadata with enough source information to recover omitted content later.
- [x] 2.4 Verify recalled memory, evidence, documents, tool output, and skill metadata remain background context that cannot override the latest user message.

## 3. Research Subagent Routing

- [x] 3.1 Add tests showing normal literature research does not include coding or reproduction subagents by default.
- [x] 3.2 Add tests showing explicit reproduction, benchmark, code execution, implementation inspection, or coding-subagent requests can enable a coding subagent.
- [x] 3.3 Update director routing so coding/reproduction subagents require explicit user opt-in or confirmation when intent is ambiguous.
- [x] 3.4 Ensure coding subagent outputs are represented as execution observations with commands, environment, inputs, observed output, failure details, limitations, and confidence where available.
- [x] 3.5 Ensure synthesis treats coding observations conservatively and does not promote them into final research conclusions without corroborating evidence or explicit user acceptance.

## 4. Verification

- [x] 4.1 Run focused tests for context budgeting and context rendering.
- [x] 4.2 Run focused tests for research director subagent routing.
- [x] 4.3 Run `openspec validate refine-context-compression-and-subagent-policy --strict`.
- [x] 4.4 Run the fastest relevant project test suite and document any remaining gaps.
