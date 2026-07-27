from fastapi import APIRouter

from app.auth import CurrentUser, DbSession
from app.schemas import DashboardStats
from app.services import interview as interview_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
def dashboard_stats(user: CurrentUser, db: DbSession):
    return DashboardStats(**interview_service.build_dashboard(db, user))
