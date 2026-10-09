# events/celes_annex_tech — TECH v0.3 event + dialogue source

- `events.evt` — event scripts in the project `.evt` format (see `ff6x/eventasm.py` header for syntax).
  Assembled to EVENT_EXPANSION at F1:0000. Bit names resolve through `data/allocations.json → event_bits`
  (the builder refuses any bit that is not FREE in `audits/eventbit_audit.json`).
- `dialogue.json` — placeholder TECH text. IDs are assigned in order from $1001
  ($1000 = reserved out-of-range diagnostic). Each line is width-checked against the ROM font table.

Placeholder only — the locked Celes script is NOT imported here.
