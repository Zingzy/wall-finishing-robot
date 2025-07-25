"""Trajectory API routes for v1."""

import time
from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import Session
from loguru import logger

from src.models.trajectory import (
    TrajectoryRepository,
    get_session,
)
from src.schemas.trajectory import (
    TrajectoryCreateRequest,
    TrajectoryCreateResponse,
    TrajectoryResponse,
    TrajectoryListResponse,
    TrajectoryListItem,
    DeleteResponse,
    ErrorResponse,
    ObstacleSchema,
)
from src.services.path_planning import generate_trajectory


router = APIRouter(prefix="/trajectories", tags=["trajectories"])


@router.post(
    "",
    response_model=TrajectoryCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new trajectory",
    description="Generate and store a new trajectory for wall finishing with obstacles",
    responses={
        201: {"description": "Trajectory created successfully"},
        400: {"model": ErrorResponse, "description": "Invalid input parameters"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def create_trajectory(
    request: TrajectoryCreateRequest, session: Session = Depends(get_session)
) -> TrajectoryCreateResponse:
    """Create a new trajectory with wall dimensions and obstacles."""
    start_time = time.time()

    try:
        logger.info(
            f"Creating trajectory for {request.wall_width}x{request.wall_height}m wall "
            f"with {len(request.obstacles)} obstacles"
        )

        # Convert Pydantic obstacles to dict format
        obstacles_dict = [obs.model_dump() for obs in request.obstacles]

        # Generate trajectory using path planning service
        path, metadata = generate_trajectory(
            wall_width=request.wall_width,
            wall_height=request.wall_height,
            obstacles=obstacles_dict,
            cell_size=request.cell_size,
        )

        # Store in database
        trajectory_data = {
            "wall_width": request.wall_width,
            "wall_height": request.wall_height,
            "obstacles": obstacles_dict,
            "path": path,
        }

        trajectory = TrajectoryRepository.create_trajectory(session, trajectory_data)

        # Ensure trajectory was created with an ID
        assert trajectory.id is not None, "Trajectory ID should not be None after creation"

        # Prepare response
        response = TrajectoryCreateResponse(
            id=trajectory.id,
            wall_width=trajectory.wall_width,
            wall_height=trajectory.wall_height,
            obstacles=[ObstacleSchema(**obs) for obs in obstacles_dict],
            path=path,
            metadata=metadata,
        )

        execution_time = time.time() - start_time
        logger.info(f"Created trajectory ID {trajectory.id} in {execution_time:.3f} seconds")

        return response

    except ValueError as e:
        logger.warning(f"Invalid input for trajectory creation: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating trajectory: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create trajectory")


@router.get(
    "/{trajectory_id}",
    response_model=TrajectoryResponse,
    summary="Get trajectory by ID",
    description="Retrieve a stored trajectory by its unique identifier",
    responses={
        200: {"description": "Trajectory retrieved successfully"},
        404: {"model": ErrorResponse, "description": "Trajectory not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def get_trajectory(
    trajectory_id: int, session: Session = Depends(get_session)
) -> TrajectoryResponse:
    """Get trajectory by ID."""
    start_time = time.time()

    try:
        logger.debug(f"Retrieving trajectory {trajectory_id}")

        trajectory = TrajectoryRepository.get_trajectory(session, trajectory_id)
        if not trajectory:
            logger.warning(f"Trajectory {trajectory_id} not found")
            raise HTTPException(status_code=404, detail="Trajectory not found")

        # Ensure trajectory has an ID (should always be true from database)
        assert trajectory.id is not None, "Trajectory from database should have an ID"

        # Parse JSON data
        obstacles = trajectory.get_obstacles()
        path = trajectory.get_path()

        response = TrajectoryResponse(
            id=trajectory.id,
            wall_width=trajectory.wall_width,
            wall_height=trajectory.wall_height,
            obstacles=[ObstacleSchema(**obs) for obs in obstacles],
            path=path,
        )

        execution_time = time.time() - start_time
        logger.debug(f"Retrieved trajectory {trajectory_id} in {execution_time:.3f} seconds")

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving trajectory {trajectory_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve trajectory")


@router.get(
    "",
    response_model=TrajectoryListResponse,
    summary="List all trajectories",
    description="Get a list of all stored trajectories with basic metadata",
    responses={
        200: {"description": "Trajectories retrieved successfully"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def list_trajectories(
    skip: int = 0, limit: int = 100, session: Session = Depends(get_session)
) -> TrajectoryListResponse:
    """List all trajectories with pagination."""
    start_time = time.time()

    try:
        logger.debug(f"Listing trajectories with skip={skip}, limit={limit}")

        trajectories = TrajectoryRepository.get_all_trajectories(session, skip, limit)

        trajectory_items = []
        for traj in trajectories:
            # Ensure trajectory has an ID (should always be true from database)
            assert traj.id is not None, "Trajectory from database should have an ID"
            
            obstacles = traj.get_obstacles()
            path = traj.get_path()

            trajectory_items.append(
                TrajectoryListItem(
                    id=traj.id,
                    wall_width=traj.wall_width,
                    wall_height=traj.wall_height,
                    obstacle_count=len(obstacles),
                    path_points=len(path),
                )
            )

        response = TrajectoryListResponse(
            trajectories=trajectory_items, total=len(trajectory_items)
        )

        execution_time = time.time() - start_time
        logger.debug(f"Listed {len(trajectory_items)} trajectories in {execution_time:.3f} seconds")

        return response

    except Exception as e:
        logger.error(f"Error listing trajectories: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list trajectories")


@router.delete(
    "/{trajectory_id}",
    response_model=DeleteResponse,
    summary="Delete trajectory by ID",
    description="Delete a stored trajectory by its unique identifier",
    responses={
        200: {"description": "Trajectory deleted successfully"},
        404: {"model": ErrorResponse, "description": "Trajectory not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def delete_trajectory(
    trajectory_id: int, session: Session = Depends(get_session)
) -> DeleteResponse:
    """Delete trajectory by ID."""
    start_time = time.time()

    try:
        logger.info(f"Deleting trajectory {trajectory_id}")

        success = TrajectoryRepository.delete_trajectory(session, trajectory_id)
        if not success:
            logger.warning(f"Trajectory {trajectory_id} not found for deletion")
            raise HTTPException(status_code=404, detail="Trajectory not found")

        response = DeleteResponse(
            message="Trajectory deleted successfully", deleted_id=trajectory_id
        )

        execution_time = time.time() - start_time
        logger.info(f"Deleted trajectory {trajectory_id} in {execution_time:.3f} seconds")

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting trajectory {trajectory_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete trajectory")
