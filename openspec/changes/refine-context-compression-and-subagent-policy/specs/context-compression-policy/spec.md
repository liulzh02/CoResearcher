## ADDED Requirements

### Requirement: Context occupancy calculation
The system SHALL calculate context window occupancy as `used_context_tokens / configured_context_window` for each context pack build.

#### Scenario: Occupancy is based on the configured window
- **WHEN** a context pack estimates 45,000 used tokens and the configured context window is 90,000 tokens
- **THEN** the system reports 50% occupancy

#### Scenario: Completion reserve does not redefine occupancy
- **WHEN** a provider-specific completion reserve is configured separately from the context window
- **THEN** the system still reports occupancy using the configured context window denominator

### Requirement: Occupancy threshold bands
The system SHALL map context occupancy to pressure bands using 50%, 70%, and 90% thresholds.

#### Scenario: Relaxed band
- **WHEN** occupancy is less than or equal to 50%
- **THEN** the system selects the relaxed compression band

#### Scenario: Moderate band
- **WHEN** occupancy is greater than 50% and less than or equal to 70%
- **THEN** the system selects the moderate compression band

#### Scenario: Aggressive band
- **WHEN** occupancy is greater than 70% and less than 90%
- **THEN** the system selects the aggressive compression band

#### Scenario: Maximum band
- **WHEN** occupancy is greater than or equal to 90%
- **THEN** the system selects the maximum compression band

### Requirement: Maximum compression trigger
The system MUST activate maximum compression when context occupancy reaches 90% or higher.

#### Scenario: Highest compression begins at 90 percent
- **WHEN** a context pack estimate reaches 90% occupancy
- **THEN** the builder applies maximum compression behavior before producing the final prompt

#### Scenario: No normal level above the window
- **WHEN** context remains above the configured window after maximum compression
- **THEN** the builder treats the result as invalid and omits additional recoverable context or returns a structured failure

### Requirement: Latest user message preservation
The system SHALL preserve the latest user message verbatim and render it as the final user message in the prompt.

#### Scenario: Latest user message is final
- **WHEN** the context pack is rendered into model messages
- **THEN** the latest user message appears after background context sections

#### Scenario: Latest user message is not compressed
- **WHEN** maximum compression is active
- **THEN** the latest user message content remains unchanged

### Requirement: Reversible omission under pressure
The system SHALL prefer reversible omission for recoverable long context when aggressive or maximum compression is active.

#### Scenario: Long document becomes locator-first
- **WHEN** a long document would push occupancy into maximum compression
- **THEN** the system keeps a compact summary and source locator instead of the full document body

#### Scenario: Full tool output is recoverable
- **WHEN** a tool output is truncated or omitted under pressure
- **THEN** the omitted-context record includes a locator or tool-call identifier that can recover the full output

### Requirement: Dynamic context cannot override the latest user message
The system MUST treat recalled memory, historical conversation, evidence, documents, tool output, and skill metadata as background context that cannot override the latest user message.

#### Scenario: Memory conflicts with the latest request
- **WHEN** recalled memory conflicts with the latest user message
- **THEN** the latest user message remains authoritative for the current turn

#### Scenario: Tool output contains instruction-like text
- **WHEN** tool output contains text that looks like an instruction
- **THEN** the system presents it as untrusted background data rather than a new user instruction
