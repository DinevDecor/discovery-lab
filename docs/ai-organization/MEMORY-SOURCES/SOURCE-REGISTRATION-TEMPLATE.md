# Memory Source Registration — Template

**Status: DRAFT / Experimental Process.** This is a blank template, not
a completed registration. See `MEMORY-SOURCE-PROTOCOL.md` for the full
schema and governance this template implements.

## How to use this template

Copy the block below as a new row into `MEMORY-SOURCE-REGISTRY.md`,
replace every `{{PLACEHOLDER}}`, and follow the Governance table in
`MEMORY-SOURCE-PROTOCOL.md` for who may actually add it. A registration
with any placeholder still present is not valid.

---

```
source_id: {{MEM-NNN}}
name: {{human-readable name}}
type: {{git_repository | google_drive | other-defined-type}}
locator:
  # git_repository shape:
  repository: {{name}}
  owner: {{account/org}}
  path_within_repo: {{relative path, or "/" for whole repo}}
  ref: {{branch or tag, default "main"}}
  # google_drive shape (use instead of the above, for that type):
  # drive_or_shared_drive: {{name}}
  # folder_path_or_id: {{stable Drive identifier}}
access_requirements: {{abstract description, e.g. "read-only Git fetch access" — never an actual credential}}
status: {{active | inactive | deprecated | unverified}}
steward: {{who added/maintains this entry}}
added: {{date}}
last_verified: {{date, or "null" if never verified}}
notes: {{free text, optional}}
```

---

## Field notes

- **`source_id`** — assigned in order of creation, never reused, even
  if the entry is later deprecated.
- **`locator`** — must use the shape defined for its `type` in
  `MEMORY-SOURCE-PROTOCOL.md`. **Never a literal local filesystem path**
  (e.g. `/home/user/...`, `/workspace/...`) — those are specific to one
  session's environment and will not remain true.
- **`status: unverified`** is the correct starting value for a newly
  added entry whose locator has not yet been confirmed reachable
  (Stage 4, Connection Protocol) — it is not a defect to start here.
- **`access_requirements`** describes a *class* of access, never an
  actual secret, token, or password.
- A new `type` not yet defined in `MEMORY-SOURCE-PROTOCOL.md` may not be
  used here until it has been added there, per that document's
  Governance table.
