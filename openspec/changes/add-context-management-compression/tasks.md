## 1. Context Models

- [x] 1.1 Add ContextPack, ContextSection, ContextSectionType, CompressionLevel, and ContextBuildMetadata models.
- [x] 1.2 Add SourceLocator model supporting paper, URL, file, artifact, message, tool_call, note, and database_record references.
- [x] 1.3 Add OmittedContextRecord model with reason, source locator, estimated tokens, and recovery metadata.
- [x] 1.4 Add typed latest-user-message handling so it is separated from selected conversation history before assembly.

## 2. Context Budgeting

- [x] 2.1 Implement model-aware ContextBudgeter with prompt budget, completion reserve, and per-section budget allocation.
- [x] 2.2 Implement token or character estimation utilities for messages, context blocks, tool outputs, snippets, and Skill text.
- [x] 2.3 Implement progressive compression-level selection from Level 0 through Level 5 based on budget pressure.
- [x] 2.4 Add debug metadata for section sizes, selected level, omitted sections, and source locator counts without logging secrets.

## 3. Retrieval And Selection

- [x] 3.1 Implement retrieval inputs that use the latest user message as the primary ranking signal.
- [x] 3.2 Select relevant research state view, active plan, unresolved questions, and current phase for the ContextPack.
- [x] 3.3 Select global user memory and per-research memory through the memory adapter without including candidates by default.
- [x] 3.4 Select evidence, claims, artifacts, paper references, and snippets through SourceLocator-backed retrieval.
- [x] 3.5 Select Skill context by task intent and active LangGraph node without exposing Skill text as system instructions.

## 4. Compression Policies

- [x] 4.1 Implement conversation history policy that never lossy-summarizes user messages.
- [x] 4.2 Implement older user-message selection and omission with message_id preservation.
- [x] 4.3 Implement assistant-history trimming and summarization with transcript locators.
- [x] 4.4 Implement long-document policy that prefers paper, URL, file, page, section, and line locators over full text.
- [x] 4.5 Implement tool-output bounding with excerpt, summary, full-output locator, and truncation metadata.
- [x] 4.6 Implement emergency lossy-summary fallback that preserves source references and never replaces the latest user message.

## 5. Context Rendering And Safety

- [x] 5.1 Implement reserved context tag registry for backend-owned block tags.
- [x] 5.2 Implement sanitizer that removes or escapes reserved tags from dynamic content at render time.
- [x] 5.3 Implement fenced renderers for memory-context, research-state, evidence-context, tool-output, skill-context, and omitted-context blocks.
- [x] 5.4 Add standard notes that mark recalled memory, evidence, tool output, external notes, and Skill text as background data rather than new user input.
- [x] 5.5 Ensure raw sources remain unchanged while only rendered prompt content is sanitized.

## 6. Prompt Assembly

- [x] 6.1 Implement deterministic ContextPack ordering with stable prefix and runtime/context rules first.
- [x] 6.2 Assemble selected conversation history without the latest user message.
- [x] 6.3 Render research state, memory, evidence, tool output, Skill context, and omitted-context manifest before the latest user message.
- [x] 6.4 Render the latest user message verbatim as the final user message.
- [x] 6.5 Add conflict-resolution rules stating that latest user instructions override recalled memory and dynamic background context.

## 7. Director And Subagent Integration

- [x] 7.1 Route Research Director LLM calls through the Context Builder.
- [x] 7.2 Route Subagent LLM calls through task-specific ContextPack slices.
- [x] 7.3 Ensure Subagents receive assigned task, selected state, memory, evidence, tool refs, and applicable Skill context only.
- [x] 7.4 Ensure Subagent results return structured summaries and SourceLocators instead of raw transcript dumps.
- [x] 7.5 Keep Subagent recursion prohibition compatible with context slicing and delegation rules.

## 8. Configuration

- [x] 8.1 Add configuration for context budgets per model, director node, and Subagent node.
- [x] 8.2 Add configuration for per-section token limits, tool-output character limits, and long-document snippet limits.
- [x] 8.3 Add configuration for compression-level thresholds and emergency-summary behavior.
- [x] 8.4 Add configuration for reserved context tags and renderer block names.

## 9. Tests And Validation

- [x] 9.1 Test that latest user message is verbatim and appears last.
- [x] 9.2 Test that user messages are selected or omitted with message IDs but never lossy-summarized.
- [x] 9.3 Test that long papers and files are represented with SourceLocators unless a snippet is selected.
- [x] 9.4 Test that tool output is bounded and includes a full-output locator when truncated.
- [x] 9.5 Test that reserved tags in memory, tool output, external notes, and evidence are sanitized in rendered prompts.
- [x] 9.6 Test that Skill content is rendered as skill-context and not as a system message.
- [x] 9.7 Test that Subagent ContextPack slices exclude unrelated main-thread history.
- [x] 9.8 Test compression-level selection across no-pressure, light-pressure, moderate-pressure, severe-pressure, and emergency cases.

## 10. Implementation Confirmation

- [x] 10.1 Confirm all context entry points go through Context Builder instead of hand-written prompt concatenation in graph nodes.
- [x] 10.2 Confirm the latest user message drives retrieval ranking and is rendered verbatim at the end of the final prompt.
- [x] 10.3 Confirm memory, tool output, paper snippets, external notes, and Skill content are fenced and sanitized for reserved tags.
- [x] 10.4 Confirm long content prefers reversible URL, path, message_id, artifact_id, and tool_call_id references over direct summaries.
- [x] 10.5 Confirm tool permissions and sandbox enforcement remain backend policy concerns, not prompt-only Skill text constraints.
