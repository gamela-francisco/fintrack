from fastapi import FastAPI

# Initialise the FastAPI application instance
app = FastAPI()

# We use this decorator to map HTTP GET requests sent to the root URL ("/")
# directly to the function defined immediately below it.
@app.get("/")
def read_root() -> dict:
    """
    Health check endpoint that returns a simple welcome message.

    This allows clients or deployment platforms to verify that the backend
    server is up and running correctly.
    """
    return {"message": "Welcome to FinTrack API"}
