# Sample engagement

This is the unedited output of one real run of
[`examples/run_engagement.py`](../examples/run_engagement.py) on Claude. Only
the heading levels were changed to fit this page. Nothing was added,
rewritten or removed from the model's answers.

| | |
| --- | --- |
| Date | 2026-11-03 |
| Model | `claude-sonnet-5-5` |
| Mode | `full_audit` |
| Request | "Our support team is overwhelmed. We need a diagnosis and an action plan to cut response times by 30% before Q3." |
| Business context | `{"sector": "support"}` |
| Model requests | 4 (diagnostic, process, automation, strategy) |
| Duration | 138 s |
| Guard | `pass`, no violation |
| Declared gaps | none |

The request is a fictional example: no client data was used.

## Reproduce it

```bash
pip install -e ".[anthropic]"
export ANTHROPIC_API_KEY=...   # PowerShell: $env:ANTHROPIC_API_KEY = "..."
python examples/run_engagement.py --json engagement.json
```

Model answers vary from one run to the next, so your output will differ in
wording. The structure, the caps and the guard rules stay the same.

## What to look at

- **No invented figures.** The only figure about the client's business,
  the 30% target, comes from the request. Other numbers are plan horizons
  (the first 30 days) or sizes of the work itself (a one-page rule). The
  model states that no baseline, volume or headcount data was shared, and
  makes measuring a baseline the first action.
- **Inferences are labelled.** Each root cause says "probably" and carries a
  confidence level. The impact and effort scores (1 to 5) are the model's
  own ratings, as the diagnostic prompt requires.
- **Process before automation.** Each bottleneck links to a root cause.
  Automation candidates come from the redesigned process, and seven tasks
  are explicitly kept away from automation, with a reason for each.
- **Traceability.** Every action carries an owner, a done-condition and a
  link to an upstream root cause, bottleneck or candidate. The guard found
  no violation, so it made no extra model call.
- **Honest scope.** The summary and the risks flag that process changes
  alone may not reach 30% if volume has outgrown headcount.

## Output

### Diagnostic — root causes

- [RC1] Incoming requests are probably sorted and routed by hand, so every request waits for a person to read and classify it before work starts. (impact 4/5, effort 2/5, confidence medium)
- [RC2] Agents probably write similar answers from scratch each time because there is no shared, maintained set of approved responses for recurring request types. (impact 4/5, effort 2/5, confidence low)
- [RC3] Escalation probably happens without explicit criteria, so complex requests are either escalated late or passed on without the information the next person needs. (impact 3/5, effort 2/5, confidence low)

### Process — bottlenecks

- [B1] Every request waits for a person to read and classify it before work begins. Triage is manual and has no named owner or rules. (root cause RC1)
- [B2] Recurring questions are answered from scratch because no maintained set of approved answers exists. (root cause RC2)
- [B3] Escalation has no agreed criteria, destination or handoff content. Complex requests are held too long or passed on incomplete. (root cause RC3)

### Automation — candidates

- [A1] Structured intake: capture request type, product or account, and urgency from the customer at the point of contact, with mandatory fields. — rules_workflow
- [A2] Automatic categorisation, prioritisation and routing of requests that arrive with complete structured intake, using the written category and urgency rules. — rules_workflow
- [A7] Automatic recording of time spent at each stage (waiting for triage, waiting for pickup, handling, escalated) and a weekly summary for the support lead. — rules_workflow
- [A5] Escalation support: flag requests when a written trigger is met (for example, unresolved after the agreed time) and pre-fill the fixed escalation note with the case details already held. — rules_workflow
- [A6] One-step flagging of new answers for the answer base at the point of sending the reply, creating a review item for a named owner. — rules_workflow
- [A4] Draft replies for recurring request types from the approved answer base, adapted to the customer's details. The agent reviews, edits and sends. — hybrid
- [A3] AI suggestion of category and urgency for requests that arrive as free text without structured intake. The triage owner confirms or corrects. — hybrid

### Automation — do not automate

- Sending AI-drafted replies to customers without an agent reading them — Customer-facing wording carries reputational and sometimes legal exposure. We also have no baseline for quality and no confirmed quality target, so unsupervised replies cannot yet be judged safe.
- Fully automated answering or closing of requests (for example a customer-facing assistant that resolves cases alone) — Out of scope for the Q3 timeline and unsupported by evidence. We do not know the share of repetitive requests or the quality bar, and a wrong automated resolution produces repeat contacts.
- The decision to escalate in cases that are unusual, sensitive, or outside the written triggers — Escalation of non-standard cases is a judgement call. Automation may flag and pre-fill, but the agent decides.
- Handling of complaints, legal or regulatory matters, safety concerns, and requests from customers in difficult circumstances — These need judgement, empathy and accountability. Errors carry the highest reputational and legal cost. Route them to a named person.
- Writing answers for new or unusual requests from scratch — The target process keeps these with agents, and there is no approved material for a system to draw on. This is also where agents learn what to add to the answer base.
- Approving new answers into the answer base — Approval is what keeps answers correct. An unreviewed base would spread errors through A4. A named owner must keep this decision.
- Setting and changing category, urgency and escalation rules, and deciding what to do with the weekly findings — These are management decisions about service levels and priorities. Automation reports and applies the rules, but does not set them.

### Executive summary

The support team is overloaded and wants response times cut by 30% before Q3, but no baseline, volume or headcount data has been shared. The likely causes are manual triage, answers written from scratch, and escalation without clear rules. Each of these is an inference from sector patterns and has not been confirmed with client data. We recommend fixing the definition of 'response time' and measuring a baseline now, putting written rules around triage and escalation in the first 30 days, and adding automation only in the order the evidence supports. We also recommend testing capacity separately, because process changes alone may not deliver 30% if volume has outgrown headcount.

### Action plan — now

- Agree with management what 'response time' means for the 30% target (first response, resolution, or both). Confirm whether quality and customer satisfaction must hold while times fall, and confirm whether Q3 is a fiscal or calendar quarter. (owner: Head of support (decision) with the sponsoring executive; done when: The definition, the quality constraint and the Q3 date are written down and signed off by management.; linked to A7)
- Record a baseline from a sample of recent requests, by channel and request type. Measure the time waiting for triage, waiting for pickup, handling and escalated. (owner: Support lead; done when: A baseline for the agreed definition exists and the largest source of waiting time is identified.; linked to A7)
- Gather volume and trend, team size, shift coverage and how requests arrive. Compare volume growth with headcount to test whether capacity, not process, is the main constraint. (owner: Support lead with Finance or HR for headcount data; done when: A short note states whether volume has outgrown staffing. If it has, a staffing or demand-reduction decision is put to management alongside the process plan.; linked to RC1)
- Name a daily triage owner on a rota. Give them a one-page list of request categories, urgency levels and who handles each. (owner: Support lead; done when: The rota is running and the one-page rules are signed off and used by every triage owner.; linked to B1)
- Review a sample of recent requests with the team to list the most frequent request types and the share that are repetitive. Also ask agents for the three situations where they lose most time, to test all three inferred causes against their experience. (owner: Support lead with two or three senior agents; done when: A list of frequent request types and an estimated repeat share exist. RC1, RC2 and RC3 are each marked as confirmed, weakened or unchanged.; linked to B2)
- Write a one-page escalation rule covering when to escalate, to whom, and what information the handoff must contain. Review it with the receiving teams and start using it. (owner: Support lead with second-level owners; done when: The rule is agreed by the receiving teams and used for all escalations.; linked to B3)

### Action plan — next

- Draft approved answers for the few most frequent request types, written by the agents who handle them best. Give the answer base a named owner and a review cycle. Scale this to what the repeat-share finding supports, and reduce its scope if repeats are few. (owner: Answer-base owner (named by the support lead) with senior agents; done when: The starting set is published where all agents can find it, with a named owner and a set review time.; linked to B2)
- Introduce structured intake on the highest-volume channels, capturing request type, product or account, and urgency with mandatory fields. Keep the fields few. Make sure phone and email contacts are entered in the same structure by agents. (owner: Support lead (intake design owner); done when: The highest-volume channels capture the agreed fields. The share of requests arriving with complete intake is being tracked.; linked to A1)
- Set up automatic recording of time at each stage, with a weekly summary for the support lead. Report at stage and team level first, not by individual. Start a short weekly review of the summary. (owner: Support lead; done when: Weekly stage-level figures are produced on one agreed definition, and the lead acts on them at a standing weekly review.; linked to A7)
- Introduce automatic categorisation, prioritisation and routing for requests that arrive with complete structured intake, using the signed-off rules. Every category has a named handler with absence cover. Exceptions have a visible path to the triage owner. (owner: Support lead with the triage owner; done when: Structured requests are routed without a manual read. The triage owner handles only exceptions, and misroutes are logged and reviewed.; linked to A2)

### Action plan — later

- Add escalation support. Flag requests when a written trigger is met and pre-fill the fixed escalation note from case details. Set trigger time limits using the first weeks of stage data. (owner: Support lead with second-level owners; done when: Flags and pre-filled notes are in use. The escalation return rate and late escalations are being reviewed, and the triggers are adjusted from that data.; linked to A5)
- Add one-step flagging of new answers at the point of sending a reply. This creates a review item for the answer-base owner, who has set time to process them. (owner: Answer-base owner; done when: Flagged items are reviewed on a fixed cycle and approved answers join the base. The queue of unreviewed items does not grow.; linked to A6)
- Pilot AI-drafted replies for recurring request types, built only on approved answers. The agent reviews, edits and sends every reply. Start only if the repeat-share finding and the quality targets support it. Run a sampled quality check of sent replies in the first weeks. (owner: Support lead with the answer-base owner; done when: The pilot runs with agent approval on every reply. Sampled quality checks show quality holding against the agreed target, and the handling-time effect is measured. Management then decides whether to widen or stop it.; linked to A4)
- Consider AI suggestions of category and urgency for free-text requests that bypass structured intake, with the triage owner confirming or correcting each. Go ahead only if stage data shows triage wait is a meaningful part of the delay for those requests. (owner: Support lead with the triage owner; done when: Management has made a go or no-go decision based on stage data. If go, suggestions are confirmed by a person and corrections are recorded.; linked to A3)

### KPIs

- Response time on the agreed definition (first response, resolution, or both), by request type — Down. The client's target is a 30% reduction before Q3.
- Time waiting for triage and time waiting for pickup — Down
- Share of requests arriving with complete structured intake, by channel — Up
- Escalation return rate and share of escalations made late — Down
- Share of replies sent from the approved answer base, and handling time on those request types — Share up, handling time down
- Customer satisfaction or quality score, if the client already holds one — Held or improved while response times fall

### Risks

- The root causes are inferred from sector patterns and may not match this client. The overload may mainly be a capacity issue. — Baseline measurement, the sample review and agent input come first. Each cause is marked confirmed or removed before further effort goes into it. The capacity test runs in parallel.
- 'Response time' is left undefined, or means different things to different people, so the 30% cannot be judged. — Management signs off the definition in the first 30 days, and all KPIs use it.
- Wrong or outdated routing rules misroute requests at scale, faster than a person would. Customers may also pick the wrong category. — The support lead signs off the rules, exceptions have a visible path to a person, and misroutes are logged and reviewed.
- Too many mandatory intake fields put customers off, or agents on phone and email bypass the structure. — Keep the fields to what routing needs. Have agents fill them in for phone and email, and track the share of complete intake.
- The answer base goes stale, or flagged items pile up, because no one has time to review them. — Name an owner with protected review time. No answer enters the base without that owner's approval.
- An AI-drafted reply is wrong and is sent by a rushed agent. Customer details may also reach an external service. — An agent approves every reply, drafts draw on approved answers only, and sampled quality checks run in the first weeks. Check data protection before any pilot. Fully automated replies and closures are excluded from this plan.
- Escalation flags are ignored if there are too many, or triggers set without data are too tight or too loose. — Set trigger time limits from the first weeks of stage data and review them regularly.
- Stage figures are read as individual performance policing, which harms trust and makes status entries unreliable. — Report at stage and team level first, and define stages so that agents apply them the same way.
- The team has no spare time to change how it works before Q3, and the rules and answer base are not kept up. — Ask management to protect time for the first 30 days of work. If it cannot, raise the capacity decision with management early.

### Next step

This week, hold one working session between the head of support and the support lead to fix the definition of 'response time' for the 30% target, and assign someone to pull a sample of recent requests with their timestamps for the baseline.

### Guard violations

- (none)

### Declared gaps

- (none)

---

Model: claude-sonnet-5-5 · Model requests: 4 · Duration: 138 s
