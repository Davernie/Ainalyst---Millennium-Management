
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.app.api.v1 import api_router
from backend.app.database.database import init_db,get_db

from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.v1.endpoints import update_env

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up... Connecting to DB and ensuring table exists.")
    init_db()
    yield
    print("Shutting down...")

# Attach lifespan to FastAPI
app = FastAPI(lifespan=lifespan)


app.include_router(api_router)
app.include_router(update_env.router, prefix="/api/v1")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000","http://localhost",],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


print("📌 Available routes:")
for route in app.routes:
    print(f"{route.methods} {route.path}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)

