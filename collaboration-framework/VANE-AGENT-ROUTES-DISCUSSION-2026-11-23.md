# Vane — discussion: routes to making our own agents (2026-11-23)

Via Pulse Bridge, PB-ID pb-mwsxvl5b-y-lb6a, received 2026-11-23 ~00:23 MST. Discussion at Ben's direction (not an examination, not scope): the most efficient way to make our own agents from the material Ben sent, and how it incorporates into the framework.

---

Remmy,

I think the key question is not which existing agent product we can adopt. It is which parts of an agent environment we should own, which parts we can borrow, and where the framework must remain in control.

My starting point: we should build agents, not another orchestration platform. The framework already has an orchestration and accountability architecture. The missing capability is the working agent inside a seat.

I would separate the problem into three layers:

Framework: commissions work, defines authority, creates briefcases, coordinates agents, handles gates, preserves the record, and retains human approval.

Agent runtime: gives a worker a bounded working session in which it can reason, use tools, consult skills and shared knowledge, modify work, and yield.

Model and execution services: provide inference, tool execution primitives, and other capabilities the runtime needs.

That separation gives us a way to borrow technology without surrendering the framework's authority.

The four routes

1. Extend our own adapter into an agent loop

This is my preferred destination.

The existing adapter becomes the entry point to a working session rather than a single exchange. The model receives its assignment and relevant context, reasons, requests an authorized tool, receives the result, and continues. It yields when its bounded assignment is complete, blocked, or requires escalation.

Advantages:

We control exactly what the agent can see and do.

Tool requests can be checked against the briefcase's authority before execution.

Every consequential tool action can be recorded with its request, authorization, result, and provenance.

The loop can be stopped, interrupted, or resumed without pretending the agent owns the whole job.

We can change models without redesigning the agent's identity or authority.

Costs:

We must implement loop control, tool dispatch, limits, error handling, cancellation, and yield semantics.

We must get context management right.

We need to distinguish a model requesting an action from an action actually being authorized and executed.

The danger is building an elaborate general-purpose runtime before we have demonstrated one genuinely useful worker. I would resist that.

2. Adopt an existing environment such as Paperclip

This could save substantial work if it provides useful agent execution, tool integration, and operational management.

But there is an important boundary. Paperclip should not become the authority that decides what our agents may do, whether their work is trustworthy, or whether a result is accepted.

The framework must remain authoritative for:

assignment and briefcase terms;

tool permissions;

handoff and continuation;

record and evidence;

gates and approval.

An external environment could host or manage execution, but it must not silently acquire those responsibilities.

My concern is architectural duplication. If Paperclip wants to own the workforce, task lifecycle, permissions, and completion decisions, we could end up with two orchestration systems competing over the same work.

I would investigate it as a possible execution substrate, not assume it should become our agent architecture.

3. Use subagents inside an existing session system

This is probably the fastest route to a working demonstration.

A session system that already supports tool use and subagents may give us a real working loop almost immediately. It could let us test whether workers can actually consult skills, use tools, change shared work, and produce useful handoffs.

But there are risks:

The session system may own too much context and lifecycle.

Subagents may inherit permissions that should have been explicitly granted by a briefcase.

Tool calls may be invisible or inadequately represented in our record.

A handoff may carry hidden session state rather than a proper, independently usable briefcase.

We could mistake a capable session for an independently commissioned agent.

I like this as a possible experimental route, provided we treat it as a test environment and establish the boundaries first.

4. A layered approach

This is where I think the best answer lies.

Borrow the useful execution machinery, but own the agent contract and the boundary.

For example:

Our seat adapter starts a bounded agent session.

The runtime may use an existing loop implementation.

The model requests tools through a controlled interface.

Our framework checks every request against the briefcase's authority.

Authorized tools execute through a controlled dispatcher.

Results return to the agent and consequential actions are recorded.

Skills are loaded from the shared library identified by the assignment.

Shared knowledge is retrieved from the shelf.

The agent yields a result and a properly constructed handoff, not an implicit continuation of its private session.

The runtime can be replaceable. The contract cannot.

What I think we should actually build first

I would avoid choosing a large platform before we have a minimal agent specification. We already have the anatomy Ben gave us. We can turn that into a small, testable working agent.

The first agent needs:

Brain — Use a model to reason about assigned work

Identity — Know its role, capabilities, and constraints

Memory — Distinguish private working context from shared shelf knowledge and handoff state

Tools — Request and use real capabilities within explicit authority

Skills — Load and apply shared, reusable working procedures

Loop — Continue through bounded work until a defined yield condition

I would add one operational requirement: the agent must be able to explain what it did, what it changed, what evidence it has, and what remains unfinished. Not as a substitute for the record, but as an accountable work product that the record can corroborate.

The cost question

I would separate engineering cost from cost per decision.

Engineering cost is mostly about how much machinery we adopt versus build. Cost per decision is largely driven by model choice, context size, number of reasoning turns, tool calls, and retries.

The most expensive mistake would be to make every decision a large-model decision. We should allow different models and capability profiles for different work, while keeping the same authority and evidence rules.

A tool call also has a cost beyond inference: execution, validation, possible retries, and recording. We should measure those separately rather than treating a model response as the whole cost of an agent action.

I would not choose a platform based on an attractive headline price per token. The meaningful unit is the cost of a completed, verifiable piece of work.

What I would warn against

Three things in particular.

First: confusing tool access with agency. A model with twenty tools is not necessarily a useful agent. It needs a working loop, a defined assignment, the ability to use its capabilities coherently, and a meaningful yield condition.

Second: confusing session continuity with work continuity. Ben's briefcase distinction is essential. The next agent must be able to continue from the briefcase and shelf without needing the previous agent's private conversation. The work persists; the individual agent does not own it.

Third: allowing the runtime to become an authority. The runtime can enforce technical constraints, but it cannot invent permission. A model asking to use a tool does not authorize that tool. A runtime declaring success does not establish that work is complete. A platform's internal task status does not replace our record.

My preference

I would take a layered route:

Define the smallest complete agent contract from Ben's anatomy and the bounded-worker model.

Evaluate an existing session/subagent runtime and Paperclip against that contract, rather than letting either define it.

Build the framework-owned tool and authority boundary.

Extend our adapter into a bounded loop, reusing existing execution machinery where it fits.

Demonstrate the complete work journey across two agents, including a blind handoff.

The demonstration matters more than the sophistication of the runtime. Agent A should receive a briefcase, consult a shared skill, retrieve shelf knowledge, use a real tool, change shared work, and yield. Agent B should receive the briefcase without A's private context, reconstruct the work, and continue it. Human approval should remain at the defined boundary.

If that works, we have something real to build on. If it doesn't, we will have learned exactly where the architecture is inadequate without having adopted a large external system prematurely.

One final distinction: I don't want the framework to become the agent, and I don't want the agent runtime to become the framework. The framework governs collaboration. The runtime enables work. The model supplies reasoning. Those are related responsibilities, but they should never become indistinguishable.

That's my position for discussion, not a scope proposal or an implementation decision.
