# Watchdog Stage 3 — empty-term should-fix closed

Per the gate-rebuild review (claude/WATCHDOG-STAGE3-GATE-REBUILD-REVIEW):
`load_registry` now refuses a job whose gate_terms contain an empty
or whitespace-only term, as a RegistryError — such a term matches
every turn, so the gate would silently pass everything while looking
like a gate. Fixtures: an empty term fails load; a whitespace-only
term fails load. Ledger suite 70/70; detector 101/101; guard 45/45;
waker 0 failures.

Job-authoring guidance (from the same review's note): gate matching
is case-insensitive substring. Short terms over-match ("ai" matches
"said"). That is correct for a pre-filter — the judge makes the real
decision — but authors should write specific terms.
