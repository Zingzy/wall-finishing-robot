"""Database models for trajectory storage using SQLModel."""

from typing import Optional, List, Dict, Any, Generator
from sqlmodel import SQLModel, Field, create_engine, Session, select
from sqlalchemy import Engine
import json
from loguru import logger
from src.config.loader import get_settings


class TrajectoryBase(SQLModel):
    """Base model for trajectory with common fields."""

    wall_width: float = Field(..., description="Width of the wall in meters")
    wall_height: float = Field(..., description="Height of the wall in meters")
    obstacles: str = Field(..., description="JSON string of obstacles list")
    path: str = Field(..., description="JSON string of trajectory path")
    obstacles_count: int = Field(..., description="Number of obstacles")
    path_points: int = Field(..., description="Number of points in trajectory path")


class Trajectory(TrajectoryBase, table=True):
    """Database model for storing robot trajectories."""

    __tablename__ = "trajectories"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)

    def __repr__(self) -> str:
        return f"<Trajectory(id={self.id}, wall={self.wall_width}x{self.wall_height})>"

    @classmethod
    def create_with_json(
        cls,
        wall_width: float,
        wall_height: float,
        obstacles: List[Dict[str, float]],
        path: List[List[int]],
    ) -> "Trajectory":
        """Create a trajectory instance with JSON serialization."""
        return cls(
            wall_width=wall_width,
            wall_height=wall_height,
            obstacles=json.dumps(obstacles),
            path=json.dumps(path),
            obstacles_count=len(obstacles),
            path_points=len(path),
        )

    def get_obstacles(self) -> List[Dict[str, float]]:
        """Parse obstacles from JSON string."""
        try:
            obstacles: List[Dict[str, float]] = json.loads(self.obstacles)
            return obstacles
        except json.JSONDecodeError:
            logger.error(f"Failed to parse obstacles JSON for trajectory {self.id}")
            return []

    def get_path(self) -> List[List[int]]:
        """Parse path from JSON string."""
        try:
            path: List[List[int]] = json.loads(self.path)
            return path
        except json.JSONDecodeError:
            logger.error(f"Failed to parse path JSON for trajectory {self.id}")
            return []


def get_engine() -> Engine:
    """Get database engine with current settings."""
    settings = get_settings()
    return create_engine(settings.database.url, echo=settings.database.echo)


engine = get_engine()


def create_db_and_tables() -> None:
    """Create database and tables."""
    try:
        SQLModel.metadata.create_all(engine)

        # Create index on id for efficient retrieval (primary key already indexed)
        # But let's ensure we have the table created
        logger.info("Database and tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database: {e}")
        raise


def get_session() -> Generator[Session, None, None]:
    """Get database session."""
    with Session(engine) as session:
        yield session


# Database operations
class TrajectoryRepository:
    """Repository for trajectory database operations."""

    @staticmethod
    def create_trajectory(session: Session, trajectory_data: Dict[str, Any]) -> Trajectory:
        """Create a new trajectory in the database."""
        trajectory = Trajectory.create_with_json(
            wall_width=trajectory_data["wall_width"],
            wall_height=trajectory_data["wall_height"],
            obstacles=trajectory_data["obstacles"],
            path=trajectory_data["path"],
        )

        session.add(trajectory)
        session.commit()
        session.refresh(trajectory)

        return trajectory

    @staticmethod
    def get_trajectory(session: Session, trajectory_id: int) -> Optional[Trajectory]:
        """Get trajectory by ID."""
        trajectory = session.get(Trajectory, trajectory_id)
        if trajectory:
            logger.debug(f"Retrieved trajectory {trajectory_id}")
        else:
            logger.warning(f"Trajectory {trajectory_id} not found")
        return trajectory

    @staticmethod
    def get_all_trajectories(
        session: Session, skip: int = 0, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get all trajectories with pagination."""
        statement = (
            select(  # type: ignore[call-overload]
                Trajectory.id,
                Trajectory.wall_width,
                Trajectory.wall_height,
                Trajectory.obstacles_count,
                Trajectory.path_points,
            )
            .offset(skip)
            .limit(limit)
        )
        trajectories = session.exec(statement).all()
        logger.debug(f"Retrieved {len(trajectories)} trajectories")
        return [
            {
                "id": traj[0],
                "wall_width": traj[1],
                "wall_height": traj[2],
                "obstacles_count": traj[3],
                "path_points": traj[4],
            }
            for traj in trajectories
        ]

    @staticmethod
    def delete_trajectory(session: Session, trajectory_id: int) -> bool:
        """Delete trajectory by ID."""
        trajectory = session.get(Trajectory, trajectory_id)
        if trajectory:
            session.delete(trajectory)
            session.commit()
            logger.info(f"Deleted trajectory {trajectory_id}")
            return True
        else:
            logger.warning(f"Trajectory {trajectory_id} not found for deletion")
            return False

    @staticmethod
    def trajectory_exists(session: Session, trajectory_id: int) -> bool:
        """Check if trajectory exists."""
        trajectory = session.get(Trajectory, trajectory_id)
        return trajectory is not None
