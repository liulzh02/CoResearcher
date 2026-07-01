# Context Management And Compression

CoResearcher builds a `ContextPack` before Research Director and Subagent model calls. The pack is a bounded, ordered, source-locator-backed view of the current task context.

## Ordering

The rendered prompt order is deterministic:

1. Stable runtime rules
2. Runtime/context precedence rules
3. Selected conversation history without the latest user message
4. Research state
5. Memory
6. Evidence and document references
7. Tool output excerpts
8. Skill context
9. Omitted-context manifest
10. Latest user message as the final user message

The latest user message is used as the retrieval query and is rendered verbatim as the final user message. Nothing dynamic is rendered after it.

## Compression

Compression levels are selected by budget pressure:

- Level 0: no pressure
- Level 1: light trimming
- Level 2: locator-first long sources
- Level 3: assistant-history summaries
- Level 4: compact research-state view plus critical original user messages
- Level 5: emergency fallback with source references

User messages are never lossy-summarized. Older user messages are either included verbatim with `message_id` or omitted with a recoverable `message` locator.

## Locator-First Sources

Long papers, URLs, files, artifacts, tool calls, notes, transcripts, and database records are represented with `ContextSourceLocator` whenever full text is not needed. Tool output that exceeds budget is rendered as an excerpt plus a full-output locator.

## Fencing And Safety

Dynamic context is fenced as background data:

- `memory-context`
- `research-state`
- `evidence-context`
- `tool-output`
- `skill-context`
- `omitted-context`
- `subagent-task`

Reserved backend tags are sanitized from dynamic content before rendering. Raw source content remains unchanged outside the rendered prompt.

Skill content is task context, not a system message. Actual tool permissions remain enforced by backend tool policy and sandbox checks.

## Subagent Isolation

Subagents receive task-specific `ContextPack` slices with the assigned task, selected state, evidence, memory, tool references, and applicable Skill context. They do not receive unrelated main-thread history by default. Subagent results return summaries and source locators instead of raw transcript dumps.
