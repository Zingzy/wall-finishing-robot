"""Main router for API v1."""

from fastapi import APIRouter
from .trajectories import router as trajectories_router

# Create the main v1 router
router = APIRouter(prefix="/api/v1")

# Include all route modules
router.include_router(trajectories_router)
