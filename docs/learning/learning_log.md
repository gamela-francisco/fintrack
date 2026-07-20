# FinTrack Learning Log
Weekly teach-back log — each entry written from memory, no notes, no AI,
as a check that I actually understand what I built.

## 2026-07-16 — Baseline audit (logged 2026-07-20)
- Backend gaps identified: read_all_transactions, update_transaction,
  lifespan, get_db_connection (all SQL/async — matches Week 1 and Week 4)
- Frontend: functional, deep understanding deferred until backend
  curriculum done. Known gap: XSS escaping in loadTransaction only
  handles single quotes in onclick attributes, not full HTML injection.
- Categorisation: not yet built. Belongs to Phase 2 (Anthropic API
  integration), after Ground Zero Curriculum.

## 2026-07-20 — Light review
- Reread baseline audit, let the gap list sit before starting Week 1.