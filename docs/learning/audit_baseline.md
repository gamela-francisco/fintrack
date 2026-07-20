Date: Wednesday, 15 July 2026

1. Core Path
- 

2. Repetitive CRUD siblings
-

3. Don't recognise
- async def lifespan




## 2026-07-20 — Baseline audit
- Backend gaps identified: read_all_transactions, update_transaction, lifespan, get_db_connection (all SQL/async — 
matches Week 1 and Week 4)
- Frontend: functional, deferred deep understanding until backend curriculum done. Known gap: XSS escaping in 
loadTransaction is incomplete (only handles single quotes in onclick attributes, not full HTML injection).
- Categorisation logic: not yet built. Belongs to Phase 2 (Anthropic API integration), after Ground Zero Curriculum