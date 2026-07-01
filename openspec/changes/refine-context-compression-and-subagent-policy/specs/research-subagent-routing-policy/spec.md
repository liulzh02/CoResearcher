## ADDED Requirements

### Requirement: Coding subagent explicit opt-in
The research director MUST NOT launch coding, experiment, benchmark, or reproduction subagents unless the user explicitly requests execution-based validation.

#### Scenario: Normal literature research
- **WHEN** the user asks for a literature review, paper summary, research map, critique, or synthesis without requesting code execution
- **THEN** the director does not include a coding or reproduction subagent in the research plan

#### Scenario: Explicit reproduction request
- **WHEN** the user asks to reproduce a result, run code, benchmark a method, inspect an implementation, or explicitly use the coding subagent
- **THEN** the director may include a coding or reproduction subagent in the research plan

#### Scenario: Ambiguous execution value
- **WHEN** code execution could help but the user did not clearly ask for it
- **THEN** the director asks for confirmation or proceeds without the coding subagent

### Requirement: Coding output as execution observation
The system SHALL treat coding subagent results as bounded execution observations rather than authoritative research conclusions.

#### Scenario: Failed reproduction
- **WHEN** a coding subagent fails to reproduce a result
- **THEN** the synthesis describes the observed failure, environment, and limitations without declaring the source claim false solely from that failure

#### Scenario: Successful run
- **WHEN** a coding subagent successfully runs an experiment or benchmark
- **THEN** the synthesis describes the observed result as evidence from the current environment and inputs rather than as proof of general validity

### Requirement: Coding observation metadata
Coding subagent outputs SHALL include enough metadata for the director to judge scope and reliability.

#### Scenario: Execution result is returned
- **WHEN** a coding subagent returns a result
- **THEN** the result includes commands run, environment or runtime notes, inputs or dataset sample when applicable, observed output, and limitations

#### Scenario: Execution fails
- **WHEN** a coding subagent cannot complete execution
- **THEN** the result includes failure logs or error summaries and identifies whether the failure is likely environmental, dependency-related, data-related, or unknown

### Requirement: Synthesis weights coding observations conservatively
The research synthesis MUST NOT promote a coding observation into a final research conclusion without corroborating source evidence or explicit user acceptance of the observation's limits.

#### Scenario: Coding result conflicts with paper evidence
- **WHEN** a coding observation conflicts with paper evidence
- **THEN** the synthesis presents the conflict as an unresolved or limited observation unless corroborating evidence resolves it

#### Scenario: Coding result supports a claim
- **WHEN** a coding observation supports a claim
- **THEN** the synthesis cites it as execution evidence with scope limitations rather than as a standalone authoritative conclusion
