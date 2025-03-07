# main.py
from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.v1 import api_router
from database.database import init_db,get_db

from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up... Connecting to DB and ensuring table exists.")
    init_db()  # Ensure table exists on startup
    yield  # Application runs
    print("Shutting down...")

# Attach lifespan to FastAPI
app = FastAPI(lifespan=lifespan)

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000","http://localhost",],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
print("📌 Manually testing database connection...")
db = next(get_db())  # Manually get a session

try:
    print("✅ Successfully created a database session!")
except Exception as e:
    print(f"❌ Failed to create session: {e}")
finally:
    db.close()

print("📌 Available routes:")
for route in app.routes:
    print(f"{route.methods} {route.path}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)

