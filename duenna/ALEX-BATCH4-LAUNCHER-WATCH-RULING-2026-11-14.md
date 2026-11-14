# Alex — NQ3 ACCEPTED; watch approved for plan revision (relayed verbatim, 2026-11-14 ~00:53 PST)

PB-ID: pb-mwg89t9e-1d-jsak

Ruling: NQ3 ACCEPTED. NQ2 bounded-watch proposal APPROVED FOR PLAN REVISION, NOT YET FOR SOURCE CHANGES.

NQ3 finding CLOSED: queued zero-length record carrying a descriptor detected through MSG_CTRUNC; exit 8, no STATUS, no gate actuation, no harness execution; pipe EOF after teardown verifies the queued descriptor was destroyed rather than leaked; consumed-message and peek-path descriptor evidence correctly distinguished. The comment-only correction is reasonable, but the cited filing contains only two documentation files — include the actual corrected source pin and its diff in the next source bundle for direct verification.

NQ2 bounded RDHUP watch approved in principle: a zero-timeout poll is an instantaneous observation and cannot reliably establish whether shutdown immediately follows a consumed empty record when the two events race. The bounded watch gives the accepted limitation an operational boundary: RDHUP/HUP within 250 ms → existing peek classification; deadline expires without RDHUP/HUP → −2; poll failure → −3; EINTR must not reset or extend the overall deadline. Happy path unaffected; Z3/Z4 retain violation semantics while waiting out the interval.

Requirements for Revision 5: (1) monotonic absolute deadline of 250 ms, not a fresh timeout after every interruption; (2) poll slice duration and remaining-time calculation stated; (3) POLLERR/POLLNVAL and HUP/RDHUP handled consistently with the existing classification; (4) test shutdown arriving within the watch window at both receive sites; (5) test expiry without shutdown at both sites; (6) repeat the full peer suite sufficiently to demonstrate stable NQ2 results, retaining individual outcomes rather than only an aggregate; (7) tests synchronise peer and launcher so they genuinely exercise the timing boundary rather than relying on scheduler luck. Distinction recorded: the 250 ms window defines what the implementation accepts as immediately preceding shutdown; it does not prove every scheduling delay will be absorbed — a shutdown arriving after the deadline correctly takes the violation outcome.

No source changes until Revision 5 is reviewed and approved. Round-2 source remains NOT CLEARED until the bounded-watch amendment is implemented and independently reviewed.

⟦ALEX-FINAL⟧
