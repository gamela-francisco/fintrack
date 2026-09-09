# FinTrack Learning Log

Weekly teach-back log — each entry written from memory, no notes, no AI,
as a check that I actually understand what I built.

## Week 1
### 2026-07-16 — Baseline audit (logged 2026-07-20)
- Backend gaps identified: read_all_transactions, update_transaction,
  lifespan, get_db_connection (all SQL/async — matches Week 1 and Week 4)
- Frontend: functional, deep understanding deferred until backend
  curriculum done. Known gap: XSS escaping in loadTransaction only
  handles single quotes in onclick attributes, not full HTML injection.
- Categorisation: not yet built. Belongs to Phase 2 (Anthropic API
  integration), after Ground Zero Curriculum.

### 2026-07-20 — Light review
- Reread baseline audit, let the gap list sit before starting Week 1.

### 2026-07-21
- confirmed 404/405/422 distinctions hands-on. Minor mix-up: tested wrong path (/item vs /items) but it accidentally 
confirmed 422 behavior on a real route I'd forgotten I registered. Good reminder to check actual code, not memory, 
when debugging.

### 2026-07-22 - Week 1, Wednesday: connecting HTTP to FinTrack
- Question for next week note: Why doesn't read_all_transactions use async? Noticed no await inside it - is that 
intentional or a gap? Revisit in week 2
- Wrote "why this endpoint exists" sentences for read_all_transactions and get_db_connection
- Learned: object.method() vs object.attribute = value distinction, via row factory
- row_factory: makes fetchall()/fetchone() return dict-like Row objects instead of bare tuples, so columns are accessed 
by name(row["amount"]) not position (row[1])

### 2026-07-23 - Week 1, Thursday: comparing understanding, lifespan
- lifespan (@asynccontextmanager): code before yield runs once at startup, code after yield runs once at shutdown - NOT
per-request. Corrected my own initial mix-up here (thought "after-yield" ran per-request - it doesn't, route functions 
handle per-request logic separately).
- app = FastApi(lifespan=lifespan) is what actually wires the functions the function in - without it, lifespan would be 
defined but never called.
- CORS middleware noted but not deep-dived - allows frontend (different origin) to talk to backend. allow_origins=["*"]
fine for local dev, flagged as a real security setting to tighten before deployment.
- get_financial_summary: SUM() is a SQL aggregate function - collapses many rows into one computed value, calculated
inside SQLite itself (faster than looping in Python). Because the query produces exactly ome row with one (unnamed) 
column, fetchone() + positional [0] access is the natural fit - contrasts with read_all_transactions'  SELECT *, which
produces many named rows, naturally pairing with fetchall() + row_factory's dict-style access
- update_transaction: SQL's UPDATE silently affects zero rows if the WHERE clause matches nothing - no error, no new row,
just does nothing. Without Step A's existence check, the endpoint would return a false "success" message for an update that
never happened. Same category of bug as the earlier list-index-as-identity flaw: a request that appears to succeed while
silently not doing what the client thinks it did.
- HTTPException: not a database error - used when the query itself succeeds but the situation is still wrong from a 
business-logic standpoint. Converts directly into a real HTTP status code + JSON body for the client.

### 2026-07-24 - Week 1, Friday: teach-back + environment debugging
**First teach-bag attempt (out loud, no notes):**
- fumbled: request/response definitions, path+method matching, lifespan
- solid: error codes(404, 405, 422)
- result: did not pass - repeated targeted sections rather than full week

**Environment detour - venv relocation bug:**
- Server wouldn't start after Monday's repo restructure. Root cause:
  venvs hardcode their own absolute path at creation time. Moving/renaming
  the containing folder breaks activation silently — prompt shows (venv)
  and $VIRTUAL_ENV looks set, but points to the old, now-wrong path.
- Fix: delete and recreate the venv fresh at its current location — don't
  try to repair a moved venv.
- Also reinforced from Tuesday: `python3 -m <tool>` bypasses PATH lookup
  and forces resolution through the currently active Python, which is why
  it's the reliable fix when a CLI command misbehaves inside a venv.
- New tool notes: `-m` in `python3 -m fastapi dev` = run as a module,
  not a PATH-resolved command. `-i` in curl = include response headers
  in output, not just the body. curl is a general-purpose HTTP client,
  unrelated to FastAPI — it just sends raw requests to any server.

**Second teach-back attempt (after re-running live examples):**
- Ran curl against real FinTrack data (GET /transactions), correctly
  named status line, headers, body from raw output.
- Re-ran 404/405/422 examples live, cold — explained correctly.
- Full teach-back: request/response anatomy, 422, and lifespan landed
  clean. Two corrections needed:
  1. Endpoint = path + method together, not just a path — this is
     precisely why 405 exists as distinct from 404.
  2. 404 = path doesn't exist at all (method isn't even checked yet).
     405 = path exists, but that specific method isn't registered for it.
     Had these backwards on the first pass.
- Third pass, corrected: clean.

**Week 1: PASSED.**

**Open question carried to Week 2:** why does read_all_transactions have
no async/await? No I/O actually awaited inside it — intentional, or a gap?
Revisit once event loop mechanics are covered.

**Interview-likely topics flagged this week:**
- 404 vs 405 vs 422 — precise distinction, not just "an error happened"
- Why HTTPException differs from a raw Python exception
- update_transaction's existence-check: SQL UPDATE silently affects zero
  rows on a non-matching WHERE — without the check, a bad ID gets a false
  "success" response instead of an honest error 

## 2026-07-30 — Week 2, event loop + resolving the read_all_transactions question
- Event loop (JS): Web APIs (browser-provided, not JS itself) handle slow
  tasks off the main thread. Completed tasks go to the task queue. Event
  loop moves them to the call stack once it's empty. JS itself stays
  single-threaded throughout — the waiting happens outside JS entirely.
- Resolved open question: read_all_transactions has no async/await because
  (1) practically, local SQLite disk I/O is fast enough that blocking
  rarely matters, and (2) technically, Python's built-in sqlite3 module
  doesn't support async at all — would need aiosqlite or similar.
- Forward note: this decision must be revisited in Phase 2. Once migrated
  to PostgreSQL (a real network call, especially once deployed on Railway),
  async becomes the correct choice, not just a nice-to-have — likely via
  asyncpg or SQLAlchemy's async support.

## 2026-07-31 — Week 2 add FastAPI def vs async def notes, resolve event loop follow-up, teach back
- FastAPI def vs async def: plain def endpoints run in a separate thread
  pool automatically — a safety net FastAPI provides because it can't
  trust a sync function not to block. async def endpoints run directly
  on the event loop, no safety net — FastAPI trusts the dev to await
  everything slow correctly inside it. Risk: async def + an unawaited
  blocking call freezes the entire server for all requests, not just
  that one — worse than plain def, which is protected either way.
- Forward note for Phase 2: Anthropic API calls are exactly the kind of
  slow, external operation async/await exists for. Check if Anthropic's
  SDK has an async client, and if the categorisation endpoint is async
  def, make sure the call is properly awaited.
- Full teach-back, out loud, no notes: event loop, Web APIs, task queue,
  def vs async def, and why read_all_transactions doesn't need async.
- Passed cleanly, first attempt. One precision note: sqlite3 not
  supporting async is the hard technical reason; "overkill" is secondary
  practical color, not the primary reason.
- Week 2: PASSED.

## 2026-08-05 — Week 3, Tuesday: Pydantic first exposure
- Pydantic checks shape and type of incoming request body data, before
  the endpoint function runs at all. Invalid data → FastAPI raises 422
  automatically (connects directly to Week 1's understanding of what 422
  actually means).
- Correction: Pydantic doesn't just validate — it also converts where
  reasonable (e.g. "50" string → 50.0 float). Only fails when conversion
  genuinely isn't possible (e.g. "fifty" can't become a number).

## 2026-08-07 — Week 3, schema rebuild
- Rebuilt TransactionBase using Decimal for amount (not float) — avoids
  float rounding errors at the validation boundary. Correct reasoning,
  but connects to a real design tension: create_transaction/update_transaction
  explicitly convert to float() before hitting SQLite, because SQLite has
  no native Decimal storage class (only NULL/INTEGER/REAL/TEXT/BLOB) —
  so precision protection at validation is partially undone at storage.
  Real systems often store money as integer cents to sidestep this
  entirely (not implementing now, just noting it exists).
- Date format consistency: without a fixed format (e.g. YYYY-MM-DD),
  SQLite compares date strings alphabetically, not chronologically —
  produces silently wrong filter/sort results, no error thrown. Same
  bug family as update_transaction's silent-failure risk from Week 1:
  no crash doesn't mean no bug.
- Break 2 (wrong type): sent amount as a string "not-a-number" against a
  Decimal field. Error type: "decimal_parsing" — not a generic ValueError,
  Pydantic's error types are specific to the exact type being validated
  against (would've been "float_parsing" if the field were float instead).
  Confirms error type reflects the schema's own type choices, not a
  generic catch-all.
- Week 3 (Wed/Thu tasks): completed in one session, 7 Aug.

## 2026-08-17 — Week 3 teach-back (delayed by camp, 10 days post-material)
- Full teach-back, out loud, no notes, cold after camp gap.
- Covered: Pydantic type-hint validation running before endpoint execution,
  missing-field 422 example, decimal_parsing example, and the Decimal-vs-
  float storage-layer conversion tension.
- Passed cleanly. Notably stronger than the material felt on 7 Aug —
  the gap (including camp, zero contact) is good evidence this is real
  ownership, not short-term recall.
- Week 3: PASSED.

## 2026-08-18 — Week 4, Tuesday: SQL injection first exposure
- Keyword-blocking (DROP, DELETE, etc.) is not real defense — attackers
  can't be fully anticipated, infinite variation possible.
- Real defense: parametrized queries. Query structure and user input are
  sent to the database SEPARATELY, not glued into one string. Database
  compiles the query shape first (e.g. WHERE id = ?), then substitutes
  the value in afterward as a literal — never as executable syntax.
- Unsafe (string concatenation): entire query built as one string before
  reaching the database — by the time it arrives, database can't tell
  what was originally user input vs. code you wrote.
- Confirmed: my own delete_transaction, update_transaction, etc. already
  use parametrization correctly — this week is understanding *why* what
  I already have is safe, not fixing something broken.

## 2026-08-19 — Week 4, Wednesday: injection demo, hands-on
- Built vulnerable_login (string concatenation) and safe_login
  (parametrized) in scratch/injection_test.py, using ' OR '1'='1'
  as the attack input against both.
- vulnerable_login: attack input got glued into the query string itself,
  turning WHERE username = '' OR '1'='1' into an always-true condition —
  returned every row in the table (full password dump).
- safe_login: same attack input, but sent separately from the query
  structure via parametrization — treated as one literal string value
  to search for. No match found, correctly returned empty.
- Same attack, opposite outcomes — purely a function of how query and
  data were combined, confirming Tuesday's mechanism firsthand.
- Verified read_all_transactions specifically (the dynamic query-building
  case, flagged as highest injection risk since query is built piece by
  piece). Confirmed: query string only ever gets static text appended
  (" AND LOWER(...) LIKE LOWER(?)") — the ? never touches user input
  directly. params.append(f"%{search}%") uses an f-string, but only to
  build a VALUE, not the query structure — that value still flows through
  the safe cursor.execute(query, params) parametrized channel.
- Key distinction: f-strings/concatenation aren't dangerous by default —
  only when used to build query STRUCTURE. Building a value that still
  passes through ?/params separately is safe. Confirmed all four
  endpoints (read_all_transactions, create_transaction, delete_transaction,
  update_transaction) are genuinely parametrized, not just assumed.

## 2026-08-20 — Week 4, Thursday: schema rebuild and comparison
- Rebuilt CREATE TABLE from reasoning: id (INTEGER PRIMARY KEY AUTOINCREMENT),
  amount (REAL — SQLite has no Decimal), description (TEXT), category
  (TEXT), date (TEXT — no native date type, connects to Tuesday's point
  on format consistency for correct chronological sorting). All NOT NULL.
  No foreign keys — single table currently.
- Corrected two gaps found by comparing against real init_db():
  1. IF NOT EXISTS — not just "avoids duplication." Without it, init_db()
     (which runs on every server startup via lifespan) would throw
     sqlite3.OperationalError and CRASH the server on every restart after
     the first, since the table already exists from the previous run.
  2. Triple quotes ("""..."""): do NOT mean "this is code" vs regular
     quotes meaning "this is structure" — that was wrong. Triple quotes
     are purely a readability choice, allowing a string to span multiple
     lines. CREATE TABLE uses them because it has many columns/lines;
     DELETE stays single-quoted because it fits on one line. Zero effect
     on execution or safety either way.


## 2026-08-21 — Week 4 teach-back
- Full teach-back, out loud, no notes: code vs data distinction, why
  keyword-blocking fails, ' OR '1'='1' mechanism with concrete
  consequence (full data exposure), parametrized query mechanism
  (separate transmission, structure compiled first, value substituted
  as literal).
- Passed cleanly, first attempt. Strongest teach-back so far — fully
  grounded in hands-on demo (vulnerable_login/safe_login) rather than
  just recalled reading.
- Week 4: PASSED.

## Ground Zero Curriculum — Weeks 1-4 complete
All four weeks passed. Real gaps corrected along the way: 404/405
confusion, event loop mechanics, Decimal/float storage tension, date
format consistency, IF NOT EXISTS crash prevention, triple-quote
misconception. Ready for Week 5 full rebuild.

## 2026-08-25 — Week 5, Day 1: rebuilding lifespan from memory
- Rebuilt lifespan + FastAPI app wiring from memory, checked syntax
  against official docs (not my own code) — correctly distinguished
  my init_db() as one-time setup, NOT a shared connection pool like
  the docs' example (each endpoint opens its own fresh connection via
  get_db_connection(), lifespan just guarantees the table exists first).
- Caught my own bug: imported `from app import database` but called
  bare init_db() — would raise NameError. Fixed via importing the function
  by name.
- Raised own question: should init_db() be wrapped in try/except?
  Reasoned through it: catching-and-swallowing (Option 2) is dangerous —
  server starts looking healthy, then fails confusingly later on the
  first real request with a table-not-found error, far from the real
  cause. Catching-log-then-RE-RAISE (Option 1) is good practice —
  better diagnostics, same fail-fast behavior preserved.
- Principle: no point starting a server that can't fulfill requests —
  fail loudly and immediately beats failing silently and later.

## 2026-08-26 — Week 5, Day 2: TransactionBase rebuild, staticmethod vs classmethod
- Rebuilt TransactionBase from memory, correctly carried forward Decimal
  (validation precision) and date type (stronger validation than plain
  str, converts to string before SQLite storage — same layer-conversion
  pattern as amount).
- Added own field_validator to reject amount == 0 — went beyond the
  original Week 3 schema.
- Questioned real code's use of @classmethod, believing @staticmethod
  was more correct since the validator doesn't use cls. TESTED it
  directly (not just reasoned abstractly) — @staticmethod actually ran
  fine, caught the zero-amount error correctly.
- Checked Pydantic's official docs anyway, despite it "working" — found
  @classmethod is the documented, conventional pattern for field_validator.
- Key lesson: "it runs without error" and "it's correct/idiomatic" are
  different questions. Match documented convention even when an
  alternative technically works — consistency across a codebase matters
  more than what's minimally sufficient for one specific case.
- Date-to-string conversion before database storage: chose
  transaction.date.isoformat() over str(transaction.date). Tested both —
  currently identical output ("2026-08-26"), but isoformat() is explicit
  and purpose-built for this exact conversion, while str() relies on
  date's __str__ implementation happening to match ISO format — not
  guaranteed by the method's name or documented intent. Same
  layer-conversion pattern as float(transaction.amount).

## 2026-08-27 — Week 5, Day 3: create_transaction rebuilt
- Wrote full create_transaction from memory: connection, cursor,
  amount/date conversions, parametrized INSERT, commit, lastrowid,
  close, response. Complete and correct on first attempt.
- Caught own path typo (/transaction vs /transactions) before running —
  same mistake as Week 1's accidental path mismatch, caught faster
  this time.
- Verified create_transaction end-to-end via curl: valid request →
  200 with correct stored data; amount=0 → 422 with custom validator
  message, confirming field_validator is genuinely wired in, not just
  defined. Resolved own question on path mismatch → 404: FastAPI does
  exact string matching on registered paths, zero semantic awareness
  that "/transaction" and "/transactions" are related — same mechanism
  as Week 1's item/items mismatch, just triggered from the other direction.
- Rebuilt read_all_transactions from memory. Real bug found and confirmed
  by running it: missing leading space in " AND ..." string concatenation
  produced invalid SQL (1=1AND...), causing a 500 Internal Server Error —
  new status code, distinct from 422. Key distinction: 422 = client sent
  bad data, handled gracefully. 500 = server's own code broke in an
  unanticipated way, generic message returned to avoid leaking internals.
  Fixed by restoring the space; confirmed clean 200 afterward.

## 2026-08-28 — Week 5, Day 4: delete_transaction rebuilt, 3 real bugs found
- Wrote delete_transaction from memory. Three real bugs, all caught by
  actually running the code, not visual review:
  1. Wrong HTTP method (@app.get instead of @app.delete) — a mutation
     operation must never be GET.
  2. Malformed path string — missing closing brace in
     "/transactions/{transaction_id" — would have failed at startup.
  3. (transaction_id) is NOT a tuple — parentheses alone don't make a
     tuple in Python, only the trailing comma does. (5) is just 5;
     (5,) is a one-element tuple. sqlite3's execute() requires a real
     sequence as its second argument.
- Deeper bug found via deliberate testing (not code review): deleting a
  non-existent ID (9999) returned a false 200 "successfully deleted" —
  same silent-failure category as Week 1's update_transaction bug.
  DELETE matching zero rows isn't a SQL error, just does nothing — but
  the endpoint's response claimed otherwise. Fixed with the same
  existence-check pattern as update_transaction: SELECT first, raise
  404 if not found, then DELETE.
- Confirmed both paths: 9999 → honest 404. Real ID → genuine 200 delete.
- This endpoint is now more correct than the original audited code —
  the original delete_transaction never had this existence check either.

## 2026-08-28 — Week 5, Day 4: update_transaction rebuilt, full rebuild complete
- Wrote update_transaction from memory. Existence-check pattern applied
  confidently (third use today — delete, then update). One real bug:
  UPDATE statement was missing the WHERE clause separator, merging
  "date = ? id = ?" into invalid SQL — SET is for columns to change,
  WHERE is for targeting the row, two distinct clauses. Also correctly
  applied .isoformat() to updated_tx.date, consistent with
  create_transaction.
- Verified end-to-end: real update confirmed by reading data back
  (amount 100.0 → 200.0, not just trusting the success message) and
  9999 ghost update correctly returns 404.

## Week 5 core rebuild: COMPLETE
All five endpoints (create, read_all, delete, update, plus lifespan and
TransactionBase) rebuilt from memory, official docs only, zero
AI-generated code. Real bugs found and fixed at every single endpoint:
- lifespan: reasoned through fail-fast error handling (original addition)
- TransactionBase: staticmethod/classmethod investigation, isoformat
  vs str reasoning (original addition: zero-amount validator)
- create_transaction: path typo caught before running
- read_all_transactions: missing space caused 500 error (new status
  code learned)
- delete_transaction: 3 bugs (wrong method, malformed path, non-tuple
  argument) + added missing existence check (improvement over original)
- update_transaction: missing WHERE clause separator
Every endpoint verified by real curl requests, not visual review alone.
Two endpoints (delete, update) are now MORE correct than the original
audited code — added existence checks that weren't originally as robust.

## 2026-08-28 — Week 5 mock interview
- Q1: Full request lifecycle, correct and complete.
- Q2 (redo needed): Initial answer conflated "SQLite is fast enough" with
  the actual mechanism. Corrected: def endpoints run in FastAPI's thread
  pool automatically, keeping the event loop free regardless of how fast
  or slow the blocking call is.
- Q3: Correct, with distinction clarified — Pydantic's core job (type
  validation/conversion) vs. my own added field_validator (zero-amount
  check) are two separate things, not one.
- Q4: Correct, matches Week 4 teach-back precisely.
- Q5 (redo needed): Initial answer was thin ("migrate to Postgres").
  Redone with real reasoning: PostgreSQL for concurrent writes (SQLite's
  single-writer file-lock limitation specifically), connection pooling
  via lifespan (tied to Week 5's own lifespan understanding), pagination,
  and indexing on date/category for read performance. Honestly flagged
  own gap: same-row concurrent writes still an open question.

## GROUND ZERO CURRICULUM: COMPLETE
Weeks 1-5 all passed. Full FinTrack core rebuilt from memory, verified
by execution, with real bugs found and fixed throughout — several
endpoints now more correct than the original AI-assisted code. Ready
to proceed to Phase 2: PostgreSQL, Anthropic API integration, Railway
deployment, polish — per docs/roadmap.md.

## 2026-08-31 — Phase 2 prep: PostgreSQL installed locally
- Installed Homebrew (wasn't present), then postgresql@16 via brew.
- Started as a background service (brew services start postgresql@16) —
  runs persistently, unlike uvicorn which needs manual start each session.
- Verified connection via psql postgres — reached interactive shell
  successfully.
- Noted: default install uses "trust" authentication for local
  connections (no password required) — fine for local dev, would need
  proper auth for any real deployment. Same category as CORS
  allow_origins=["*"] — a dev-only default to remember, not fix now.
- Decision: developing against local Postgres first, Railway deployment
  (with its own separately-provisioned Postgres instance) comes later,
  as a distinct Tier 2 step — not conflating "learn Postgres" with
  "deploy to Railway."
- No FinTrack code touched today — Phase 2 proper starts tomorrow,
  1 Sept, per roadmap.md.

## 2026-09-01 — Phase 2, Day 1: psycopg first exposure
- SQLite: embedded, file-based — connecting just means pointing at a
  file on disk. PostgreSQL: client-server — connecting requires host,
  port, username, password, and a database NAME (not a file — Postgres
  manages named databases within a running server process, distinct
  from SQLite's "database = file" model).
- Placeholder syntax differs: SQLite uses ?, psycopg/Postgres uses %s —
  same underlying purpose (safe parametrized queries, data sent
  separately from query structure), different syntax per library.

## 2026-09-01 — Phase 2, Day 1: first psycopg script, verified end-to-end
- Installed psycopg[binary] in venv, confirmed correct location via
  pip show. Wrote first psycopg script from memory/docs: connect,
  create table, 3 parametrized inserts, verified via separate psql
  query — all 3 rows correctly stored, correctly ordered.
- Self-caught bugs before running: missing comma in CREATE TABLE
  (same category as last week's SQL syntax bugs), and a column-order
  mismatch in INSERT statements — correctly reasoned that %s fills
  positionally, not by name, same rule as SQLite's ?.
- Independently adopted `with` context managers (not prompted) to solve
  connection-cleanup — same underlying principle as lifespan's
  guaranteed setup/teardown, just applied per-connection instead of
  per-app-lifetime. Real transfer of a known Python pattern to new code.
- Minor PATH confusion: psql unavailable in one terminal tab, worked
  fine in another — per-session PATH issue, not a broken install.

- get_db_connection migrated to psycopg: from psycopg.rows import dict_row,
  passed as row_factory=dict_row directly to psycopg.connect() — different
  pattern from SQLite (which set row_factory AFTER connecting, on the
  conn object). Verified via real query against scratch_users: confirmed
  genuine dict-style rows returned ({'id': 1, 'name': 'Alice', 'age': 30}),
  not plain tuples.
- Corrected stale docstring — old version said "SQLite database file",
  now inaccurate given psycopg connects to a client-server database,
  not a file.
- init_db migrated to psycopg, real DECIMAL/numeric column for amount
  (Postgres has native decimal support, unlike SQLite) — verified table
  structure via psql \d transactions.
- Open question for tomorrow: should float(transaction.amount) be
  removed from create_transaction/update_transaction now that Decimal
  can be stored natively? Answer: yes, in principle — but need to verify
  psycopg actually accepts Python Decimal objects directly in parameterized
  queries before removing the conversion. Also check: does Postgres have
  a native DATE type, closing the same gap for dates that DECIMAL just
  closed for amounts?


## 2026-09-03 — Phase 2, Day 3: PostgreSQL migration complete, CRUD verified
- Replaced all SQLite ? placeholders with psycopg %s across all
endpoints (create, read_all, delete, update) and dynamic filters in
read_all_transactions.
- Removed float(transaction.amount) and transaction.date.isoformat()
from create_transaction and update_transaction — psycopg accepts Python
Decimal and date objects directly via type adapters, confirmed by
test inserting Decimal("10.00") and date(2026,9,3) which returned
as Decimal('10.00') and datetime.date(2026,9,3).
- Fixed create_transaction to use RETURNING id instead of
cursor.lastrowid (SQLite-only). New pattern: execute INSERT with
RETURNING, fetchone()["id"] before commit.
- Hit KeyError: 0 in get_financial_summary — psycopg's dict_row makes
fetchone() return dict-like, not tuple. Fixed by aliasing SUM(amount)
as total and accessing income_row["total"] / expense_row["total"].
- Also changed fallback for NULL sums from 0.0 to Decimal("0.00") to
avoid mixing Decimal and float (would raise TypeError on addition).
- Summary endpoint now returns correct values, but expenses are negative
sums (since expenses stored as negative amounts). Leaving as-is for
personal use; can document later.
- Learned why amounts appear as JSON strings: JSON has only one numeric
type (double-precision float), so FastAPI/Pydantic serialises Decimal
as string to preserve precision. Need to refine full interview answer
tomorrow (still fuzzy on client trade-off).
- Cleaned up stale docstrings/comments (SQLite → PostgreSQL, removed
float conversion comment).
- All CRUD + summary tested with curl: create, read, update, delete, and
summary all return 200 with correct data. No remaining runtime errors.

## 2026-09-09 — Phase 2, Day 4: async fundamentals + first AI service (Ollama)
- Deepened thread/process understanding: process is a running program with its own memory; 
  threads are paths of execution inside the process that share memory. 
  Threads are lighter but need careful coordination.

- Event loop is single-threaded because creating many threads is expensive. 
It switches between tasks while waiting for I/O — perfect for many slow 
network/disk operations, not for CPU-heavy work.

- Blocking vs non-blocking operations: blocking functions (`requests.get`, `time.sleep`, `cursor.execute`) 
don't return control to the event loop until finished. Non-blocking functions (`httpx.AsyncClient.get`, 
`asyncio.sleep`) are awaited and yield control, letting the event loop run other tasks.

- Why `requests.get` is safe in `def` endpoints: FastAPI runs `def` in a thread pool, so blocking only 
blocks a worker thread, not the event loop. In `async def`, blocking would freeze the whole server.

- How to tell if a function is blocking: async library functions need `await` (non-blocking); 
plain functions that just run are usually blocking.

- Installed Ollama via Homebrew, started as background service, pulled `llama3.2`. Tested with curl: returned 
`"Purchase"` for "Coffee at Starbucks".
- Built `app/categorizer.py` with `OllamaCategorizer.categorize(description) -> str`. Uses 
`httpx.AsyncClient(timeout=30.0)` to POST to `{base_url}/api/generate`. Loads `LLM_BASE_URL` and `LLM_MODEL` from `.env` 
via `load_dotenv()`. Prompt asks for single category word. Handles response with `raise_for_status()` and strips whitespace.
Tested with `test_categorizer.py`: returned "beverage" for "Coffee at Starbucks". Async external API call works end-to-end from Python.
- Environment variables: `.env` file (gitignored) holds config like `LLM_BASE_URL`; python-dotenv loads it. In Railway, 
set env vars in dashboard — no need to edit lifespan.
- Open question for next session: how to structure the categorizer so swapping Ollama for Anthropic later is minimal (likely an abstract base class or protocol).
Interview-likely topics flagged today:
  - "Why did you use httpx.AsyncClient instead of requests?" — because categorisation endpoint will be async def; requests is blocking and would freeze the event loop, while httpx.AsyncClient is non-blocking.
  - "What's the difference between a process and a thread?" — process has own memory; threads share memory within a process.
  - "How do you keep API keys or config out of code?" — environment variables, loaded via dotenv locally and platform dashboard in production.
