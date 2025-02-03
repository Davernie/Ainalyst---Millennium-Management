from fastapi import APIRouter
from app.services.health_service import check_health

router = APIRouter()

@router.get("/health", status_code=200)
def health_check():
    return check_health()
