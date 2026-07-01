## 1. Context Models

- [ ] 1.1 Add ContextPack, ContextSection, ContextSectionType, CompressionLevel, and ContextBuildMetadata models.
- [ ] 1.2 Add SourceLocator model supporting paper, URL, file, artifact, message, tool_call, note, and database_record references.
- [ ] 1.3 Add OmittedContextRecord model with reason, source locator, estimated tokens, and recovery metadata.
- [ ] 1.4 Add typed latest-user-message handling so it is separated from selected conversation history before assembly.

## 2. Context Budgeting

- [ ] 2.1 Implement model-aware ContextBudgeter with prompt budget, completion reserve, and per-section budget allocation.
- [ ] 2.2 Implement token or character estimation utilities for messages, context blocks, tool outputs, snippets, and Skill text.
- [ ] 2.3 Implement progressive compression-level selection from Level 0 through Level 5 based on budget pressure.
- [ ] 2.4 Add debug metadata for section sizes, selected level, omitted sections, and source locator counts without logging secrets.

## 3. Retrieval And Selection

- [ ] 3.1 Implement retrieval inputs that use the latest user message as the primary ranking signal.
- [ ] 3.2 Select relevant research state view, active plan, unresolved questions, and current phase for the ContextPack.
- [ ] 3.3 Select global user memory and per-research memory through the memory adapter without including candidates by default.
- [ ] 3.4 Select evidence, claims, artifacts, paper references, and snippets through SourceLocator-backed retrieval.
- [ ] 3.5 Select Skill context by task intent and active LangGraph node without exposing Skill text as system instructions.

## 4. Compression Policies

- [ ] 4.1 Implement conversation history policy that never lossy-summarizes user messages.
- [ ] 4.2 Implement older user-message selection and omission with message_id preservation.
- [ ] 4.3 Implement assistant-history trimming and summarization with transcript locators.
- [ ] 4.4 Implement long-document policy that prefers paper, URL, file, page, section, and line locators over full text.
- [ ] 4.5 Implement tool-output bounding with excerpt, summary, full-output locator, and truncation metadata.
- [ ] 4.6 Implement emergency lossy-summary fallback that preserves source references and never replaces the latest user message.

## 5. Context Rendering And Safety

- [ ] 5.1 Implement reserved context tag registry for backend-owned block tags.
- [ ] 5.2 Implement sanitizer that removes or escapes reserved tags from dynamic content at render time.
- [ ] 5.3 Implement fenced renderers for memory-context, research-state, evidence-context, tool-output, skill-context, and omitted-context blocks.
- [ ] 5.4 Add standard notes that mark recalled memory, evidence, tool output, external notes, and Skill text as background data rather than new user input.
- [ ] 5.5 Ensure raw sources remain unchanged while only rendered prompt content is sanitized.

## 6. Prompt Assembly

- [ ] 6.1 Implement deterministic ContextPack ordering with stable prefix and runtime/context rules first.
- [ ] 6.2 Assemble selected conversation history without the latest user message.
- [ ] 6.3 Render research state, memory, evidence, tool output, Skill context, and omitted-context manifest before the latest user message.
- [ ] 6.4 Render the latest user message verbatim as the final user message.
- [ ] 6.5 Add conflict-resolution rules stating that latest user instructions override recalled memory and dynamic background context.

## 7. Director And Subagent Integration

- [ ] 7.1 Route Research Director LLM calls through the Context Builder.
- [ ] 7.2 Route Subagent LLM calls through task-specific ContextPack slices.
- [ ] 7.3 Ensure Subagents receive assigned task, selected state, memory, evidence, tool refs, and applicable Skill context only.
- [ ] 7.4 Ensure Subagent results return structured summaries and SourceLocators instead of raw transcript dumps.
- [ ] 7.5 Keep Subagent recursion prohibition compatible with context slicing and delegation rules.

## 8. Configuration

- [ ] 8.1 Add configuration for context budgets per model, director node, and Subagent node.
- [ ] 8.2 Add configuration for per-section token limits, tool-output character limits, and long-document snippet limits.
- [ ] 8.3 Add configuration for compression-level thresholds and emergency-summary behavior.
- [ ] 8.4 Add configuration for reserved context tags and renderer block names.

## 9. Tests And Validation

- [ ] 9.1 Test that latest user message is verbatim and appears last.
- [ ] 9.2 Test that user messages are selected or omitted with message IDs but never lossy-summarized.
- [ ] 9.3 Test that long papers and files are represented with SourceLocators unless a snippet is selected.
- [ ] 9.4 Test that tool output is bounded and includes a full-output locator when truncated.
- [ ] 9.5 Test that reserved tags in memory, tool output, external notes, and evidence are sanitized in rendered prompts.
- [ ] 9.6 Test that Skill content is rendered as skill-context and not as a system message.
- [ ] 9.7 Test that Subagent ContextPack slices exclude unrelated main-thread history.
- [ ] 9.8 Test compression-level selection across no-pressure, light-pressure, moderate-pressure, severe-pressure, and emergency cases.

## 10. 中文任务说明

- [ ] 10.1 确认实现时所有上下文入口都经过 Context Builder，而不是各节点手写 prompt 拼接。
- [ ] 10.2 确认最新用户消息既用于召回排序，又在最终 prompt 中原文放在最后。
- [ ] 10.3 确认记忆、工具输出、论文摘录、外部知识库笔记和 Skill 内容都经过 fence 包裹与 reserved tag 清洗。
- [ ] 10.4 确认长内容优先保留 URL、路径、message_id、artifact_id、tool_call_id 等可逆引用，而不是直接摘要。
- [ ] 10.5 确认真正的工具权限与 sandbox 由后端策略执行，不能依赖 prompt 里的 Skill 文本约束。
