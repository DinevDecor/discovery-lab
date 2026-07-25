# processed/

Where the agent/steward moves a file's original, unmodified copy once
handling is complete — regardless of whether the outcome was `ACCEPTED`,
`REJECTED`, or `BLOCKED` (see `../PROCESSING-PROTOCOL.md`, step 12 and
"File handling rules"). Nothing here is deleted automatically. The
matching manifest in `../manifests/` is the authoritative record of a
file's status — this folder just holds the files themselves.

Not a folder a human ever chooses to put something in.
