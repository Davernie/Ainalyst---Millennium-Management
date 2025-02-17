from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.v1 import api_router
from database.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up... Connecting to DB and ensuring table exists.")
    init_db()  # Ensure table exists on startup
    yield  # Application runs
    print("Shutting down...")

# Attach lifespan to FastAPI
app = FastAPI(lifespan=lifespan)

app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
