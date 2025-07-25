"""Pydantic schemas for trajectory API validation and responses."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, model_validator, ConfigDict


class ObstacleSchema(BaseModel):
    """Schema for obstacle validation."""

    x: float = Field(..., ge=0, description="X coordinate in meters (must be >= 0)")
    y: float = Field(..., ge=0, description="Y coordinate in meters (must be >= 0)")
    width: float = Field(..., gt=0, description="Width in meters (must be > 0)")
    height: float = Field(..., gt=0, description="Height in meters (must be > 0)")

    model_config = ConfigDict(
        json_schema_extra={"example": {"x": 1.0, "y": 1.0, "width": 0.25, "height": 0.25}}
    )


class TrajectoryCreateRequest(BaseModel):
    """Schema for trajectory creation request."""

    wall_width: float = Field(..., gt=0, description="Width of the wall in meters (must be > 0)")
    wall_height: float = Field(..., gt=0, description="Height of the wall in meters (must be > 0)")
    obstacles: List[ObstacleSchema] = Field(
        default_factory=list, description="List of rectangular obstacles"
    )

    @model_validator(mode="after")
    def validate_obstacles_within_wall(self) -> "TrajectoryCreateRequest":
        """Validate that all obstacles fit within the wall boundaries."""
        for i, obstacle in enumerate(self.obstacles):
            # Check if obstacle fits within wall
            if obstacle.x + obstacle.width > self.wall_width:
                raise ValueError(
                    f"Obstacle {i + 1} extends beyond wall width: "
                    f"x({obstacle.x}) + width({obstacle.width}) = {obstacle.x + obstacle.width} > {self.wall_width}"
                )

            if obstacle.y + obstacle.height > self.wall_height:
                raise ValueError(
                    f"Obstacle {i + 1} extends beyond wall height: "
                    f"y({obstacle.y}) + height({obstacle.height}) = {obstacle.y + obstacle.height} > {self.wall_height}"
                )

        return self

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "wall_width": 5.0,
                "wall_height": 5.0,
                "obstacles": [
                    {"x": 1.0, "y": 1.0, "width": 0.25, "height": 0.25},
                    {"x": 3.0, "y": 2.0, "width": 0.25, "height": 0.25},
                    {"x": 2.0, "y": 3.5, "width": 0.25, "height": 0.25},
                ],
            }
        }
    )


class TrajectoryGetResponse(BaseModel):
    """Schema for trajectory response."""

    id: int = Field(..., description="Unique trajectory identifier")
    wall_width: float = Field(..., description="Width of the wall in meters")
    wall_height: float = Field(..., description="Height of the wall in meters")
    obstacles: List[ObstacleSchema] = Field(..., description="List of obstacles")
    path: List[List[int]] = Field(..., description="Trajectory path as [row, col] coordinates")
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional trajectory metadata"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "wall_width": 5.0,
                "wall_height": 5.0,
                "obstacles": [{"x": 1.0, "y": 1.0, "width": 0.25, "height": 0.25}],
                "path": [[0, 0], [0, 1], [0, 2]],
                "metadata": {
                    "total_cells": 2500,
                    "obstacle_cells": 25,
                    "free_cells": 2475,
                    "path_points": 2473,
                    "coverage_percentage": 99.9,
                },
            }
        }
    )


class TrajectoryCreateResponse(BaseModel):
    """Schema for trajectory creation response."""

    id: int = Field(..., description="Unique trajectory identifier")
    wall_width: float = Field(..., description="Width of the wall in meters")
    wall_height: float = Field(..., description="Height of the wall in meters")
    obstacles: List[ObstacleSchema] = Field(..., description="List of obstacles")
    path: List[List[int]] = Field(..., description="Trajectory path as [row, col] coordinates")
    metadata: Dict[str, Any] = Field(..., description="Trajectory generation metadata")
    execution_time: float = Field(
        ..., description="Time taken to generate the trajectory in seconds"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "wall_width": 5.0,
                "wall_height": 5.0,
                "obstacles": [{"x": 1.0, "y": 1.0, "width": 0.25, "height": 0.25}],
                "path": [[0, 0], [0, 1], [0, 2]],
                "metadata": {
                    "total_cells": 2500,
                    "obstacle_cells": 25,
                    "free_cells": 2475,
                    "path_points": 2473,
                    "coverage_percentage": 99.9,
                    "grid_dimensions": {"rows": 50, "cols": 50},
                    "cell_size": 0.1,
                },
                "execution_time": 0.123,
            }
        }
    )


class TrajectoryListItem(BaseModel):
    """Schema for trajectory list item (basic metadata)."""

    id: int = Field(..., description="Unique trajectory identifier")
    wall_width: float = Field(..., description="Width of the wall in meters")
    wall_height: float = Field(..., description="Height of the wall in meters")
    obstacle_count: int = Field(..., description="Number of obstacles")
    path_points: int = Field(..., description="Number of points in trajectory path")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "wall_width": 5.0,
                "wall_height": 5.0,
                "obstacle_count": 3,
                "path_points": 2473,
            }
        }
    )


class TrajectoryListResponse(BaseModel):
    """Schema for trajectory list response."""

    trajectories: List[TrajectoryListItem] = Field(..., description="List of trajectory metadata")
    total: int = Field(..., description="Total number of trajectories")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "trajectories": [
                    {
                        "id": 1,
                        "wall_width": 5.0,
                        "wall_height": 5.0,
                        "obstacle_count": 3,
                        "path_points": 2473,
                    }
                ],
                "total": 1,
            }
        }
    )


class ErrorResponse(BaseModel):
    """Schema for error responses."""

    detail: str = Field(..., description="Error message")

    model_config = ConfigDict(json_schema_extra={"example": {"detail": "Trajectory not found"}})


class DeleteResponse(BaseModel):
    """Schema for delete operation response."""

    message: str = Field(..., description="Success message")
    deleted_id: int = Field(..., description="ID of deleted trajectory")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"message": "Trajectory deleted successfully", "deleted_id": 1}
        }
    )
