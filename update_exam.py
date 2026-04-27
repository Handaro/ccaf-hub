#!/usr/bin/env python3
import json, re

HTML = r'C:\Users\alejandro.parpan\Desktop\genai\cca\CCA-F_study_hub_final.html'

# ── Scenario definitions ───────────────────────────────────────────────────
SC = {
 'sc1':{'sc_label':'Customer Support Agent','sc_color':'#E8F4F0','sc_bc':'#2E7D6A','sc_tc':'#1A4A3A',
        'sc_ctx':'You are building a customer support resolution agent using the Claude Agent SDK. The agent handles high-ambiguity requests like returns, billing disputes, and account issues. It has access to your backend systems through custom MCP tools: get_customer, lookup_order, process_refund, escalate_to_human. Target: 80%+ first-contact resolution while knowing when to escalate.'},
 'sc2':{'sc_label':'Code Generation with Claude Code','sc_color':'#E4F2F8','sc_bc':'#1A6B7A','sc_tc':'#0E3D46',
        'sc_ctx':'You are using Claude Code to accelerate software development for code generation, refactoring, debugging, and documentation. You need to integrate it with custom slash commands, CLAUDE.md configurations, and understand when to use plan mode vs direct execution.'},
 'sc3':{'sc_label':'Multi-Agent Research System','sc_color':'#E8EDF8','sc_bc':'#2A4A80','sc_tc':'#1A2E50',
        'sc_ctx':'You are building a multi-agent research system using the Claude Agent SDK. A coordinator agent delegates to specialized subagents: web search, document analysis, synthesis, and report generation. The system produces comprehensive cited reports.'},
 'sc4':{'sc_label':'Developer Productivity','sc_color':'#F8F0E0','sc_bc':'#7A5010','sc_tc':'#4A3008',
        'sc_ctx':'You are building developer productivity tools using the Claude Agent SDK. The agent helps engineers explore unfamiliar codebases, understand legacy systems, generate boilerplate, and automate repetitive tasks. Uses built-in tools (Read, Write, Bash, Grep, Glob) and MCP servers.'},
 'sc5':{'sc_label':'Claude Code for CI/CD','sc_color':'#F0EAF8','sc_bc':'#5A2A7A','sc_tc':'#3A1A50',
        'sc_ctx':'You are integrating Claude Code into CI/CD pipelines. The system runs automated code reviews, generates test cases, and provides pull request feedback. You need prompts that provide actionable feedback and minimize false positives.'},
 'sc6':{'sc_label':'Structured Data Extraction','sc_color':'#F8EEE0','sc_bc':'#7A4010','sc_tc':'#4A2808',
        'sc_ctx':'You are building a structured data extraction system using Claude. The system extracts information from unstructured documents, validates output using JSON schemas, and maintains high accuracy. Must handle edge cases gracefully and integrate with downstream systems.'},
}

def q(id,sc,d,stem,opts,ans,exp):
    rec = {'id':id,'sc':sc,'d':d,'stem':stem,'opts':opts,'ans':ans,'exp':exp}
    rec.update(SC[sc])
    return rec

EXQDB = [
# ── Scenario 1: Customer Support ──────────────────────────────────────────
q(1,'sc1','D1',
  "Production data shows that in 12% of cases, your agent skips get_customer entirely and calls lookup_order using only the customer's stated name, occasionally leading to misidentified accounts and incorrect refunds. What change would most effectively address this reliability issue?",
  ["Add a programmatic prerequisite that blocks lookup_order and process_refund calls until get_customer has returned a verified customer ID.",
   "Enhance the system prompt to state that customer verification via get_customer is mandatory before any order operations.",
   "Add few-shot examples showing the agent always calling get_customer first, even when customers volunteer order details.",
   "Implement a routing classifier that analyzes each request and enables only the subset of tools appropriate for that request type."],
  0,"When a specific tool sequence is required for critical business logic, programmatic enforcement provides deterministic guarantees that prompt-based approaches cannot. Options B and C rely on probabilistic LLM compliance. Option D addresses tool availability rather than tool ordering."),

q(2,'sc1','D1',
  "You are building a customer support agent using the Claude Agent SDK. The agent processes billing disputes by calling tools like lookup_order, get_invoice, and process_refund. A code review notes that after each tool call, your loop checks whether Claude's response text contains the phrase 'I have completed' to decide whether to stop. What is the primary problem with this loop termination approach?",
  ["The agent will never terminate because process_refund always returns a success message that prevents 'I have completed' from appearing.",
   "Relying on natural language signals in the assistant's text is unreliable; the correct approach is to inspect stop_reason and only terminate when it equals 'end_turn'.",
   "The loop should terminate as soon as any tool call fails, since continuing after a failure will corrupt the conversation history.",
   "Checking response text is only valid in synchronous mode; you must use a callback handler for proper loop control in async contexts."],
  1,"Inspecting stop_reason is the canonical method for agentic loop control: continue iterating when stop_reason is 'tool_use', stop when it is 'end_turn'. Natural language phrases like 'I have completed' are not reliable termination signals because Claude's phrasing varies across responses and prompt updates."),

q(3,'sc1','D1',
  "Your customer support agent handles account closure requests. The workflow requires: (1) verify customer identity via get_customer, (2) check for active subscriptions via check_subscriptions, (3) process closure via close_account. Production logs show the agent occasionally calls close_account before completing the identity verification step, resulting in unauthorized account closures. A colleague suggests adding a system prompt instruction: 'Always verify identity before closing accounts.' What is the most effective approach?",
  ["The system prompt instruction is sufficient because it explicitly describes the required order.",
   "Add few-shot examples showing the correct three-step sequence alongside the system prompt instruction.",
   "Implement a programmatic prerequisite that blocks close_account from executing until get_customer has returned a verified customer ID.",
   "Add a routing classifier that analyzes the request type and pre-selects the appropriate tools before the agent begins."],
  2,"When a tool ordering requirement has serious consequences such as unauthorized account closures, programmatic enforcement provides deterministic guarantees. Prompt instructions have a non-zero failure rate even when explicit. Option A relies on probabilistic compliance. Option B improves odds but still does not guarantee compliance. Option D addresses tool selection rather than ordering enforcement."),

q(4,'sc1','D1',
  "A customer contacts your support agent about three issues in a single message: a billing charge dispute, a missing order, and a request to update their email address. The agent processes these sequentially, taking 3-4 minutes per request. A senior architect suggests you redesign the handling approach. What design change would most improve efficiency while maintaining accuracy?",
  ["Instruct the agent to address only the highest-priority issue per conversation turn and ask the customer to submit separate tickets for the remaining issues.",
   "Decompose the three concerns into distinct investigation items and process each in parallel using shared customer context, then compile a unified response.",
   "Process the three issues sequentially but cache intermediate results so subsequent issues benefit from data already retrieved.",
   "Delegate all three issues to a single specialized 'multi-issue' subagent that handles complex requests with multiple concerns."],
  1,"When a customer presents multiple independent concerns, decomposing them into parallel investigation items dramatically reduces latency. Each concern can be investigated simultaneously using shared customer context. Option A creates a poor customer experience. Option C improves caching but does not eliminate the serial bottleneck. Option D creates an undifferentiated subagent that does not reflect the coordinator-subagent specialization pattern."),

q(5,'sc1','D1',
  "Your customer support agent integrates with three backend MCP tools: a legacy billing system returning Unix timestamps, an order management system returning ISO 8601 dates, and a subscription service returning numeric status codes (1=active, 2=paused, 3=cancelled). The agent frequently misinterprets these heterogeneous formats when reasoning about customer records. What is the most appropriate architectural fix?",
  ["Update each backend system to return a uniform date and status format before the agent calls them.",
   "Add format conversion instructions to the system prompt explaining how to interpret each tool's output conventions.",
   "Implement PostToolUse hooks that intercept tool results from each source and normalize timestamps, dates, and status codes into a consistent format before the model processes them.",
   "Add a post-processing step after the agent produces its final response to re-format any dates and statuses that appear in the output."],
  2,"PostToolUse hooks are the correct mechanism for intercepting and transforming tool results before the model processes them. This ensures the model always sees normalized data regardless of backend heterogeneity. Option A requires backend changes that may not be feasible. Option B relies on probabilistic compliance and adds token overhead. Option D applies normalization after the model has already reasoned on inconsistent data."),

q(6,'sc1','D1',
  "Your customer support agent has a policy: refunds above $500 require manager approval and must not be processed autonomously. Your system prompt states 'Do not process refunds above $500 without manager approval.' Production logs show this rule is violated in approximately 3% of cases. What is the most effective way to guarantee compliance?",
  ["Strengthen the system prompt language: 'You are strictly forbidden from processing refunds above $500 without explicit manager approval under any circumstances.'",
   "Add 10 few-shot examples in the system prompt, all demonstrating the agent requesting manager approval for high-value refunds.",
   "Implement a hook that intercepts outgoing process_refund tool calls, checks the refund amount, and blocks execution or redirects to the manager approval workflow when the amount exceeds $500.",
   "Implement a validation step that runs after process_refund completes and reverses any refunds that exceeded the threshold."],
  2,"Business rules that require guaranteed compliance must be enforced programmatically. A hook that intercepts process_refund calls before execution provides deterministic enforcement regardless of how the model interprets the system prompt. Options A and B improve adherence probabilistically but cannot guarantee zero violations. Option D runs after the action has already been taken — the policy violation has already occurred."),

q(7,'sc1','D4',
  "Production logs show the agent frequently calls get_customer when users ask about orders, instead of calling lookup_order. Both tools have minimal descriptions and accept similar identifier formats. What's the most effective first step to improve tool selection reliability?",
  ["Add few-shot examples to the system prompt demonstrating correct tool selection patterns, with 5-8 examples.",
   "Expand each tool's description to include input formats it handles, example queries, edge cases, and boundaries explaining when to use it versus similar tools.",
   "Implement a routing layer that parses user input before each turn and pre-selects the appropriate tool based on detected keywords.",
   "Consolidate both tools into a single lookup_entity tool that accepts any identifier and internally determines which backend to query."],
  1,"Tool descriptions are the primary mechanism LLMs use for tool selection. Option B directly addresses the root cause. Few-shot examples (A) add token overhead without fixing the underlying issue. A routing layer (C) is over-engineered. Consolidating tools (D) requires more effort than a first step warrants."),

q(8,'sc1','D4',
  "Your customer support agent has a lookup_order tool that is called at the right times, but frequently returns errors. Logs show the agent passes free-text descriptions like 'order from last Tuesday' instead of the required ISO-8601 timestamp format. The tool description reads: 'Retrieves order details given a date or identifier.' No examples or format constraints are provided. What change to the tool definition would most directly reduce these input format errors?",
  ["Add input format constraints, accepted value formats, and example inputs to the tool description so the model knows exactly how to format its calls.",
   "Add a system prompt instruction: 'Always use ISO-8601 format when calling lookup_order.'",
   "Add input schema validation that rejects malformed inputs and returns an error to the agent.",
   "Split lookup_order into two tools: lookup_order_by_id and lookup_order_by_date to reduce ambiguity."],
  0,"Tool descriptions are the primary mechanism the model uses to understand how to call a tool. Adding format constraints and examples directly to the description gives the model the information it needs at decision time. Option B is more fragile than a tool-specific description. Option C adds validation but does not prevent the model from sending malformed inputs in the first place. Option D addresses disambiguation rather than format guidance."),

q(9,'sc1','D4',
  "Your customer support agent has three tools with overlapping names and descriptions: get_account_info ('Get information about the account'), fetch_account_details ('Fetch account details'), and retrieve_customer_record ('Retrieve customer information'). All three call different backend systems with different data. The agent frequently picks the wrong tool. Which approach most effectively resolves the misrouting?",
  ["Add a system prompt instruction listing all three tools and specifying exactly when each should be used based on the request type.",
   "Rename the tools to reflect their distinct data sources and rewrite their descriptions to explain what data each returns, what backend it queries, and what use case it serves.",
   "Consolidate all three tools into one tool with a source parameter that specifies which backend to query.",
   "Keep the current tools but randomize which one the agent calls, then merge the responses in a post-processing step."],
  1,"Ambiguous or overlapping tool names and descriptions cause misrouting. Renaming tools to reflect their distinct backends and writing descriptions that explain what each one returns, where its data comes from, and when to use it are the right fixes. Option A may reduce misrouting but does not fix the root problem. Option C shifts the burden of correct routing back to the model in a less structured way. Option D is not a viable architecture."),

q(10,'sc1','D4',
  "Your customer support MCP tool process_refund returns the same error response for all failures: {status: 'error', message: 'Operation failed'}. The agent currently handles all errors by apologizing to the customer and ending the conversation. Logs show this response is triggered by: network timeouts, invalid refund amounts, refunds blocked by fraud detection, and expired order IDs. What structured error response design would most improve the agent's ability to recover appropriately?",
  ["Return different HTTP status codes for each failure type and have the agent interpret the status code to determine recovery action.",
   "Return structured error metadata including errorCategory (transient/validation/permission/business), isRetryable boolean, and a human-readable explanation specific to the failure reason.",
   "Return a verbose error log with the full stack trace and system state so the agent has maximum information to reason from.",
   "Return a numeric error code and have the system prompt map each code to a recovery action."],
  1,"Structured error metadata gives the agent the information it needs to choose the correct recovery path: retry a transient failure, ask the customer for corrected input on a validation failure, or explain a policy block on a business rule violation. Option A relies on HTTP semantics that may not map cleanly to all failure categories. Option C provides excessive detail that consumes context without improving decision quality. Option D encodes recovery logic in the system prompt rather than in a principled error structure."),

q(11,'sc1','D4',
  "Your MCP tool check_fraud_risk returns {isError: true, message: 'Refund blocked'} when a refund is flagged by fraud detection. The agent interprets this as a transient failure and retries the refund three times before giving up. Each retry generates a separate fraud alert in your compliance system. What is the missing element in the error response design?",
  ["The response should include a retry_after timestamp so the agent knows when to retry.",
   "The response should include isRetryable: false and a customer-appropriate explanation distinguishing this business rule block from a transient system error.",
   "The tool should suppress the isError flag for fraud blocks and instead return the result as a successful response with a blocked: true field.",
   "The response should include the fraud risk score so the agent can decide whether the score is high enough to justify blocking."],
  1,"A business rule block from fraud detection is a non-retryable error. Including isRetryable: false signals to the agent that retrying will not resolve the situation, preventing redundant attempts that trigger compliance alerts. Option A implies the block is temporary and retriable. Option C hides the error nature of the response. Option D provides fraud risk data to the agent that it may not be authorized to act on directly."),

q(12,'sc1','D4',
  "Your customer support system requires that every response from the draft_response agent includes a structured JSON summary before the agent returns its output. You want to guarantee the agent calls the generate_summary tool on every invocation, not optionally. Which tool_choice configuration achieves this?",
  ["Set tool_choice: 'auto' so the model decides when the summary tool is needed.",
   "Set tool_choice: 'any' so the model must call at least one tool, though it may choose a different tool instead.",
   "Set tool_choice: {type: 'tool', name: 'generate_summary'} to force the model to call generate_summary specifically.",
   "Remove all other tools from the agent's tool list so generate_summary is the only option available."],
  2,"Forced tool selection via tool_choice: {type: 'tool', name: 'generate_summary'} guarantees the model calls that specific tool on every invocation. Option A allows the model to return text without calling any tool. Option B guarantees a tool call but does not guarantee which tool. Option D achieves the same result indirectly but removes legitimate tools the agent may need for its other tasks."),

q(13,'sc1','D5',
  "Your agent achieves 55% first-contact resolution, well below the 80% target. Logs show it escalates straightforward cases while attempting to autonomously handle complex situations requiring policy exceptions. What's the most effective way to improve escalation calibration?",
  ["Add explicit escalation criteria to your system prompt with few-shot examples demonstrating when to escalate versus resolve autonomously.",
   "Have the agent self-report a confidence score (1-10) before each response and automatically route requests to humans when confidence falls below a threshold.",
   "Deploy a separate classifier model trained on historical tickets to predict which requests need escalation before the main agent begins processing.",
   "Implement sentiment analysis to detect customer frustration levels and automatically escalate when negative sentiment exceeds a threshold."],
  0,"Adding explicit escalation criteria with few-shot examples directly addresses the root cause: unclear decision boundaries. Option B fails because LLM self-reported confidence is poorly calibrated. Option C is over-engineered. Option D solves a different problem entirely."),

q(14,'sc1','D5',
  "A customer support agent is handling a complex billing dispute that spans 20+ turns. A customer mentioned early in the conversation that they were charged $847.50 on March 3rd for a service they cancelled on February 28th. Midway through the conversation, the agent references the charge as 'the overcharge from last month' without the specific amount. The customer disputes the agent's understanding of the case. What context management technique would prevent this?",
  ["Use /compact at the start of each conversation to summarize prior turns into a shorter representation.",
   "Extract transactional facts (amounts, dates, order numbers, statuses) into a persistent 'case facts' block that is included at the beginning of every subsequent prompt in the conversation.",
   "Increase the model's context window by switching to a larger tier to retain the full conversation without summarization.",
   "Instruct the agent to re-read the full conversation history before each response."],
  1,"Extracting precise transactional facts into a persistent 'case facts' block ensures that specific numerical values, dates, and customer-stated details are explicitly available in every prompt turn rather than buried in growing conversation history. Option A's compaction can lose precision on transactional facts. Option C does not prevent progressive summarization. Option D is not practical for long conversations."),

q(15,'sc1','D5',
  "A customer opens a support chat saying 'I'd like to speak to a human please. I've been dealing with this billing issue for three weeks and I'm frustrated.' The agent has already identified this as a standard billing adjustment that it can resolve in 2 steps using its available tools. Your agent responds by saying 'I can help with that right away, let me pull up your account.' and proceeds to investigate. The customer repeats their request for a human. What is wrong with this behavior?",
  ["The agent should honor an explicit customer request for a human agent immediately on first request, without attempting investigation first.",
   "The agent should detect negative sentiment and escalate once the frustration score exceeds a defined threshold.",
   "The agent should complete its investigation, present the proposed solution, and escalate only if the customer still insists afterward.",
   "The agent should apologize for the wait, then proceed with automated resolution since the case is within its capability."],
  0,"When a customer explicitly requests a human agent, that request must be honored immediately regardless of whether the agent believes it can resolve the issue. Option B introduces sentiment scoring as a proxy, but the customer has already expressed an explicit preference. Option C delays honoring the request. Option D is the agent's current incorrect behavior: capability is not the deciding factor when a customer has made an explicit request."),

# ── Scenario 3: Multi-Agent Research ──────────────────────────────────────
q(16,'sc3','D1',
  "After running on 'impact of AI on creative industries,' each subagent completes successfully but the final reports cover only visual arts, missing music, writing, and film production. The coordinator decomposed the topic into: 'AI in digital art creation,' 'AI in graphic design,' and 'AI in photography.' What is the most likely root cause?",
  ["The synthesis agent lacks instructions for identifying coverage gaps in the findings it receives from other agents.",
   "The coordinator agent's task decomposition is too narrow, resulting in subagent assignments that don't cover all relevant domains.",
   "The web search agent's queries are not comprehensive enough and need to be expanded to cover more creative industry sectors.",
   "The document analysis agent is filtering out sources related to non-visual creative industries due to overly restrictive relevance criteria."],
  1,"The coordinator's logs reveal the root cause directly: it decomposed 'creative industries' into only visual arts subtasks. The subagents executed their assigned tasks correctly. The problem is what they were assigned."),

q(17,'sc3','D1',
  "Your multi-agent research system uses a coordinator that always routes every query through all four subagents (web search, document analysis, synthesis, and report generation) regardless of query complexity. For a simple factual question like 'What year was the Anthropic API released?', the system takes 45 seconds and incurs unnecessary cost. What design change most directly addresses this?",
  ["Replace the coordinator with a static routing table that maps query keywords to specific subagent pipelines.",
   "Have each subagent evaluate its own relevance to the current query and self-select into or out of the pipeline.",
   "Design the coordinator to dynamically select which subagents to invoke based on query complexity and type, rather than always routing through the full pipeline.",
   "Reduce the number of subagents from four to two by merging web search and document analysis into a single 'retrieval' agent."],
  2,"A coordinator that always runs the full pipeline regardless of query complexity wastes resources and adds latency for simple requests. The correct design is a coordinator that evaluates the query and selects only the subagents needed. Option A replaces adaptive intelligence with a brittle keyword table. Option B distributes coordination logic across subagents, breaking the hub-and-spoke pattern. Option D reduces capability unnecessarily."),

q(18,'sc3','D1',
  "A coordinator agent in your research system has delegated document analysis to a subagent. After the subagent finishes, the coordinator notices the findings are incomplete: the subagent covered only three of the five specified sources. The coordinator needs to get the remaining two sources analyzed. What is the correct approach for re-delegating this work?",
  ["Invoke the synthesis agent with the partial findings and instruct it to infer what the missing sources likely contain based on patterns from the three completed analyses.",
   "The coordinator should re-invoke the document analysis subagent with an explicit prompt specifying only the two missing sources, including the previously completed findings as context.",
   "Send all five sources again to a new document analysis subagent instance, which will re-analyze the three already-completed sources along with the two missing ones.",
   "Let the coordinator generate its own analysis of the remaining two sources directly, rather than spawning another subagent delegation."],
  1,"The coordinator's role includes evaluating output for gaps and re-delegating targeted work to close those gaps. Re-invoking the subagent with only the unfinished sources and providing the completed findings as context is efficient and correct. Option A asks synthesis to fabricate content. Option C wastes resources by re-processing already-completed sources. Option D bypasses the coordinator-subagent architecture."),

q(19,'sc3','D1',
  "You are building a coordinator that delegates research tasks to subagents using the Task tool. When you test the system, the coordinator cannot invoke any subagents. Reviewing the coordinator's AgentDefinition, you notice the allowedTools field is set to ['web_search', 'read_document']. What is the most likely cause of the failure?",
  ["The Task tool requires an explicit subagent_endpoint configuration before it can be invoked.",
   "'Task' is not included in the coordinator's allowedTools, so it cannot spawn subagents.",
   "The coordinator's system prompt does not include instructions to use the Task tool, so the model never attempts to call it.",
   "Subagent invocation requires the coordinator to be running in plan mode rather than direct execution mode."],
  1,"The Task tool is the mechanism for spawning subagents in the Claude Agent SDK. For a coordinator to invoke subagents, 'Task' must be explicitly included in its allowedTools. Option A describes a configuration parameter that does not exist. Option C conflates prompt instructions with capability gating. Option D conflates plan mode with subagent spawning."),

q(20,'sc3','D1',
  "Your multi-agent research system has a web search subagent that consistently returns findings without identifying which sources correspond to which claims. When the synthesis agent receives these findings, it cannot produce properly cited reports. What is the correct fix during context passing?",
  ["Instruct the synthesis agent to run its own web searches to re-locate the original sources.",
   "Use structured data formats that separate claim content from metadata (source URLs, publication dates, page numbers) in the subagent's output, and include this structure when passing context to the synthesis agent.",
   "Have the coordinator concatenate all subagent outputs into a single text block before forwarding to synthesis, since synthesis will extract citations naturally.",
   "Configure the web search subagent to return only source URLs, and have the synthesis agent re-read each source to reconstruct the findings."],
  1,"Structured data formats that separate content from metadata ensure that claim-source mappings survive the handoff between agents. When context is passed as unstructured text, citation information is easily lost. Option A introduces redundant work. Option C risks losing the claim-source associations during concatenation. Option D is extremely inefficient."),

q(21,'sc3','D1',
  "A coordinator needs to research three independent subtopics in parallel: market trends, competitor analysis, and regulatory environment. Each requires a separate web search subagent. How should the coordinator spawn these subagents to maximize throughput?",
  ["Spawn the subtopics sequentially: start the first subagent, wait for its result, then start the second, and so on, to avoid context conflicts.",
   "Emit all three Task tool calls in a single coordinator response, which allows the subagents to run in parallel.",
   "Route all three subtopics through a single subagent sequentially, sharing context between them to reduce total memory usage.",
   "Use a single subagent with three separate prompts in sequence, passing prior results as context for each subsequent prompt."],
  1,"The Claude Agent SDK supports parallel subagent execution by emitting multiple Task tool calls in a single coordinator response. This maximizes throughput for independent subtopics that do not depend on each other's results. Option A introduces unnecessary serial latency. Option C assumes a dependency that the question does not establish. Option D collapses three specialists into one sequential process."),

q(22,'sc3','D1',
  "Your multi-agent research system's agentic loop appends each tool result to the conversation history before sending the next request. A teammate suggests instead storing all tool results in a separate database and providing only a summary to the model at each iteration, rather than the full result. Under what condition would this change most likely degrade agent performance?",
  ["When the tool results contain binary data such as images or file attachments.",
   "When the model needs to reason across multiple tool results simultaneously to determine its next action, since summaries may omit details required for that reasoning.",
   "When the number of tool calls per session exceeds 10, since larger histories slow down the API.",
   "When tools return results faster than 200ms, making history appending redundant."],
  1,"The agentic loop depends on tool results being present in conversation history so the model can reason about what it has already discovered before deciding its next action. Summaries may omit field values, error codes, or conditional data the model needs to make correct decisions. Option A is a valid concern but not the primary performance risk. Options C and D are not recognized failure modes for this architecture."),

q(23,'sc3','D4',
  "The web search subagent times out while researching a complex topic. You need to design how this failure information flows back to the coordinator agent. Which error propagation approach best enables intelligent recovery?",
  ["Return structured error context to the coordinator including the failure type, the attempted query, any partial results, and potential alternative approaches.",
   "Implement automatic retry logic with exponential backoff within the subagent, returning a generic 'search unavailable' status only after all retries are exhausted.",
   "Catch the timeout within the subagent and return an empty result set marked as successful.",
   "Propagate the timeout exception directly to a top-level handler that terminates the entire research workflow."],
  0,"Structured error context gives the coordinator the information it needs to make intelligent recovery decisions. Option B's generic status hides valuable context. Option C suppresses the error, preventing any recovery. Option D terminates the entire workflow unnecessarily."),

q(24,'sc3','D4',
  "The synthesis agent frequently needs to verify specific claims while combining findings. Currently, this creates 2-3 round trips per task, increasing latency by 40%. 85% of verifications are simple fact-checks; 15% require deeper investigation. What's the most effective approach to reduce overhead while maintaining reliability?",
  ["Give the synthesis agent a scoped verify_fact tool for simple lookups, while complex verifications continue delegating to the web search agent through the coordinator.",
   "Have the synthesis agent accumulate all verification needs and return them as a batch to the coordinator at the end of its pass.",
   "Give the synthesis agent access to all web search tools so it can handle any verification need directly without round-trips.",
   "Have the web search agent proactively cache extra context around each source during initial research, anticipating what the synthesis agent might need to verify."],
  0,"Option A applies the principle of least privilege by giving the synthesis agent only what it needs for the 85% common case while preserving the existing coordination pattern for complex cases. Option B creates blocking dependencies. Option C over-provisions the synthesis agent. Option D relies on speculative caching."),

q(25,'sc3','D4',
  "A web search subagent in your research system calls search_web and receives: {results: [], status: 'success'}. The subagent reports to the coordinator: 'Web search was successful but no relevant results were found.' Later you discover the search API was actually down and returning empty results for all queries. What change to the MCP tool's error handling would prevent this confusion?",
  ["Always return a non-empty results array by including fallback content when the actual search returns nothing.",
   "Distinguish between access failures (where the backend could not be reached or returned an error) and valid empty results (where the search succeeded but found no matches), using the isError flag for the former.",
   "Add a confidence field to the response so the agent can infer whether the empty result is a real outcome or a failure.",
   "Implement automatic retry in the MCP tool itself, so the agent never sees an empty result unless all retries were exhausted."],
  1,"Access failures and valid empty results are fundamentally different conditions that require different agent responses. Using the isError flag for access failures while returning {results: [], status: 'success'} only for genuine empty-result queries gives the coordinator accurate information. Option A masks failures by fabricating content. Option C introduces ambiguity. Option D handles retries locally but does not solve the agent's inability to distinguish the two conditions."),

q(26,'sc3','D4',
  "You are building a multi-agent research system with a synthesis agent whose sole job is combining findings from subagents and producing a structured report. You have given the synthesis agent access to all 18 tools in your system: web search, file reading, database queries, email sending, calendar access, and more. What problem does this configuration most likely introduce?",
  ["The synthesis agent will refuse to call any tools because it is overwhelmed by the number of choices.",
   "Having access to tools outside its specialization increases the likelihood the synthesis agent will misuse them, such as initiating new web searches instead of synthesizing the provided findings.",
   "18 tools will exceed the context window limit for tool schemas, causing API errors on every request.",
   "The additional tools will slow down the synthesis agent because the model must read all tool descriptions before producing output."],
  1,"Giving an agent access to tools outside its specialization degrades tool selection reliability. A synthesis agent with web search tools will sometimes initiate new searches rather than working with the findings already provided. Option A overstates the effect. Option C is not a realistic failure mode for 18 tools with typical schema sizes. Option D mischaracterizes how tool descriptions affect latency."),

q(27,'sc3','D1',
  "You are leading a research investigation using Claude Code. You have completed an initial analysis of a competitor's public API documentation and want to explore two divergent architectural approaches for your response strategy: one focused on feature parity, one focused on differentiation. You want both explorations to start from the same analysis baseline. Which session management approach best fits this scenario?",
  ["Run two separate new sessions, each with a copy of the analysis findings injected as context in the initial prompt.",
   "Use --resume to resume the current session twice in parallel, once for each exploration direction.",
   "Use fork_session to create two independent branches from the current session, then explore each approach in its respective branch.",
   "Continue in the same session, exploring one approach, then using /compact to clear context before exploring the second approach."],
  2,"fork_session is designed precisely for this scenario: creating independent branches from a shared analysis baseline to explore divergent approaches. Each branch inherits the common findings and can be explored independently without contaminating the other. Option A requires duplicating context. Option B describes a mechanism that does not work this way. Option D uses /compact destructively, losing the baseline context needed for the second exploration."),

q(28,'sc3','D5',
  "A multi-agent research pipeline aggregates findings from six subagents, each returning 800-1,200 tokens of raw tool output and reasoning. The synthesis agent receives all results in a single large message. The final report consistently omits or contradicts findings that appeared in the middle sections of the aggregated input. What is the most likely cause and the most effective mitigation?",
  ["The subagents are returning conflicting information; add a deduplication step before synthesis.",
   "The synthesis agent is hitting its output token limit; increase max_tokens to allow a longer response.",
   "The 'lost in the middle' effect causes models to reliably process content at the beginning and end of long inputs but miss middle sections. Mitigate by placing key findings summaries at the beginning of aggregated inputs and organizing sections with explicit headers.",
   "The synthesis agent's context window is exhausted; route some subagent outputs through a secondary summarization agent before passing to synthesis."],
  2,"The 'lost in the middle' effect is a well-documented limitation where models attend less reliably to content in the middle of long inputs. Placing key findings at the beginning and using explicit section headers significantly mitigates this effect. Option A addresses data consistency but not positional attention. Option B addresses output length, not input attention. Option D adds pipeline complexity but does not address the positional attention issue."),

q(29,'sc3','D5',
  "Your web search subagent encounters a timeout while fetching results for a competitor analysis. The engineering team implements a change so the subagent catches the timeout internally and returns an empty result set with status: 'success' and results: []. The coordinator receives this and the synthesis agent produces a report that is missing the competitive section entirely, with no indication anything went wrong. What is the problem with this approach?",
  ["Silently returning an empty success result prevents the coordinator from making any recovery decision and allows incomplete work to pass as complete output.",
   "The synthesis agent should be responsible for detecting empty sections and re-triggering the search subagent directly.",
   "The coordinator should always validate that each subagent returned non-empty results before proceeding to synthesis.",
   "The timeout threshold should be increased so that the subagent does not time out before returning real results."],
  0,"Silently suppressing errors by returning empty results as success is an explicitly documented anti-pattern. It removes the coordinator's ability to recover, retry, or annotate output with coverage gaps. Option B incorrectly shifts recovery responsibility to the synthesis agent. Option C adds coordinator-level validation as a safeguard but does not address the root cause. Option D addresses the symptom rather than the error propagation design flaw."),

q(30,'sc3','D5',
  "A research synthesis agent is combining findings from five subagents that searched different sources. The final report states that 'AI adoption in healthcare reached 45% in 2024' but does not cite which source this came from. A reviewer cannot verify the claim because the subagents' individual outputs were not preserved. What structural change to the pipeline would prevent this provenance loss?",
  ["Require the synthesis agent to add a generic 'Sources consulted' section at the end of the report listing all sources accessed.",
   "Require subagents to output structured claim-source mappings (claim text, source URL, document name, relevant excerpt) and instruct the synthesis agent to preserve and merge these mappings into the final report rather than summarizing them away.",
   "Store all raw subagent outputs in a separate log file so they can be consulted if a claim needs verification.",
   "Add a post-synthesis review step where a separate agent checks each claim in the report against the raw subagent outputs."],
  1,"The root cause of provenance loss is that summarization steps compress findings without preserving claim-to-source mappings. Requiring subagents to output structured mappings and instructing the synthesis agent to preserve and merge them ensures that each claim in the final report carries its source attribution. Option A produces a list of sources but does not link individual claims to specific sources. Option C stores raw data but does not integrate provenance into the report. Option D adds a verification step but does not prevent the structural provenance loss."),

# ── Scenario 2: Code Generation with Claude Code ───────────────────────────
q(31,'sc2','D2',
  "A senior engineer adds detailed coding standards and security guidelines to their ~/.claude/CLAUDE.md file. When a new team member joins and clones the repository, they report that Claude Code behaves differently and does not appear to follow the team's documented standards. What is the most likely cause?",
  ["The new team member's Claude Code version is outdated and does not support shared configuration files.",
   "The ~/.claude/CLAUDE.md file is user-scoped and not version-controlled, so teammates do not receive it when they clone the repository.",
   "CLAUDE.md files must be placed in the .claude/ subdirectory to be recognized; a root-level CLAUDE.md is ignored.",
   "The configuration hierarchy requires the project-level file to explicitly import from user-level files using @import."],
  1,"User-level configuration in ~/.claude/CLAUDE.md applies only to the individual developer and is never committed to version control. Teammates will not see it regardless of their setup. To share standards across the team, those instructions must live in the project-level CLAUDE.md, which is committed to the repository. Options A and D describe mechanisms that do not exist. Option C is incorrect because a root-level CLAUDE.md is a valid project-level location."),

q(32,'sc2','D2',
  "Your monorepo has a root CLAUDE.md that has grown to over 400 lines, covering Python conventions, TypeScript conventions, infrastructure rules, and testing standards. Developers report that Claude sometimes applies the wrong conventions to the wrong files, and the file is difficult to maintain. What is the best approach to reorganize this configuration?",
  ["Split the content into multiple files in .claude/rules/, with each file covering a focused topic, and use path-scoped YAML frontmatter to activate rules only for relevant files.",
   "Create a separate CLAUDE.md in each top-level package directory and delete the root file entirely.",
   "Add inline section headers to the monolithic file and use the /memory command to tell Claude which section to prioritize for each task.",
   "Break the root CLAUDE.md into topic files and use @import directives in the root file to pull them all in unconditionally."],
  0,"The .claude/rules/ directory is designed for exactly this scenario: organizing topic-specific rule files with YAML frontmatter path scoping so each rule set activates only when editing relevant files. This reduces irrelevant context and token usage. Option B would require duplicating shared rules across package directories. Option C relies on manual intervention each session. Option D with unconditional @import addresses the maintenance concern but not the wrong-conventions problem."),

q(33,'sc2','D2',
  "You maintain a monorepo with five packages: a Python backend, a TypeScript frontend, a Go service, shared infrastructure Terraform, and a documentation site. Each package has different linting standards, testing conventions, and framework-specific rules. The root CLAUDE.md has grown to 600 lines and developers report that rules intended for one package often bleed into sessions working on another. What is the most modular and maintainable solution?",
  ["Create a CLAUDE.md in each package directory with that package's rules, and use @import in the root CLAUDE.md to include shared conventions that apply to all packages.",
   "Keep the 600-line root file but add explicit section headers and instruct developers to tell Claude which section applies at the start of each session.",
   "Delete the root CLAUDE.md and rely entirely on package-level files, accepting that shared conventions must be duplicated across packages.",
   "Move all rules into .claude/rules/ files and tag each with a projects: key in their frontmatter specifying which subdirectory the rule applies to."],
  0,"The @import syntax in CLAUDE.md is designed for exactly this modular pattern: shared conventions in the root file, package-specific rules in each package's own CLAUDE.md. This keeps each file focused and maintainable while eliminating rule bleed. Option B relies on developer discipline to manually scope rules each session. Option C requires duplicating common conventions. Option D is valid for path-scoped rules but does not address the need for package-level CLAUDE.md isolation."),

q(34,'sc2','D2',
  "You want to create a custom /review slash command that runs your team's standard code review checklist and should be available to every developer when they clone or pull the repository. Where should you create this command file?",
  ["In the .claude/commands/ directory in the project repository.",
   "In ~/.claude/commands/ in each developer's home directory.",
   "In the CLAUDE.md file at the project root.",
   "In a .claude/config.json file with a commands array."],
  0,"Project-scoped custom slash commands are stored in .claude/commands/ within the repository, version-controlled and automatically available to all developers. Option B is for personal, non-shared commands. Option C is for project instructions, not command definitions. Option D describes a mechanism that does not exist."),

q(35,'sc2','D2',
  "A developer wants a /scaffold skill that generates boilerplate for a new microservice. The skill runs many exploratory file reads and Bash commands to understand existing patterns before generating output, producing hundreds of lines of intermediate output. Teammates complain this pollutes their main conversation context. Which frontmatter setting resolves this?",
  ["Set allowed-tools: [] in the skill's frontmatter to prevent tool use during execution.",
   "Set context: fork in the skill's frontmatter to run the skill in an isolated sub-agent context that does not affect the main session.",
   "Move the skill file from .claude/skills/ to .claude/commands/ so it runs as a command rather than a skill.",
   "Add argument-hint: 'service-name' to the frontmatter so the skill receives a clean input without inheriting session context."],
  1,"The context: fork frontmatter option runs the skill in an isolated sub-agent context. All exploratory output, intermediate tool calls, and reasoning happen in the fork and do not accumulate in the main conversation context. Only the final output is returned to the parent session. Option A would disable the tool use the skill depends on. Option C does not change execution isolation behavior. Option D is for prompting the user for input parameters."),

q(36,'sc2','D2',
  "Your codebase has distinct areas with different conventions. Test files are spread throughout the codebase alongside the code they test. You want all tests to follow the same conventions regardless of location. What's the most maintainable way to ensure Claude automatically applies the correct conventions when generating code?",
  ["Create rule files in .claude/rules/ with YAML frontmatter specifying glob patterns to conditionally apply conventions based on file paths.",
   "Consolidate all conventions in the root CLAUDE.md file under headers for each area, relying on Claude to infer which section applies.",
   "Create skills in .claude/skills/ for each code type that include the relevant conventions in their SKILL.md files.",
   "Place a separate CLAUDE.md file in each subdirectory containing that area's specific conventions."],
  0,".claude/rules/ with glob patterns such as **/*.test.tsx allows conventions to be automatically applied based on file paths regardless of directory location. Option B relies on inference rather than explicit matching. Option C requires manual invocation. Option D cannot easily handle files spread across many directories."),

q(37,'sc2','D2',
  "Your team uses Terraform for infrastructure but only in the infra/ directory. You want Claude to automatically apply Terraform naming conventions and module structure rules only when editing .tf files, without those rules appearing in unrelated Python or TypeScript sessions. What is the correct approach?",
  ["Create a CLAUDE.md file inside infra/ that contains the Terraform rules so they apply only within that subdirectory.",
   "Create a rules file in .claude/rules/terraform.md with YAML frontmatter specifying paths: ['infra/**/*'] and listing the Terraform conventions.",
   "Add the Terraform rules to the root CLAUDE.md under a clearly marked section, and instruct Claude in the system prompt to apply them only to .tf files.",
   "Create a skill in .claude/skills/terraform.md with allowed-tools restricted to file operations on the infra/ directory."],
  1,"The .claude/rules/ directory with YAML frontmatter path scoping is the correct mechanism for conditionally loading conventions. Setting paths: ['infra/**/*'] ensures the Terraform rules load only when editing files in that directory tree. Option A would work for files inside infra/ but cannot use glob patterns to further filter by file type. Option C relies on Claude's inference rather than explicit path matching. Option D requires manual skill invocation."),

q(38,'sc2','D2',
  "You've been assigned to restructure a monolithic application into microservices. This will involve changes across dozens of files and requires decisions about service boundaries and module dependencies. Which approach should you take?",
  ["Enter plan mode to explore the codebase, understand dependencies, and design an implementation approach before making changes.",
   "Start with direct execution and make changes incrementally, letting the implementation reveal the natural service boundaries.",
   "Use direct execution with comprehensive upfront instructions detailing exactly how each service should be structured.",
   "Begin in direct execution mode and only switch to plan mode if you encounter unexpected complexity during implementation."],
  0,"Plan mode is designed for complex tasks involving large-scale changes, multiple valid approaches, and architectural decisions. Option B risks costly rework when dependencies are discovered late. Option C assumes you already know the right structure without exploring the code. Option D ignores that the complexity is already stated."),

q(39,'sc2','D2',
  "A developer asks Claude Code to add a single null-check to one function in a utility module. The function signature, expected behavior, and fix are all clear. Should they use plan mode or direct execution?",
  ["Plan mode, because any code change could have unexpected side effects that need exploration before committing.",
   "Direct execution, because the task is well-scoped with a clear fix that does not require architectural decisions or multi-file analysis.",
   "Plan mode, because exploring the codebase first prevents Claude from making assumptions about dependencies.",
   "Use direct execution first, but run a quick plan mode scan afterward to catch any side effects before committing."],
  1,"Direct execution is appropriate for simple, well-understood, single-location changes with clear scope. Plan mode is designed for tasks involving large-scale changes, multiple valid approaches, architectural decisions, or multi-file modifications. A null-check to one function meets none of the criteria for plan mode. Option D inverts the correct workflow: plan mode is used before execution to explore and decide."),

q(40,'sc2','D2',
  "A developer is using plan mode to explore a large codebase before deciding how to approach a library migration. During exploration, Claude generates dozens of tool results including full file reads, search outputs, and dependency traces. The developer notices the main conversation context is filling up rapidly and fears context exhaustion before the plan is complete. What is the most appropriate technique to preserve main session context during verbose exploration?",
  ["Switch to direct execution partway through exploration so that Claude uses fewer tool calls.",
   "Use the Explore subagent to isolate verbose discovery output, having it return a structured summary to the main session rather than accumulating raw results.",
   "Run /compact immediately after each tool call to keep the context window from growing.",
   "Restrict Claude to reading only entry point files during plan mode to limit tool call volume."],
  1,"The Explore subagent is specifically designed to isolate verbose discovery work from the main conversation context. It performs the exploration and returns a structured summary, preventing raw tool results from consuming the main session's context budget. Option A abandons the architectural exploration prematurely. Option C helps but is operationally cumbersome and loses detail. Option D artificially limits the exploration and would produce an incomplete analysis."),

q(41,'sc2','D2',
  "A developer asks Claude Code to reformat date strings in a data pipeline. After the first attempt, the output format is partially correct but inconsistent: some dates are formatted as YYYY-MM-DD, others as MM/DD/YYYY. Prose instructions like 'always use ISO 8601' have been tried twice without improvement. What technique is most likely to resolve the inconsistency?",
  ["Rewrite the instruction to be more emphatic, using capitalization and repetition to signal importance.",
   "Provide 2-3 concrete input/output examples showing the exact transformation expected, including edge cases like two-digit years and ambiguous formats.",
   "Switch to plan mode so Claude can explore the codebase before formatting dates.",
   "Ask Claude to generate a formatting function first, then apply it in a second pass."],
  1,"Concrete input/output examples are the most effective way to communicate expected transformations when prose instructions are interpreted inconsistently. Showing '3/15/2024' -> '2024-03-15' is unambiguous in a way that 'use ISO 8601' is not. Option A is unlikely to improve results; emphasis does not resolve ambiguity. Option C is for architectural decisions. Option D adds complexity and still does not clarify what the correct transformation looks like."),

q(42,'sc2','D2',
  "A development team is using Claude Code to implement a new authentication module. Before any implementation begins, the team lead wants to ensure Claude surfaces potential security considerations, edge cases, and design tradeoffs that the team may not have anticipated. Which iterative refinement technique is most appropriate here?",
  ["Write a detailed specification document and pass it to Claude for direct implementation.",
   "Use the interview pattern: ask Claude to question the team about their requirements, constraints, and assumptions before proposing a design.",
   "Start with a minimal implementation and iterate by describing issues found during code review.",
   "Provide a complete test suite first and ask Claude to write code that passes all tests."],
  1,"The interview pattern is designed to surface design considerations and uncover assumptions the developer may not have anticipated before any implementation begins. It is particularly valuable in domains like security where overlooked edge cases carry high risk. Option A bypasses the opportunity to surface gaps before implementation is locked in. Option C defers the discovery of design issues until after implementation. Option D cannot surface considerations the team has not yet thought of."),

q(43,'sc2','D2',
  "Claude Code generated a data transformation function that has three separate issues: an off-by-one error in a loop, a missing null check for an optional field, and an incorrect sort order. Each issue is in a completely different part of the function and none of them interact. What is the recommended approach for addressing these issues?",
  ["Report all three issues in a single detailed message so Claude has full context for all fixes at once.",
   "Fix them sequentially: address each issue in a separate message and verify the fix before moving to the next.",
   "Ask Claude to regenerate the entire function from scratch rather than patching the existing code.",
   "Address the off-by-one error and null check together since they are in loops, then fix the sort order separately."],
  1,"When issues are independent, sequential iteration is appropriate: fixing each one separately and verifying the fix before moving on reduces the chance of fixes interfering with each other. The guidance for sending all issues in a single message applies when the issues interact. Option A is suited to interacting problems. Option C discards working code unnecessarily. Option D creates an arbitrary grouping not based on actual interaction."),

q(44,'sc2','D2',
  "A developer has identified three issues in a data processing module: two logic bugs that interact because they both affect the same intermediate result, and a set of five inconsistent variable names scattered across multiple files. The logic bugs produce incorrect output only when both are present; the naming violations are independent style issues. How should these issues be addressed using iterative refinement?",
  ["Report all eight issues in a single message so Claude can resolve them together with full context.",
   "Send the two interacting logic bugs in one message so Claude can resolve them together, then address the naming violations sequentially in separate follow-up messages after verifying the bug fixes.",
   "Fix all naming violations first since they are simpler, then tackle the two logic bugs in a single message.",
   "Fix each of the eight issues in eight separate sequential messages, verifying each before proceeding."],
  1,"The guidance for batching issues is based on whether they interact. The two logic bugs interact and Claude needs full context on both to resolve them correctly, so they should be reported together. The naming violations are independent, so sequential iteration is appropriate. Option A lumps all issues together, adding noise. Option C addresses ordering by complexity rather than interaction. Option D applies sequential iteration to interacting bugs, which risks an incomplete fix."),

q(45,'sc2','D2',
  "A team is adding a caching layer to an existing microservice. The service was written two years ago by engineers who are no longer on the team, and its internal patterns for dependency injection and lifecycle management are unfamiliar to the current developer. Before writing any code, the developer wants to ensure Claude surfaces all relevant design considerations. Which iterative refinement technique is most appropriate?",
  ["Ask Claude to implement a generic Redis-based caching layer using standard patterns for the framework, then review its output for compatibility issues.",
   "Use the interview pattern: ask Claude to question you about the service's architecture, existing lifecycle hooks, and caching requirements before proposing any design.",
   "Provide the service's entry point files to Claude and ask it to generate a caching design document for review.",
   "Start with a minimal proof-of-concept cache for one endpoint and iterate by describing any failures encountered during testing."],
  1,"The interview pattern is specifically designed for situations where the developer may not have anticipated all relevant design considerations. By asking Claude to question the developer about the service's patterns and constraints before implementing, it surfaces assumptions about lifecycle management and cache invalidation strategy. Option A proceeds with generic patterns that may be incompatible with the unfamiliar service. Option C produces a design document but does not interactively surface considerations the developer has not thought of. Option D defers discovery to runtime failures."),

q(46,'sc2','D3',
  "A developer generates a 300-line module using Claude Code in one session, then asks the same session to review the code for bugs. The review returns 'looks good' with minor style suggestions but misses two logic errors that a colleague catches in manual review. What is the most likely cause, and what architectural change addresses it?",
  ["The context window was too large; the fix is to limit code generation to smaller chunks so the review has less to process.",
   "The reviewing instance retains reasoning context from generation, making it less likely to question its own decisions. Use a second independent Claude instance without the generation context to perform the review.",
   "The review prompt was too vague; adding more explicit review criteria to the same session would catch the missed errors.",
   "The model tier used for generation is more capable than the one used for review; switching both to the same tier resolves the quality gap."],
  1,"Self-review limitation is a known pattern: when a model retains the reasoning context from code generation, it is less likely to identify errors in its own output. An independent review instance approaches the code without prior assumptions and catches issues the generating instance would overlook. Option A addresses context length, not reasoning context bias. Option C might improve detection of certain categories but does not address the fundamental self-review limitation. Option D addresses model selection, not the structural problem."),

q(47,'sc2','D3',
  "A developer builds a code generation pipeline where Claude generates a 200-line module, and then the same session reviews the generated code for correctness. The review returns only minor style suggestions and misses a logic error in the error handling path. A second developer reviewing the code manually finds the bug immediately. What architectural change would make the review phase more effective?",
  ["Add more explicit review criteria to the generation session's system prompt to help it catch logic errors.",
   "Use a second independent Claude instance without the generation context to perform the review, since the generating instance retains reasoning context that makes it less likely to question its own decisions.",
   "Run the review immediately after generation before any other tool calls accumulate in the context window.",
   "Switch to a larger model tier for the review step to improve reasoning quality."],
  1,"When a model reviews code it generated in the same session, it retains the reasoning context from generation and is less likely to identify errors in its own output. An independent review instance approaches the code without prior assumptions and catches issues the generating instance overlooks. This is the documented rationale for multi-instance review architectures. Option A improves the review prompt but does not address the fundamental self-review limitation. Option C manages context length but does not remove the generator's retained reasoning bias. Option D improves general capability but does not change the structural problem."),

# ── Scenario 4: Developer Productivity ────────────────────────────────────
q(48,'sc4','D1',
  "A developer productivity agent investigates bug reports by calling search_codebase, read_file, and run_tests. During a code review, a colleague proposes adding an iteration cap: if the loop has not finished after 15 tool calls, terminate with a generic 'investigation incomplete' response. What is the correct characterization of this design?",
  ["Iteration caps are the recommended primary stopping mechanism because they prevent runaway costs in production.",
   "Iteration caps are a reasonable safety boundary for long-running tasks but should not be the primary termination mechanism; stop_reason: 'end_turn' remains the authoritative signal.",
   "The iteration cap should be replaced with a time-based timeout, since token counts are a more reliable measure of completion than iteration count.",
   "Iteration caps are unnecessary if the system prompt instructs the agent to always request only the minimum tools needed."],
  1,"The agentic loop should terminate primarily when stop_reason equals 'end_turn', which signals that the model has finished its task. An iteration cap can serve as a safety guardrail against runaway loops, but treating it as the primary stopping mechanism means the loop may cut off legitimate multi-step investigations. Options A and C misstate recommended practice. Option D conflates prompt-based guidance with loop control."),

q(49,'sc4','D1',
  "A developer productivity agent has a PostToolUse hook that transforms raw Bash output. Currently the hook appends a formatted summary but also preserves the full raw output in the result passed to the model. Sessions exploring large codebases are hitting context limits faster than expected. What change would most effectively reduce unnecessary context consumption from tool results?",
  ["Disable the PostToolUse hook entirely and let the model process raw Bash output directly.",
   "Modify the hook to return only the formatted summary to the model, trimming the verbose raw output rather than preserving it alongside the summary.",
   "Increase the model's max_tokens parameter to accommodate the additional context from both raw and formatted output.",
   "Switch from PostToolUse hooks to pre-processing the Bash commands themselves to produce shorter output."],
  1,"PostToolUse hooks can trim verbose tool outputs to only the relevant data before the model processes them. Keeping both raw and summary output doubles the context consumption from each tool call. Modifying the hook to return only the formatted summary addresses the root cause directly. Option A removes normalization benefits. Option C increases output capacity but does not address the growing input context. Option D would require significant changes to tool invocation patterns."),

q(50,'sc4','D1',
  "An engineering team asks you to design a Claude-based system to investigate a production incident. The system must root-cause a bug that was introduced somewhere in the past two weeks across an unknown set of files and services. The scope of the investigation cannot be known in advance. Which decomposition approach is most appropriate?",
  ["Prompt chaining: design a fixed sequence of investigation steps (check logs, read configs, trace service calls) that the agent executes in order.",
   "Dynamic adaptive decomposition: the agent first maps the affected services and symptom timeline, then generates and prioritizes investigation subtasks based on what is discovered at each step.",
   "Split the investigation between two agents: one agent reads logs while the other reads source code, and they report findings independently to a human operator.",
   "Have the agent run a comprehensive search of all changed files in the past two weeks and produce a ranked list of candidates for manual review."],
  1,"Open-ended investigation tasks with unknown scope require dynamic adaptive decomposition, where the agent builds its investigation plan based on intermediate findings rather than following a fixed sequence. A static prompt chain cannot adapt when the investigation reveals unexpected service dependencies. Option A is appropriate for predictable multi-aspect reviews. Option C removes the coordinating intelligence. Option D is a single-pass heuristic."),

q(51,'sc4','D1',
  "A developer has been using Claude Code to investigate a legacy authentication service. After several hours, they have built up a detailed session with findings about the service's token validation logic. They need to step away and return tomorrow. Three core files in the authentication module will be modified overnight by another team. What is the most reliable approach for resuming the investigation productively the next day?",
  ["Resume the named session with --resume <session-name> and notify the agent about the specific files that were changed, so it can re-analyze those files in the context of its prior understanding.",
   "Start a completely new session each time, since stale tool results from the previous session make resumption unreliable for any scenario.",
   "Resume the named session without any notification about file changes; the agent will detect modifications automatically when it next reads those files.",
   "Use fork_session to create a branch of the current session before stepping away, then resume from the fork the next day."],
  0,"When resuming a session after code modifications, the correct approach is to use --resume <session-name> and explicitly inform the agent about which files changed so it can target re-analysis appropriately. Option B is overly conservative: when only a few known files changed, resumption with targeted context is more efficient. Option C is incorrect because the agent does not automatically detect file changes on resume. Option D misuses fork_session, which is designed for exploring divergent approaches."),

q(52,'sc4','D4',
  "Your team is setting up a shared GitHub MCP server for all engineers on a project. The server requires a GitHub API token for authentication. You want every engineer who clones the repository to have the MCP server available without each person having to manually configure it, and you want to avoid committing the actual token to version control. What is the correct configuration approach?",
  ["Add the MCP server to ~/.claude.json on each developer's machine with their personal token hardcoded.",
   "Add the MCP server to the project-scoped .mcp.json file with the token specified using environment variable expansion (e.g., ${GITHUB_TOKEN}), and commit .mcp.json to the repository.",
   "Add the MCP server configuration to the root CLAUDE.md file under a [mcp_servers] section.",
   "Create a setup script that each developer runs once to add the MCP server to their personal ~/.claude.json with their token."],
  1,"Project-scoped .mcp.json with environment variable expansion is the correct pattern for shared MCP servers: it is committed to the repository so all team members get the configuration automatically, and tokens are injected via environment variables at runtime rather than committed as plaintext. Option A requires manual per-person setup and hardcodes tokens. Option C describes a configuration mechanism that does not exist in CLAUDE.md. Option D also requires manual setup."),

q(53,'sc4','D4',
  "A developer productivity agent frequently makes multiple exploratory tool calls to discover what data sources are available in your MCP server before it can answer user questions. This pattern increases latency and consumes context for routine requests. What MCP feature most directly addresses this discovery overhead?",
  ["Add a list_tools meta-tool to the MCP server that returns all available tool names and descriptions.",
   "Expose content catalogs as MCP resources, giving the agent visibility into available data at connection time rather than through exploratory tool calls.",
   "Reduce the number of tools in the MCP server by merging similar tools together to minimize the discovery surface.",
   "Add a caching layer that stores the results of previous exploratory calls and reuses them across sessions."],
  1,"MCP resources are designed to expose content catalogs so agents know what data is available without making exploratory tool calls. This gives the agent upfront visibility at connection time, reducing the need for repeated discovery queries. Option A would still require a tool call to discover available resources. Option C reduces functionality to avoid a structural problem. Option D addresses symptom rather than cause."),

q(54,'sc4','D4',
  "A developer productivity agent needs to find all TypeScript files in a project that import from a deprecated module named legacy-auth. The project has thousands of files across many directories. Which combination of built-in tools is most appropriate for this task?",
  ["Use Bash to run find . -name '*.ts' and then Bash again to run grep on each file found.",
   "Use Glob to find all .ts files, then use Read to open each file and check whether it contains the import.",
   "Use Grep to search for the import pattern across all TypeScript files in the codebase.",
   "Use Read on the project root directory to get a file listing, then recursively Read each subdirectory."],
  2,"Grep is the correct built-in tool for searching file contents across a codebase. It efficiently searches all TypeScript files for the import pattern without requiring separate file enumeration. Option A uses Bash shell commands that should be replaced by dedicated tools when those tools are available. Option B uses Glob then Read on each file, which is far less efficient than Grep for a content search. Option D uses Read for directory traversal, which is not a supported use of that tool."),

q(55,'sc4','D4',
  "A developer productivity agent needs to update a configuration value in a file. The value appears in a block of code that contains several nearly identical lines. When the agent uses Edit, the tool returns an error: 'Match not unique: found 3 occurrences of the target text.' What is the correct fallback approach?",
  ["Use Bash to run a sed command to replace all occurrences of the target text simultaneously.",
   "Use Read to load the full file contents, identify the exact surrounding context needed to make the edit unique, and retry Edit with a larger old_string that uniquely identifies the correct location.",
   "Use Write to overwrite the entire file with a corrected version, based on the contents loaded by Read.",
   "Use Grep to locate the line number of each occurrence, then use Edit with a line number parameter to target the correct one."],
  1,"When Edit fails due to non-unique text, the correct first step is to use Read to examine the full file and find enough surrounding context to construct a unique old_string. This is more surgical than a full Write overwrite. Option C using Read+Write is a valid fallback but should only be used when Edit still cannot find a unique anchor. Option A uses Bash shell commands when built-in tools should be preferred. Option D describes a line number parameter that Edit does not support."),

q(56,'sc4','D5',
  "An agent is performing a deep exploration of a 200,000-line legacy codebase to understand its payment processing flow. After approximately 90 minutes and dozens of file reads, the agent begins referencing 'standard patterns in payment systems' rather than the specific classes and flows it found earlier, and its answers become inconsistent with findings from the first hour. What is the most likely cause and the best mitigation strategy?",
  ["The agent has reached a rate limit; the fix is to add delays between tool calls to stay within limits.",
   "Context degradation: as the session grows, specific findings from early in the session compete with general knowledge and the agent's position-attention effects. Mitigate by having the agent maintain a scratchpad file recording key findings throughout the session.",
   "The legacy codebase's file structure is too complex for a single agent; break it into independent subsystems and run separate agents on each subsystem simultaneously.",
   "The agent is using the wrong tools; switching from Read to Grep for file exploration would reduce context consumption."],
  1,"Context degradation in extended sessions is a known pattern: models start giving inconsistent answers and referencing general knowledge rather than specific findings discovered earlier. Having the agent maintain a scratchpad file that records key findings creates a persistent, explicit record that can be referenced in subsequent prompts. Option A misidentifies the cause. Option C adds parallelism but does not address single-session degradation. Option D changes tooling but does not address context growth."),

q(57,'sc4','D5',
  "You are running a multi-phase codebase investigation using the Claude Agent SDK. After 45 minutes of exploration you move into the second phase: identifying security vulnerabilities in the authentication module. You notice the agent is now describing the authentication module as 'using standard JWT patterns' when earlier in the session it had found a custom token signing implementation. What technique would most effectively preserve key findings across these phase boundaries?",
  ["Have the agent maintain a scratchpad file that records key findings after each phase, and reference that file at the start of subsequent phases rather than relying on conversation history.",
   "Use /compact before starting the second phase to free up context space and allow the agent to re-read files as needed.",
   "Restart the session with a fresh context at the start of each phase, passing a manual summary of what you found.",
   "Increase the max_tokens parameter so the model can hold more context without compressing earlier findings."],
  0,"Scratchpad files are the recommended technique for persisting key findings across context boundaries when context degradation becomes apparent. The agent can write structured notes during exploration and read them back at phase boundaries, ensuring critical findings like the custom token signing implementation are not lost. Option B uses /compact, which compresses conversation history and may lose the specific finding. Option C is a valid but costly approach. Option D is incorrect because max_tokens controls output length, not context window size."),

# ── Scenario 5: CI/CD ────────────────────────────────────────────────────
q(58,'sc5','D2',
  "Your pipeline script runs claude 'Analyze this pull request for security issues' but the job hangs indefinitely. Logs indicate Claude Code is waiting for interactive input. What's the correct approach?",
  ["Add the -p flag: claude -p 'Analyze this pull request for security issues'",
   "Set the environment variable CLAUDE_HEADLESS=true before running the command.",
   "Redirect stdin from /dev/null: claude 'Analyze this pull request for security issues' < /dev/null",
   "Add the --batch flag: claude --batch 'Analyze this pull request for security issues'"],
  0,"The -p (or --print) flag is the documented way to run Claude Code in non-interactive mode. Options B and D reference non-existent features. Option C is a Unix workaround that does not properly address Claude Code's command syntax."),

q(59,'sc5','D2',
  "A CI pipeline runs Claude Code to generate test cases for each pull request. The team discovers that Claude is consistently suggesting test scenarios that already exist in the existing test files, wasting review time. Which approach in the CLAUDE.md configuration most directly addresses this problem?",
  ["Add the -p flag to the CI invocation command to prevent interactive prompts.",
   "Use --output-format json with --json-schema so that test suggestions are machine-parseable for deduplication.",
   "Document in CLAUDE.md the testing standards, available fixtures, and instruct Claude to review existing test files before suggesting new scenarios.",
   "Add a post-processing script to the pipeline that compares Claude's suggestions against the existing test files and filters duplicates."],
  2,"Providing existing test files in context and documenting testing standards in CLAUDE.md directly instructs Claude to avoid duplicate suggestions at generation time. This addresses the root cause: Claude does not know what tests already exist. Option A prevents interactive hangs but does not affect test content. Option B improves parseability but does not prevent duplicate suggestions. Option D is a workaround that adds pipeline complexity without fixing the underlying issue."),

q(60,'sc5','D2',
  "A CI pipeline uses Claude Code to review pull requests and needs to post inline comments on specific lines in GitHub. The pipeline currently receives Claude's output as unstructured text, which requires a fragile regex parser to extract file paths, line numbers, and comment text. The parser breaks regularly as Claude's output format drifts between runs. What is the most robust solution?",
  ["Add stricter formatting instructions to the system prompt specifying the exact text structure expected, and add validation to reject any response that does not match.",
   "Use --output-format json combined with --json-schema to define a schema with file, line, and comment fields, so each finding is machine-parseable by construction.",
   "Add a post-processing step that uses a second Claude call to normalize the first response into a consistent structured format.",
   "Switch from inline comments to a single summary comment, which is easier to extract since it does not require line-level parsing."],
  1,"Using --output-format json with --json-schema produces structured output that conforms to the defined schema by construction, eliminating format drift entirely. Option A makes prompt instructions more rigid but still relies on Claude maintaining format consistency across runs, which is the root cause of the breakage. Option C adds latency and cost. Option D changes the feature behavior to work around the parsing problem."),

q(61,'sc5','D1',
  "You are building an automated code review system using Claude. The review must cover three aspects for every pull request: security vulnerabilities, style compliance, and performance implications. Each aspect has clear, defined criteria documented in your engineering handbook. Which decomposition strategy is most appropriate?",
  ["Dynamic adaptive decomposition: have the agent start by scanning the full PR and generate a review plan based on what it finds.",
   "Prompt chaining with sequential focused passes: one pass per review aspect (security, style, performance), each with dedicated criteria.",
   "A single comprehensive pass that examines all three aspects simultaneously to capture cross-cutting concerns.",
   "Spawn three fully independent agents without shared context, then merge their outputs in a final aggregation step."],
  1,"When a workflow has predictable, well-defined aspects that must each be covered, prompt chaining with sequential focused passes is the appropriate pattern. Each pass dedicates full attention to one concern rather than dividing attention across all three. Option A uses dynamic decomposition for a workflow whose structure is already known. Option C suffers from attention dilution. Option D loses cross-file integration context."),

q(62,'sc5','D3',
  "A CI code review prompt flags 60% of pull requests for 'potential security vulnerabilities.' Developers have stopped reading the reports because nearly all flags are false positives on standard input validation patterns they consider acceptable. Adding 'only report high-confidence findings' to the prompt has had no measurable effect. What is the most effective next step?",
  ["Replace the security review prompt with a rule-based static analysis tool that has zero false positives.",
   "Temporarily disable the security category and add explicit criteria defining which patterns constitute a reportable vulnerability versus acceptable practice, with concrete code examples for each.",
   "Increase the review model to a larger tier to improve its judgment on security issues.",
   "Add a post-processing confidence threshold: discard any finding where Claude rates its own confidence below 80%."],
  1,"General instructions like 'only report high-confidence findings' fail to reduce false positives because they do not define what counts as a positive. Temporarily disabling the noisy category restores developer trust immediately while explicit criteria with examples give Claude the specificity needed to distinguish real issues from acceptable patterns. Option A abandons the AI-based review entirely. Option C is unlikely to change false positive rates when the root cause is imprecise criteria. Option D relies on poorly calibrated self-reported confidence scores."),

q(63,'sc5','D3',
  "A Claude-based pull request reviewer raises 'magic number' warnings on every numeric literal in the codebase, including well-understood constants like HTTP status codes and standard buffer sizes. Developers want magic numbers flagged only when they appear in business logic with no explanation. How should the prompt be updated?",
  ["Add an instruction to 'use good judgment about whether numbers are truly magic numbers.'",
   "Define explicit criteria: flag numeric literals that appear in business logic calculations with no accompanying comment or named constant; exclude HTTP status codes, standard buffer sizes, and any value documented in a comment.",
   "Add a severity field to findings and instruct Claude to omit any finding with severity 'low.'",
   "Provide a list of allowed numeric values that should never be flagged."],
  1,"Explicit, specific criteria that define what to report and what to exclude are far more effective than general guidance or exclusion lists. Describing the precise conditions that make a number 'magic' gives Claude a clear decision rule rather than requiring inference. Option A is the kind of vague instruction that causes the problem in the first place. Option C introduces a severity layer that does not address the underlying definitional problem. Option D requires maintaining an incomplete and fragile list."),

q(64,'sc5','D3',
  "A Claude-based code reviewer is generating inconsistent feedback on documentation quality: sometimes flagging missing docstrings for private helper functions, sometimes not; sometimes requiring full parameter descriptions, sometimes accepting one-line summaries. The team wants consistent, predictable documentation feedback on public API functions only. Which change most directly addresses the inconsistency?",
  ["Instruct Claude to 'apply documentation standards consistently and carefully.'",
   "Define explicit documentation criteria: public API functions must have a docstring with a one-sentence summary, parameter descriptions, and return value description; private functions are excluded from documentation checks.",
   "Run three parallel review instances and accept feedback that appears in at least two of the three.",
   "Restrict the review prompt to only one concern at a time, alternating between security, documentation, and style in separate runs."],
  1,"Explicit criteria that specify exactly what is required, for which functions, and at what level of detail eliminate the ambiguity that causes inconsistency. Without a clear definition of 'documented,' Claude must infer the threshold each time, leading to variable results. Option A is the type of general instruction that already produces the problem. Option C adds overhead and suppresses legitimate feedback. Option D separates concerns but does not fix the definition of what counts as adequate documentation."),

q(65,'sc5','D3',
  "A team uses Claude to generate code review comments for pull requests. The comments are technically accurate but vary widely in format: some include file paths and line numbers, others are vague summaries, some use bullet points, and others write prose paragraphs. Developers want a consistent, actionable format: file path, line number, issue description, suggested fix. What is the most effective way to achieve this?",
  ["Add a format specification to the system prompt listing the required fields.",
   "Provide 2-4 few-shot examples in the prompt showing the exact desired output format for different types of issues, including file path, line number, issue description, and suggested fix.",
   "Use --output-format json and parse the results in a post-processing step to normalize format.",
   "Ask Claude to self-review its output and reformat any comment that does not match the required structure."],
  1,"Few-shot examples demonstrating the exact desired output format are the most effective technique for achieving consistently formatted output when detailed instructions alone produce inconsistent results. Seeing concrete examples of the format makes the requirement unambiguous. Option A is a format specification that has likely already been tried. Option C introduces parsing complexity and does not ensure consistent generation. Option D adds a round-trip that may still produce inconsistent intermediate output."),

q(66,'sc5','D3',
  "A CI code review pipeline is generating false positive findings at a high rate. The team wants to understand which specific code constructs are being flagged incorrectly so they can refine the prompt. The current findings output only includes file, line, and description. What schema change would best enable systematic false positive analysis?",
  ["Add a confidence field (0-100) to each finding so the team can filter by confidence threshold.",
   "Add a detected_pattern field to each finding that records the specific code construct or pattern that triggered the finding.",
   "Add a category field so findings can be grouped by issue type for aggregate analysis.",
   "Add an is_false_positive boolean field and instruct Claude to self-label its own false positives."],
  1,"The detected_pattern field directly captures what code construct triggered each finding, enabling the team to identify which patterns produce the most false positives and update prompt criteria accordingly. Option A provides confidence scores but does not identify what prompted the finding. Option C allows grouping but not pattern-level debugging. Option D asks Claude to self-identify its own false positives, which is unreliable."),

q(67,'sc5','D3',
  "A pull request modifies 14 files across the stock tracking module. Your single-pass review produces inconsistent results: detailed feedback for some files, superficial comments for others, obvious bugs missed, and contradictory feedback. How should you restructure the review?",
  ["Split into focused passes: analyze each file individually for local issues, then run a separate integration-focused pass examining cross-file data flow.",
   "Require developers to split large PRs into smaller submissions of 3-4 files before the automated review runs.",
   "Switch to a higher-tier model with a larger context window to give all 14 files adequate attention in one pass.",
   "Run three independent review passes on the full PR and only flag issues that appear in at least two of the three runs."],
  0,"Splitting reviews into focused passes directly addresses attention dilution. Option B shifts burden to developers without improving the system. Option C misunderstands that larger context windows do not solve attention quality issues. Option D would suppress detection of real bugs by requiring consensus on issues that may only be caught intermittently."),

# ── Scenario 6: Structured Data Extraction ────────────────────────────────
q(68,'sc6','D3',
  "Your team wants to reduce API costs. Two workflows: (1) a blocking pre-merge check that must complete before developers can merge, and (2) a technical debt report generated overnight for review the next morning. Your manager proposes switching both to the Message Batches API for 50% cost savings. How should you evaluate this proposal?",
  ["Use batch processing for the technical debt reports only; keep real-time calls for pre-merge checks.",
   "Switch both workflows to batch processing with status polling to check for completion.",
   "Keep real-time calls for both workflows to avoid batch result ordering issues.",
   "Switch both to batch processing with a timeout fallback to real-time if batches take too long."],
  0,"The Message Batches API has up to 24-hour processing times with no guaranteed latency SLA. This makes it unsuitable for blocking pre-merge checks but ideal for overnight batch jobs. Option B is wrong because relying on 'often faster' completion is not acceptable for blocking workflows. Option C reflects a misconception: batch results can be correlated using custom_id fields. Option D introduces unnecessary complexity."),

q(69,'sc6','D3',
  "A structured data extraction system is extracting contract clauses from legal documents. The model handles standard clauses well but consistently misclassifies ambiguous clauses that could fit two or more categories, such as a clause that contains both termination conditions and force majeure language. What few-shot prompting approach is most effective for improving accuracy on these edge cases?",
  ["Add more few-shot examples of standard, unambiguous clauses to reinforce the classification schema overall.",
   "Create targeted few-shot examples that specifically demonstrate ambiguous-case handling: showing the reasoning for why a clause with both termination and force majeure language belongs to one category and not the other.",
   "Switch from classification to extraction: ask Claude to extract the clause text without categorizing it, then apply a rule-based classifier.",
   "Add a confidence score field and route all low-confidence classifications to human review without attempting to improve the model's judgment."],
  1,"Targeted few-shot examples for ambiguous scenarios that show the reasoning behind the classification decision are the most effective technique for improving handling of edge cases. Standard examples do not teach the model how to handle cases that span category boundaries. Option A reinforces behavior that already works rather than addressing the gap. Option C sidesteps the classification problem. Option D is a reasonable operational safeguard but does not improve model accuracy."),

q(70,'sc6','D3',
  "A document extraction system uses Claude to pull financial figures from quarterly earnings reports. The reports have varied formats: some use tables, some use inline prose, some use both. Extraction accuracy for tabular data is high (94%) but prose-only documents show only 72% accuracy. What is the most targeted approach to improve prose extraction accuracy?",
  ["Increase the system prompt's emphasis on accuracy with stronger language and more detailed instructions.",
   "Add few-shot examples specifically showing correct extraction from prose-formatted documents, including cases where numbers appear in sentence form rather than tables.",
   "Pre-process all documents to convert prose financial data into table format before sending to Claude.",
   "Use a separate prompt for prose documents that instructs Claude to first identify all sentences containing numbers, then extract figures from those sentences only."],
  1,"Few-shot examples demonstrating correct extraction from documents with varied formats directly address the accuracy gap on prose documents. The model already generalizes well to tabular data; the gap is in prose, and targeted examples for that format close the gap most efficiently. Option A relies on emphasis, which does not resolve structural pattern differences. Option C requires reliable pre-processing of arbitrarily structured prose. Option D adds complexity and may miss numbers."),

q(71,'sc6','D3',
  "Your extraction pipeline uses a prompt that requests JSON output with a code block. In production, approximately 3% of responses have JSON syntax errors: missing commas, unescaped characters, or truncated objects. These errors break your downstream parser and require manual reprocessing. What is the most reliable way to eliminate JSON syntax errors?",
  ["Add a validation step that re-runs the prompt if the output fails JSON parsing, up to 3 retries.",
   "Switch to tool use with a defined JSON schema as the input parameter; extract structured data from the tool_use response block.",
   "Add an instruction to the prompt: 'Your response must be valid JSON. Double-check for syntax errors before responding.'",
   "Use a regex post-processor to fix the most common syntax errors before passing output to the parser."],
  1,"Tool use with a JSON schema guarantees schema-compliant structured output by construction, eliminating syntax errors entirely. The model populates the tool call's input parameters according to the schema rather than generating free-text JSON. Option A reduces the frequency of failures but does not eliminate syntax errors. Option C relies on model self-checking, which does not provide the deterministic guarantee that tool use provides. Option D is a fragile workaround."),

q(72,'sc6','D3',
  "Your structured data extraction pipeline processes invoices. You have two extraction tools: extract_invoice_schema and extract_receipt_schema. For each document, you do not know in advance which type it is. After switching to tool_choice: 'auto', you observe that 30% of the time the model returns a text description of what it found rather than calling either tool. What is the correct fix?",
  ["Set tool_choice: 'any' to guarantee the model calls one of the available extraction tools without specifying which one.",
   "Set tool_choice: {type: 'tool', name: 'extract_invoice_schema'} to always call a specific tool.",
   "Add a system prompt instruction: 'Always call one of the extraction tools and never return text.'",
   "Merge both schemas into a single extract_document_schema tool with an optional document_type field."],
  0,"tool_choice: 'any' guarantees the model calls a tool rather than returning conversational text, without requiring you to specify which tool. This is exactly the documented use case when you have multiple valid tools and want to ensure one is called. Option B forces a specific tool, which defeats the purpose when you do not know the document type in advance. Option C is a prompt-based approach with probabilistic compliance, which already failed. Option D is a valid architectural change but requires more engineering effort."),

q(73,'sc6','D3',
  "An invoice extraction pipeline uses tool use with a strict JSON schema. After validation, 8% of extracted invoices fail a business rule check: the sum of line item amounts does not equal the total_amount field. These are semantic errors, not schema syntax errors. The invoices are well-formed documents with no missing data. How should you implement the retry loop?",
  ["Retry up to 3 times with the same prompt; schema-compliant extraction will converge on a valid answer with additional attempts.",
   "On failure, append the original document, the failed extraction, and the specific validation error ('line items sum to X but total_amount is Y') to the follow-up prompt for model self-correction.",
   "Flag all invoices with this error as missing data and route them directly to human review without retry.",
   "Add a calculated_total field to the schema and populate it with the sum of line items in post-processing, then use the calculated total as the canonical value."],
  1,"Retry-with-error-feedback works by giving the model the specific discrepancy it needs to self-correct. Since the invoices are well-formed and the data is present, the model has the information it needs to fix the arithmetic alignment on retry. Option A retries without feedback and is unlikely to improve results. Option C routes to human review prematurely. Option D silently replaces the model's extracted total with a calculated value, which could propagate errors if line items were also extracted incorrectly."),

q(74,'sc6','D3',
  "A compliance team runs a weekly audit that analyzes 50,000 contract documents for regulatory clauses. The audit results are reviewed by a compliance analyst every Monday morning. The team is considering the Message Batches API. A colleague raises a concern: 'What if a batch fails partway through the 50,000 documents?' How should partial batch failures be handled?",
  ["Always resubmit the entire batch; tracking partial failures adds implementation complexity.",
   "Use the custom_id field to correlate each request with its response, identify which documents returned error responses, and resubmit only those documents in a new batch.",
   "Set a shorter processing window timeout to force faster completion and reduce the risk of partial failures.",
   "Switch to real-time API calls with retry logic; the batch API is not suitable for mission-critical compliance workloads."],
  1,"The custom_id field is specifically designed for correlating batch request and response pairs, enabling teams to identify which documents failed and resubmit only those, avoiding the cost of reprocessing the entire batch. Option A wastes 50% cost savings by reprocessing successful documents. Option C misunderstands the batch API; processing windows are managed by Anthropic. Option D is overly conservative: the batch API is appropriate for non-blocking, latency-tolerant compliance audits."),

q(75,'sc6','D5',
  "A financial document extraction pipeline is failing on the 'guarantor address' field for a set of loan summaries. After 3 retry attempts with error feedback, the field still extracts as null. Each retry prompt includes the original document and the validation error. What should you investigate before scheduling further retries?",
  ["Increase the retry limit from 3 to 5, since complex field extraction may require more attempts to converge.",
   "Check whether the guarantor address is actually present in the loan summary document, or whether the document only references it by directing the reader to an external exhibit.",
   "Switch to a larger model tier for the retry attempts, since the current model may lack the reasoning capacity for this field.",
   "Restructure the schema to make the guarantor address field optional, allowing the pipeline to proceed when the field cannot be extracted."],
  1,"Retries are only effective when the information needed to satisfy the validation is present in the document. A loan summary that references guarantor details in an external exhibit does not contain the address. No number of retries will extract information that is not in the input. Before adding retry cycles, validate that the target field is actually present in the source document. Option A adds more retries without diagnosing why existing retries are failing. Option C may improve performance but does not address absence of data. Option D removes the validation rather than diagnosing the root cause."),

q(76,'sc6','D5',
  "A structured data extraction system for insurance claims achieves 97% overall accuracy on a validation set. The team proposes automating the full workflow without human review. A colleague argues this aggregate metric masks important risks. What is the most important concern?",
  ["97% accuracy means 3% of claims will have errors, which could create legal liability if unchecked.",
   "Aggregate accuracy metrics can mask poor performance on specific document types or fields. A claim type or field category with 85% accuracy would be hidden by strong performance elsewhere, and stratified analysis is needed before automating.",
   "The validation set may not be representative of production data volumes, so the 97% figure cannot be trusted.",
   "Human review should always be retained regardless of accuracy metrics because automation of insurance decisions creates regulatory risk."],
  1,"The core risk is that aggregate metrics can hide poor performance on specific segments. A document type with 85% accuracy on a critical field like claim_amount would be masked by strong performance across other document types. Before automating, accuracy should be validated by document type and field segment. Option A is a valid concern but describes the error rate, not the masking risk. Option C raises a data quality concern but is not the most important concern. Option D makes a policy argument that does not engage with the analytical gap identified."),

q(77,'sc6','D5',
  "An extraction pipeline achieves high accuracy on average but the team wants to implement confidence-based routing: high-confidence extractions proceed automatically while low-confidence ones go to human review. A developer proposes using the model's stated confidence scores directly as the routing threshold. What is the critical flaw in this approach?",
  ["Confidence scores add tokens to every response, increasing API costs unnecessarily.",
   "Model confidence scores must be calibrated against a labeled validation set to determine what score threshold actually corresponds to acceptable accuracy. Uncalibrated raw scores are not reliable predictors of extraction correctness.",
   "Confidence scores only work when the model outputs a single extraction; multi-field documents require a different approach.",
   "Routing on confidence scores creates two separate code paths that are harder to maintain than a single uniform review workflow."],
  1,"A model's raw confidence scores need calibration: without comparing stated confidence against actual correctness on a labeled validation set, there is no reliable mapping between a score of '0.85' and an acceptable error rate. Calibrating the threshold ensures that the routing cut-off corresponds to a known accuracy level. Option A is a minor operational concern. Option C is incorrect; confidence scores can be applied at the field level. Option D is an engineering tradeoff, not a flaw in the confidence approach itself."),
]

assert len(EXQDB) == 77, f'Expected 77 questions, got {len(EXQDB)}'

# ── Build new EXQDB JS ─────────────────────────────────────────────────────
new_exqdb = '  var EXQDB = ' + json.dumps(EXQDB, ensure_ascii=False, indent=2) + ';\n\n'

# ── Read file ──────────────────────────────────────────────────────────────
with open(HTML, 'r', encoding='utf-8') as f:
    content = f.read()

# ── Replace 1: EXQDB block ─────────────────────────────────────────────────
start_marker = '  var EXQDB = ['
end_marker   = '  /* ── Public API'
si = content.find(start_marker)
ei = content.find(end_marker, si)
assert si != -1 and ei != -1
content = content[:si] + new_exqdb + content[ei:]

# ── Replace 2: Fix hardcoded /60 in buildResults ───────────────────────────
content = content.replace('Math.round((correct/60)*100)', 'Math.round((correct/EXQDB.length)*100)')
content = content.replace("el.textContent=correct+'/60'", "el.textContent=correct+'/'+EXQDB.length")
content = content.replace("answers.filter(a=>a!==null).length+'/60 answered'", "answers.filter(a=>a!==null).length+'/'+EXQDB.length+' answered'")
content = content.replace('total:60,scaled', 'total:EXQDB.length,scaled')

# ── Replace 3: Exam start screen ───────────────────────────────────────────
content = content.replace(
    '60 questions &middot; 120 minutes &middot; scaled 100&ndash;1000 &middot; pass at 720',
    '77 questions &middot; 120 minutes &middot; scaled 100&ndash;1000 &middot; pass at 720'
)
content = content.replace(
    '<div style="font-family:var(--ffd);font-size:22px;color:var(--g1)">60</div><div style="font-size:10px;color:var(--ink4);font-weight:600;margin-top:2px">Questions</div>',
    '<div style="font-family:var(--ffd);font-size:22px;color:var(--g1)">77</div><div style="font-size:10px;color:var(--ink4);font-weight:600;margin-top:2px">Questions</div>'
)
content = content.replace(
    '&bull; Timer counts down from 120:00 &mdash; pace yourself (~2 min per question)',
    '&bull; Timer counts down from 120:00 &mdash; pace yourself (~90 sec per question)'
)

# ── Replace 4: UCS array ───────────────────────────────────────────────────
new_ucs = r"""const UCS=[
  // HOOKS & ENFORCEMENT
  {cat:'hooks',q:'Refunds over $500 bypass manager approval ~3% of the time despite system prompt rules.',ans:'Implement a PreToolUse hook on process_refund that checks the amount and blocks or redirects when > $500.',why:'Business rules that must always apply require programmatic enforcement — system prompts are probabilistic.'},
  {cat:'hooks',q:'A mandatory identity verification step before account closure is skipped occasionally.',ans:'Add a programmatic prerequisite that blocks close_account until get_customer returns a verified customer ID.',why:'Tool ordering for critical workflows must be enforced in code, not in the prompt.'},
  {cat:'hooks',q:'You need 100% audit coverage of every tool execution in a financial agent.',ans:'Add a PostToolUse hook that writes to an audit log after every tool call.',why:'PostToolUse hooks run after every tool call — coverage is guaranteed regardless of Claude\'s reasoning.'},
  {cat:'hooks',q:'process_refund returns isError: true for fraud blocks but the agent retries it 3x, flooding the compliance system.',ans:'Add isRetryable: false to the fraud block error response to signal this is a permanent business rule block, not a transient failure.',why:'Structured error metadata with isRetryable prevents futile retries. The agent needs to distinguish transient vs. permanent errors.'},
  {cat:'hooks',q:'Three backend systems return different date formats and status codes. The agent misinterprets them.',ans:'Implement PostToolUse hooks that normalize each tool\'s output into a consistent format before the model processes it.',why:'PostToolUse hooks intercept results before the model sees them — the right place for format normalization.'},
  {cat:'hooks',q:'A web search subagent returns empty results with status: success when the API is down.',ans:'Use the isError flag to distinguish access failures from valid empty-result responses.',why:'Silently returning success for failures prevents the coordinator from making any recovery decision.'},

  // ARCHITECTURE
  {cat:'arch',q:'Agentic loop keeps checking Claude\'s response text for "I have completed" to stop. What\'s wrong?',ans:'Check stop_reason instead. Terminate when stop_reason === "end_turn"; continue when stop_reason === "tool_use".',why:'Natural language signals in response text are unreliable. stop_reason is the authoritative loop control signal.'},
  {cat:'arch',q:'A research coordinator covers only visual arts even though the topic is "all creative industries".',ans:'Fix the coordinator\'s task decomposition logic — it assigned only visual arts subtasks.',why:'Systematic output gaps trace to coordinator decomposition logic, not subagent execution quality.'},
  {cat:'arch',q:'3 independent subtopics need researching in parallel. How should the coordinator spawn subagents?',ans:'Emit all three Task tool calls in a single coordinator response to allow parallel execution.',why:'The Claude Agent SDK runs multiple Task calls emitted in one response in parallel — the key to throughput.'},
  {cat:'arch',q:'A coordinator can\'t spawn subagents even though it has web_search and read_document in allowedTools.',ans:"Add 'Task' to the coordinator's allowedTools. The Task tool is required to spawn subagents.",why:"The Task tool is the only mechanism for spawning subagents. It must be explicitly listed in allowedTools."},
  {cat:'arch',q:'Synthesis agent consistently omits middle sections of the aggregated findings.',ans:'Place key findings summaries at the beginning of aggregated inputs and use explicit section headers.',why:'"Lost in the middle" — models attend less reliably to content in the middle of long inputs.'},
  {cat:'arch',q:'You want to explore two divergent architectural approaches from the same analysis baseline.',ans:'Use fork_session to create two independent branches from the current session.',why:'fork_session is the mechanism for divergent exploration from a shared baseline without contaminating either branch.'},
  {cat:'arch',q:'Session resumed after overnight file changes. Agent refers to outdated findings.',ans:'Use --resume <session-name> and explicitly notify the agent about which files changed for re-analysis.',why:'The agent does not detect file changes automatically on resume. You must provide that context.'},

  // CLAUDE CODE (D3 in exam guide)
  {cat:'code',q:'Shared team coding standards are in ~/.claude/CLAUDE.md but new teammates don\'t see them.',ans:'Move standards to the project-level CLAUDE.md at the repo root, which is version-controlled and shared.',why:'~/.claude/CLAUDE.md is user-scoped and never committed to version control.'},
  {cat:'code',q:'A 400-line monorepo CLAUDE.md applies wrong conventions to wrong file types.',ans:'Split into .claude/rules/ files with YAML path-scoped frontmatter so each rule set activates only for matching files.',why:'.claude/rules/ with glob patterns conditionally loads rules — the fix for monolithic config bleed.'},
  {cat:'code',q:'A /scaffold skill produces hundreds of lines of intermediate output that pollutes the main session.',ans:"Set context: fork in the skill's frontmatter to run it in an isolated sub-agent.",why:'context: fork isolates all exploratory output in the fork. Only the final result returns to the main session.'},
  {cat:'code',q:'Test files are spread throughout the codebase and need consistent conventions regardless of location.',ans:'Create a .claude/rules/ file with glob pattern **/*.test.tsx (or similar) in the YAML frontmatter.',why:'.claude/rules/ with glob patterns matches files by path pattern regardless of directory location.'},
  {cat:'code',q:'Monolithic to microservices migration across dozens of files — plan mode or direct execution?',ans:'Plan mode. Explore dependencies and design service boundaries before making any changes.',why:'Plan mode is for large-scale changes, architectural decisions, and tasks where the scope is not fully known upfront.'},
  {cat:'code',q:'Simple null-check to one function — plan mode or direct execution?',ans:'Direct execution. The task is well-scoped with a clear fix and no architectural decisions required.',why:'Plan mode adds overhead with no benefit for well-understood, single-location changes.'},
  {cat:'code',q:'Three independent function bugs — address together or separately?',ans:'Sequentially: fix each in a separate message, verify before moving to the next.',why:'Independent issues should be fixed sequentially. Batch only when issues interact and Claude needs context on both.'},
  {cat:'code',q:'Two interacting logic bugs that only manifest together + 5 unrelated naming violations.',ans:'Send the two interacting bugs in one message (they need joint context). Fix naming violations sequentially after.',why:'Batching is for interacting issues. Independent issues are better handled one at a time.'},
  {cat:'code',q:'You want Claude to surface security edge cases before implementing an auth module.',ans:'Use the interview pattern: ask Claude to question the team about requirements and assumptions before any design.',why:'The interview pattern surfaces considerations the developer hasn\'t thought of yet — valuable before implementation.'},

  // PROMPT ENGINEERING (D4 in exam guide)
  {cat:'prompt',q:'Claude returns valid JSON 97% of the time but 3% have syntax errors that break the pipeline.',ans:'Switch to tool use with a JSON schema. Tool use produces schema-compliant output by construction, eliminating syntax errors.',why:'Tool use enforces schema compliance deterministically. Retry loops and instructions still leave a failure rate.'},
  {cat:'prompt',q:'tool_choice: auto results in 30% text responses instead of tool calls for invoice/receipt extraction.',ans:"Set tool_choice: 'any' to guarantee a tool call without specifying which tool.",why:"tool_choice: 'any' ensures one of the available tools is called. 'auto' allows the model to skip all tools."},
  {cat:'prompt',q:'Contract clause classifier handles standard clauses well but misclassifies ambiguous edge cases.',ans:'Add targeted few-shot examples showing ambiguous-case reasoning: why a clause with two possible categories belongs to one.',why:'Standard examples reinforce behavior that already works. Edge case examples teach boundary behavior.'},
  {cat:'prompt',q:'Validation-retry loop for semantic errors (line items don\'t sum to total_amount).',ans:'On failure, append the original document + failed extraction + specific error message to the retry prompt.',why:'Retry-with-error-feedback gives the model the exact discrepancy it needs to self-correct.'},
  {cat:'prompt',q:'After 3 retries with error feedback, a field still extracts as null.',ans:'Check if the field is actually present in the document — it may be in an external exhibit not included in the input.',why:'Retries only work when the information is present. No number of retries will extract missing data.'},
  {cat:'prompt',q:'Blocking pre-merge check AND overnight tech-debt report — can both use the Batch API?',ans:'No. Only the overnight report. Pre-merge checks must complete in real time — batch has up to 24h latency.',why:'Batch API has no latency guarantee. Never use it for user-facing or blocking workflows.'},
  {cat:'prompt',q:'CI review flags 60% of PRs as security vulnerabilities — mostly false positives.',ans:'Temporarily disable the category. Add explicit criteria defining reportable vulnerability vs. acceptable practice with concrete code examples.',why:'Vague instructions like "high confidence only" don\'t reduce false positives. Explicit criteria with examples do.'},
  {cat:'prompt',q:'Code review comments vary in format — some have file/line/fix, others are vague summaries.',ans:'Provide 2-4 few-shot examples showing the exact desired format: file path, line number, issue description, suggested fix.',why:'Few-shot examples are more effective than format specifications when format drift is already occurring.'},

  // MCP & TOOLS
  {cat:'mcp',q:'Agent calls get_customer for order queries instead of lookup_order — both have similar descriptions.',ans:'Expand each tool\'s description to include input formats, example queries, and explicit scope exclusions.',why:'Tool selection is purely description-driven. Fix the description first, not the system prompt.'},
  {cat:'mcp',q:'Three tools named get_account_info, fetch_account_details, retrieve_customer_record all cause misrouting.',ans:'Rename each tool to reflect its distinct data source and rewrite descriptions to explain what data each returns.',why:'Overlapping names and descriptions cause misrouting. Distinct names + clear descriptions fix it at the source.'},
  {cat:'mcp',q:'Synthesis agent with 18 tools starts initiating new web searches instead of synthesizing findings.',ans:'Give the synthesis agent only the tools it needs for its role. Remove tools outside its specialization.',why:'Tool overload degrades tool selection reliability. An agent with irrelevant tools will misuse them.'},
  {cat:'mcp',q:'Agent makes many exploratory calls to discover available data sources on every request.',ans:'Expose content catalogs as MCP resources so the agent has visibility into available data at connection time.',why:'MCP resources are designed for upfront data discovery, eliminating the need for exploratory tool calls.'},
  {cat:'mcp',q:'Team needs a shared GitHub MCP server available to all engineers without committing tokens.',ans:'Use project-scoped .mcp.json with environment variable expansion (${GITHUB_TOKEN}), committed to the repository.',why:'Project-scoped .mcp.json is version-controlled and shared. Tokens stay out of version control via env vars.'},

  // CONTEXT MANAGEMENT
  {cat:'context',q:'Agent handling a 20+ turn billing dispute references "the overcharge" instead of the exact $847.50 amount.',ans:'Extract transactional facts (amounts, dates, IDs) into a persistent "case facts" block at the top of every prompt.',why:'Case facts blocks preserve precise values that progressive summarization would compress into vague references.'},
  {cat:'context',q:'After 90 minutes exploring a 200k-line codebase, the agent starts referencing general patterns instead of specific findings.',ans:'Have the agent maintain a scratchpad file recording key findings throughout the session.',why:'Context degradation causes models to rely on general knowledge as specific early findings compete for attention.'},
  {cat:'context',q:'Multi-phase codebase investigation: the agent forgets custom token signing it found in phase 1 during phase 2.',ans:'Write key findings to a scratchpad file at the end of each phase and read it at the start of the next.',why:'Scratchpad files persist findings across context boundaries where conversation history degrades.'},
  {cat:'context',q:'97% aggregate accuracy on insurance claims — safe to fully automate?',ans:'Not yet. Run stratified analysis by document type and field. Aggregate metrics can hide 85% accuracy in a critical segment.',why:'Aggregate accuracy masks poor performance on specific subsets. Stratified analysis is required before automation.'},
  {cat:'context',q:'Research synthesis agent claims "AI adoption reached 45%" but the source is unknown.',ans:'Require subagents to output structured claim-source mappings and instruct synthesis to preserve them in the final report.',why:'Provenance must be preserved structurally through the pipeline. Post-hoc verification is not sufficient.'},
];"""

ucs_start = content.find('const UCS=[')
ucs_end = content.find('\nlet uccat=', ucs_start)
assert ucs_start != -1 and ucs_end != -1
content = content[:ucs_start] + new_ucs + '\n' + content[ucs_end:]

# ── Replace 5: Use cases tab filter buttons — add 'code' category ──────────
old_uc_filter = '''  <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:12px" id="ucfilter">
    <button class="lbtn on" onclick="setUC('all',this)">All</button>
    <button class="lbtn" onclick="setUC('hooks',this)">Hooks</button>
    <button class="lbtn" onclick="setUC('arch',this)">Architecture</button>
    <button class="lbtn" onclick="setUC('prompt',this)">Prompt</button>
    <button class="lbtn" onclick="setUC('mcp',this)">MCP</button>
    <button class="lbtn" onclick="setUC('context',this)">Context</button>
  </div>'''
new_uc_filter = '''  <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:12px" id="ucfilter">
    <button class="lbtn on" onclick="setUC('all',this)">All</button>
    <button class="lbtn" onclick="setUC('hooks',this)">Hooks</button>
    <button class="lbtn" onclick="setUC('arch',this)">Architecture</button>
    <button class="lbtn" onclick="setUC('code',this)">Claude Code</button>
    <button class="lbtn" onclick="setUC('prompt',this)">Prompt</button>
    <button class="lbtn" onclick="setUC('mcp',this)">MCP</button>
    <button class="lbtn" onclick="setUC('context',this)">Context</button>
  </div>'''
content = content.replace(old_uc_filter, new_uc_filter)

# ── Replace 6: uclabels to include code ───────────────────────────────────
content = content.replace(
    "const uclabels={hooks:'Hooks',arch:'Architecture',prompt:'Prompt',mcp:'MCP',context:'Context'};",
    "const uclabels={hooks:'Hooks',arch:'Architecture',code:'Claude Code',prompt:'Prompt',mcp:'MCP',context:'Context'};"
)
content = content.replace(
    "const uccols={hooks:'p1',arch:'p1',prompt:'p3',mcp:'p4',context:'p5'};",
    "const uccols={hooks:'p1',arch:'p1',code:'p2',prompt:'p3',mcp:'p4',context:'p5'};"
)

# ── Replace 7: Cheat sheet — replace content between domain pills and grid2 ─
old_cheat_intro = '''  <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:14px">
    <span class="pill p1">D1 Agentic 27%</span><span class="pill p2">D2 Claude Code 20%</span><span class="pill p3">D3 Prompt 20%</span><span class="pill p4">D4 MCP 18%</span><span class="pill p5">D5 Context 15%</span>
  </div>
  <div class="grid2">'''

new_cheat_intro = '''  <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:14px">
    <span class="pill p1">D1 Agentic 27%</span><span class="pill p2">D2 Claude Code 20%</span><span class="pill p3">D3 Prompt 20%</span><span class="pill p4">D4 Tool/MCP 18%</span><span class="pill p5">D5 Context 15%</span>
  </div>

  <!-- SCENARIO BANNERS -->
  <div class="card full" style="margin-bottom:12px">
    <div class="ctitle" style="margin-bottom:10px">6 production scenarios &mdash; 4 randomly selected on exam day</div>
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:7px">
      <div style="background:#E8F4F0;border-radius:var(--r2);padding:9px 11px;border-left:3px solid #2E7D6A"><div style="font-size:12px;font-weight:700;color:#1A4A3A;margin-bottom:2px">Scenario 1: Customer Support</div><div style="font-size:11px;color:#2E7D6A">D1 Agentic &middot; D4 Tool/MCP &middot; D5 Context</div><div style="font-size:10px;color:#4A8A78;margin-top:3px">15 questions &middot; hooks, escalation, structured errors</div></div>
      <div style="background:#E4F2F8;border-radius:var(--r2);padding:9px 11px;border-left:3px solid #1A6B7A"><div style="font-size:12px;font-weight:700;color:#0E3D46;margin-bottom:2px">Scenario 2: Code Gen / Claude Code</div><div style="font-size:11px;color:#1A6B7A">D2 Claude Code &middot; D3 Prompt</div><div style="font-size:10px;color:#2A7A8A;margin-top:3px">17 questions &middot; CLAUDE.md, plan mode, iterative refinement</div></div>
      <div style="background:#E8EDF8;border-radius:var(--r2);padding:9px 11px;border-left:3px solid #2A4A80"><div style="font-size:12px;font-weight:700;color:#1A2E50;margin-bottom:2px">Scenario 3: Multi-Agent Research</div><div style="font-size:11px;color:#2A4A80">D1 Agentic &middot; D4 Tool/MCP &middot; D5 Context</div><div style="font-size:10px;color:#3A5A90;margin-top:3px">15 questions &middot; coordinator, parallel spawn, provenance</div></div>
      <div style="background:#F8F0E0;border-radius:var(--r2);padding:9px 11px;border-left:3px solid #7A5010"><div style="font-size:12px;font-weight:700;color:#4A3008;margin-bottom:2px">Scenario 4: Developer Productivity</div><div style="font-size:11px;color:#7A5010">D1 Agentic &middot; D4 Tool/MCP &middot; D5 Context</div><div style="font-size:10px;color:#8A6020;margin-top:3px">10 questions &middot; built-in tools, session mgmt, scratchpad</div></div>
      <div style="background:#F0EAF8;border-radius:var(--r2);padding:9px 11px;border-left:3px solid #5A2A7A"><div style="font-size:12px;font-weight:700;color:#3A1A50;margin-bottom:2px">Scenario 5: CI/CD Integration</div><div style="font-size:11px;color:#5A2A7A">D2 Claude Code &middot; D3 Prompt &middot; D1 Agentic</div><div style="font-size:10px;color:#6A3A8A;margin-top:3px">10 questions &middot; -p flag, explicit criteria, few-shot format</div></div>
      <div style="background:#F8EEE0;border-radius:var(--r2);padding:9px 11px;border-left:3px solid #7A4010"><div style="font-size:12px;font-weight:700;color:#4A2808;margin-bottom:2px">Scenario 6: Structured Data</div><div style="font-size:11px;color:#7A4010">D3 Prompt &middot; D5 Context</div><div style="font-size:10px;color:#8A5020;margin-top:3px">10 questions &middot; tool use JSON, batch API, confidence calibration</div></div>
    </div>
  </div>

  <!-- EXAM TRAP DECISION TABLE -->
  <div class="card full" style="margin-bottom:12px">
    <div class="ctitle" style="margin-bottom:10px">Exam trap decision table &mdash; read the symptom, pick the answer</div>
    <table class="cmp-table">
      <thead><tr><th>Symptom in the question</th><th>Correct answer direction</th><th>Why</th></tr></thead>
      <tbody>
        <tr><td>Rule violated X% of the time despite system prompt</td><td style="color:var(--g2);font-weight:700">PreToolUse hook</td><td style="font-size:11px">Hooks are deterministic; system prompts are probabilistic</td></tr>
        <tr><td>Coordinator output systematically missing a section</td><td style="color:var(--g2);font-weight:700">Fix coordinator decomposition</td><td style="font-size:11px">Systematic gaps = coordinator assigned wrong subtasks</td></tr>
        <tr><td>Wrong tool selected despite correct system prompt</td><td style="color:var(--g2);font-weight:700">Rewrite tool description</td><td style="font-size:11px">Tool selection is purely description-driven</td></tr>
        <tr><td>30% responses return text instead of tool call</td><td style="color:var(--g2);font-weight:700">tool_choice: "any"</td><td style="font-size:11px">Guarantees a tool call without specifying which</td></tr>
        <tr><td>Middle sections of report omitted / contradicted</td><td style="color:var(--g2);font-weight:700">Key findings at top + explicit headers</td><td style="font-size:11px">"Lost in the middle" — models miss middle-positioned content</td></tr>
        <tr><td>Reviewed own generated code, missed logic bug</td><td style="color:var(--g2);font-weight:700">Second independent Claude instance</td><td style="font-size:11px">Self-review limitation — generating instance retains reasoning bias</td></tr>
        <tr><td>Customer explicitly says "I want a human"</td><td style="color:var(--g2);font-weight:700">Honor immediately, no investigation</td><td style="font-size:11px">Explicit escalation request overrides agent capability</td></tr>
        <tr><td>Retry keeps failing after 3 attempts with error feedback</td><td style="color:var(--g2);font-weight:700">Check if data is actually in the document</td><td style="font-size:11px">Retries can't extract information that isn't there</td></tr>
        <tr><td>Bulk overnight processing, no users waiting</td><td style="color:var(--g2);font-weight:700">Message Batches API (50% savings)</td><td style="font-size:11px">Batch = latency-tolerant only; never for real-time</td></tr>
        <tr><td>Large-scale change across many files, architecture decisions</td><td style="color:var(--g2);font-weight:700">Plan mode first</td><td style="font-size:11px">Plan mode explores before committing; direct for clear scoped fixes</td></tr>
      </tbody>
    </table>
  </div>

  <div class="grid2">'''

content = content.replace(old_cheat_intro, new_cheat_intro)

# ── Replace 8: Pattern quick-ref card after existing key decision rules ────
old_key_decisions_end = '''        <div style="background:var(--warm-ll);border-radius:var(--r2);padding:10px 12px;font-size:12px;color:var(--warm)"><b>Fix coordinator</b> &rarr; systematic output gaps<br><b>Fix subagent</b> &rarr; execution quality issues</div>
      </div>
    </div>
  </div>
</div>'''

new_key_decisions_end = '''        <div style="background:var(--warm-ll);border-radius:var(--r2);padding:10px 12px;font-size:12px;color:var(--warm)"><b>Fix coordinator</b> &rarr; systematic output gaps<br><b>Fix subagent</b> &rarr; execution quality issues</div>
      </div>
    </div>
    <div class="ctitle" style="margin-top:12px;margin-bottom:8px">Pattern quick-ref &mdash; one line per testable pattern</div>
    <ul class="clist">
      <li><span class="dot d1"></span><span><b>stop_reason loop control:</b> continue on "tool_use", stop on "end_turn" &mdash; never check response text</span></li>
      <li><span class="dot d1"></span><span><b>Task tool spawning:</b> "Task" must be in allowedTools; multiple Task calls in one response = parallel execution</span></li>
      <li><span class="dot d2"></span><span><b>CLAUDE.md scope:</b> user-level (~/.claude) = not shared; project-level (repo root) = shared via version control</span></li>
      <li><span class="dot d2"></span><span><b>.claude/rules/:</b> YAML frontmatter with glob paths for conditional loading &mdash; not always-on like CLAUDE.md</span></li>
      <li><span class="dot d2"></span><span><b>context: fork:</b> runs skill in isolated sub-agent &mdash; verbose output stays in fork, only final result returns</span></li>
      <li><span class="dot d2"></span><span><b>-p flag:</b> non-interactive mode for CI/CD pipelines; --output-format json + --json-schema for structured output</span></li>
      <li><span class="dot d3"></span><span><b>Explicit criteria:</b> "flag X when Y" with code examples &mdash; not "use good judgment" or "high confidence only"</span></li>
      <li><span class="dot d3"></span><span><b>Few-shot for edge cases:</b> targeted examples of the ambiguous case outperform more standard examples</span></li>
      <li><span class="dot d3"></span><span><b>Retry with feedback:</b> append original doc + failed result + specific error &mdash; not same prompt repeated</span></li>
      <li><span class="dot d4"></span><span><b>Tool descriptions:</b> include scope, formats, examples, and explicit "do NOT use for X" exclusions</span></li>
      <li><span class="dot d4"></span><span><b>tool_choice values:</b> "auto" = optional; "any" = must call one; {type:"tool",name:X} = must call this specific tool</span></li>
      <li><span class="dot d4"></span><span><b>MCP resources:</b> read-only data for upfront discovery; MCP tools for actions with side effects</span></li>
      <li><span class="dot d5"></span><span><b>Case facts block:</b> extract specific amounts/dates/IDs into persistent block &mdash; not relying on conversation history alone</span></li>
      <li><span class="dot d5"></span><span><b>Scratchpad files:</b> write key findings after each phase; read at phase boundaries to prevent context degradation</span></li>
      <li><span class="dot d5"></span><span><b>Aggregate accuracy:</b> 97% overall can hide 85% on a critical segment &mdash; always stratify before automating</span></li>
    </ul>
  </div>
</div>'''

content = content.replace(old_key_decisions_end, new_key_decisions_end)

# ── Write ──────────────────────────────────────────────────────────────────
with open(HTML, 'w', encoding='utf-8') as f:
    f.write(content)

print('Done. EXQDB:', len(EXQDB), 'questions')
print('File size:', len(content), 'bytes')
