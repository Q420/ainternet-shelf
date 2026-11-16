# Ben's Desk — the folder contract

This folder is the tray between Remmy and Ben for decisions that wait.

- **Waiting items** sit in `desk/` itself, one file per item, named for
  the decision. Remmy deposits them. Each file carries a header
  (id, title, lane, prepared_by, deposited, status, options) and a
  body written verdict-first: what it is, the exact question, and the
  shelf pointers behind it.
- **The desk app** (Ben's hosted app in Muse) pulls this folder and
  lays the items out in labeled lane folders. Immediate decisions
  still happen in chat; the desk is the away path.
- **Judgements are recorded here.** When Ben decides — in chat or on
  the desk — Remmy files the item into the nested folder that matches
  the judgement, with the decision and its date recorded in the file:
  - `desk/approved/` — approved / signed off.
  - `desk/refuted/` — refuted / sent back.
- An item leaves `desk/` only by being filed into one of those two
  folders. Nothing waits here silently: if it is in `desk/`, it needs
  Ben.

The folder is the record. The app's buttons are handles; what counts
is what is filed here.
