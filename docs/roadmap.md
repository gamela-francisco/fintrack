# FinTrack Roadmap

## Tier 1 — Non-negotiable, must exist and be understood by 21 Sept 2026
- [ ] Core CRUD (create, read, update, delete transactions) on PostgreSQL
- [ ] Anthropic API integration for transaction categorisation
- [ ] Full conceptual ownership of every line (Ground Zero Curriculum method)
- [ ] Working local demo (uvicorn + curl/docs provable)

## Tier 2 — Strongly wanted, can legitimately slip into early term
- [ ] Railway deployment (live URL)
- [ ] Plain-English monthly summaries (second AI feature)
- [ ] Polish: README, error handling, pytest tests

## Tier 3 — Explicitly out of scope, do not plan around
- Frontend depth (parked — thin demo client only)
- Auth/security hardening beyond basics
- Performance/scale work (answer conversationally in interviews, don't build)

## Sequence (locked, do not reorder)
1. Ground Zero Curriculum, Weeks 1–5 (foundation on existing FastAPI/SQLite code)
2. PostgreSQL (migrate data layer)
3. Anthropic API integration (categorisation)
4. Railway deployment
5. Polish + tests

## Calendar (camp-adjusted, as of 24 July 2026)
- Week 1: 21–24 Jul — PASSED
- Week 2: 28–31 Jul
- Week 3: 4–7 Aug
- (Youth camp: 10–14 Aug — no study)
- Week 4: 18–21 Aug
- Week 5: 25–28 Aug
- Phase 2 (Postgres → Anthropic → Railway → polish): 1 Sept onward, ~3 weeks available before term (21 Sept)
- Interview-drilling session: early Sept, using accumulated interview-likely list

## Definition of "enough" for 21 Sept
Tier 1 complete and understood, cold, no notes. As much of Tier 2 as the
calendar allows — if it slips into early term, that's acceptable and
honestly explainable in applications, not a failure state.