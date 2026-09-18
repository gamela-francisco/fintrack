# FinTrack
A personal finance REST API that stores transactions in PostgreSQL and uses
a local LLM to categorise them 

## What It Does
- Create, read, update, delete transactions stored in PostgreSQL
- Filter transactions by description or category
- Automatically categorise a transaction's description using a local LLM
- Views total for income, expenses, and net balance

# Why I Built It
I used to track my expenses in Google Sheets, and I wanted to see 
if I could build my own version with the customisations I actually 
wanted — and learn how to fit an AI feature into a real backend 
while I was at it.

FinTrack also became a way to stay sharp over summer and revisit 
first-year concepts in a deeper context. The most valuable part 
was migrating the data layer from SQLite to PostgreSQL mid-project: 
it forced me to actually understand the trade-offs between an 
embedded database and a client-server one, 
and to rewrite every endpoint accordingly rather than assume the 
two were interchangeable.

# Tech Stack
- **FastAPI** — the web framework responsible for routing, request
  handling, async support, and automatic OpenAPI docs.
- **PostgreSQL** — a client-server database with native DATE and NUMERIC
  types, chosen over SQLite for accurate dates and monetary values.
- **psycopg** — the PostgreSQL driver. Talks to Postgres from Python and
  handles type adaptation between Python objects and SQL values.
- **Pydantic** — the validation layer. Validates and coerces incoming
  JSON at the API boundary before endpoints run.
- **httpx** — the async HTTP client used to call the LLM without blocking
  the event loop.
- **Ollama** — the local LLM runtime powering categorisation. The
  categoriser is abstracted behind a BaseCategorizer interface, so
  swapping providers is a config change, not a rewrite.
- **python-dotenv** — loads .env into the environment during development
  so config stays out of the codebase.

# Architecture


# Key Design Decisions

# What I'd Do Next

# What I deliberately didn't do

# How to Run It Locally
