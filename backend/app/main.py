from fastapi import FastAPI

from api.v1 import api_router
from core.config import settings

app = FastAPI()

app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
