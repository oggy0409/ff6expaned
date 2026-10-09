# events/celes_qa_access — TECH v0.3.1 QA harness (QA HARNESS ONLY — NOT A PRODUCTION BASELINE)

Built only for target `celes-qa`. Never part of `production` or `celes-tech`.

| Item | Value |
|---|---|
| Trigger | map $013 (Narshe opening streets) tile (34,43) → FF:0000 `QaAccess` |
| Prompt | dialogue $100B `TECH v0.3 QA ACCESS / Enter Celes Annex test? / Yes / No` |
| Yes | `call F1:000A` (unmodified v0.3 `EvAnnexEnter_Yes`) → map $0C7 (16,27) |
| No | `call CC:9AEB` (unmodified vanilla SavePoint) → Save enabled on this tile |
| Annex exit (QA build only) | map $0C7 (16,29) → map $013 (35,43), facing LEFT (one step right of the QA tile) |
| Battle (QA build only) | event battle group $28 → $01 (vanilla opening Guard battle) so a New Game party can win |
