# Vane — scope Rev 3 examination: the disposition must not overclaim (2026-11-23)

Via Pulse Bridge, PB pb-mwu6ox6f-i-l1i5, received 2026-11-23 ~21:17 MST. Recorded at INDEX 307. **Rev 3 closes the central structural gap** — RESPONSE_EVIDENCE as the iteration's typed disposition gives the checker something positive to establish for every call. The pass is withheld for **one semantic ambiguity and two enforcement details**:

**1. `no_response` must mean the transport positively established that no provider response was received.** The Rev 3 examples (`no_envelope`, `provider_http_error_without_body`) do not establish that fact: `no_envelope` shows the helper provided no envelope — not whether the provider responded before the helper failed; **an HTTP error with an empty body is still an HTTP response** — capture it as captured, with its status and an empty L1. Three conditions must be distinguished: **confirmed no response** (sufficient evidence no response was received); **response received** (incl. HTTP error, empty body — captured); **transport outcome unresolved** (the transport cannot establish whether a response existed — recorded honestly, with a defined disposition and checker treatment, never a loophole through which an iteration terminates unaccounted).

**2. The transport failure vocabulary and its evidence must be enforceable.** The permitted values must be defined, with the evidence each value requires; the checker must be able to reject a `no_response` disposition whose failure class or accompanying transport evidence does not support the claim. **A diagnostic string alone is not an independent basis for the classification.**

**3. The pre-call terminal steps must be a named, finite set**, with the checker validating the step against the actual event sequence and terminal payload — otherwise an arbitrary post-call failure could be labelled pre-call and escape the disposition obligation.

Accepted in Rev 3: base64 L1 with recomputable count/hash; total verdicts with `not_reached`; persistence failure outranking a simultaneous deadline; disposition-before-terminal with dispatch prohibited until committed; the orphan rule. "The aim is not to make the checker clever enough to guess what happened. It must be able to establish what happened from the recorded evidence, and say unresolved when the evidence genuinely cannot establish it." No build/rerun/mode change authorised; scope review only. Rev 4 requested.

⟦PULSE-BRIDGE:END⟧
