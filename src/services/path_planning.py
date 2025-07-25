"""Path planning service for wall finishing robot trajectory generation."""

import numpy as np
from typing import List, Dict, Any, Tuple
from loguru import logger


def create_grid(wall_width: float, wall_height: float, cell_size: float = 0.1) -> np.ndarray:
    """
    Create a boolean grid representing the wall.

    Args:
        wall_width: Width of the wall in meters
        wall_height: Height of the wall in meters
        cell_size: Size of each grid cell in meters (default: 0.1m = 10cm)

    Returns:
        np.ndarray: Boolean grid where True represents obstacles, False represents free space
    """
    rows = int(np.ceil(wall_height / cell_size))
    cols = int(np.ceil(wall_width / cell_size))
    logger.debug(
        f"Created grid with {rows} rows and {cols} cols for wall {wall_width}x{wall_height}m"
    )
    return np.zeros((rows, cols), dtype=bool)


def mark_obstacles(
    grid: np.ndarray, obstacles: List[Dict[str, float]], cell_size: float = 0.1
) -> None:
    """
    Mark obstacles on the grid.

    Args:
        grid: Boolean grid to mark obstacles on
        obstacles: List of obstacle dictionaries with x, y, width, height keys
        cell_size: Size of each grid cell in meters
    """
    for i, obs in enumerate(obstacles):
        x, y, w, h = obs["x"], obs["y"], obs["width"], obs["height"]
        row_start = int(y / cell_size)
        row_end = int((y + h) / cell_size)
        col_start = int(x / cell_size)
        col_end = int((x + w) / cell_size)

        # Ensure bounds are within grid
        row_start = max(0, row_start)
        row_end = min(grid.shape[0], row_end)
        col_start = max(0, col_start)
        col_end = min(grid.shape[1], col_end)

        grid[row_start : row_end + 1, col_start : col_end + 1] = True
        logger.debug(
            f"Marked obstacle {i + 1} at rows {row_start}-{row_end}, cols {col_start}-{col_end}"
        )


def generate_path(grid: np.ndarray) -> List[List[int]]:
    """
    Generate a zigzag (Boustrophedon-like) path covering all free cells.

    Args:
        grid: Boolean grid where True represents obstacles, False represents free space

    Returns:
        List[List[int]]: Path as list of [row, col] coordinates
    """
    rows, cols = grid.shape
    path = []

    for row in range(rows):
        if row % 2 == 0:
            # Even rows: left to right
            for col in range(cols):
                if not grid[row, col]:
                    path.append([row, col])
        else:
            # Odd rows: right to left
            for col in range(cols - 1, -1, -1):
                if not grid[row, col]:
                    path.append([row, col])

    logger.info(f"Generated path with {len(path)} points covering {rows}x{cols} grid")
    return path


def generate_trajectory(
    wall_width: float, wall_height: float, obstacles: List[Dict[str, float]], cell_size: float = 0.1
) -> Tuple[List[List[int]], Dict[str, Any]]:
    """
    Generate complete trajectory for wall finishing with obstacles.

    Args:
        wall_width: Width of the wall in meters
        wall_height: Height of the wall in meters
        obstacles: List of obstacle dictionaries with x, y, width, height keys
        cell_size: Size of each grid cell in meters

    Returns:
        Tuple[List[List[int]], Dict[str, Any]]: Path coordinates and metadata
    """
    logger.info("Starting trajectory generation")

    # Validate inputs
    if wall_width <= 0 or wall_height <= 0:
        raise ValueError("Wall dimensions must be positive")

    if cell_size <= 0:
        raise ValueError("Cell size must be positive")

    # Validate obstacles are within wall bounds
    for i, obs in enumerate(obstacles):
        if (
            obs["x"] < 0
            or obs["y"] < 0
            or obs["x"] + obs["width"] > wall_width
            or obs["y"] + obs["height"] > wall_height
        ):
            raise ValueError(
                f"Obstacle {i + 1} (x={obs['x']}, y={obs['y']}, w={obs['width']}, h={obs['height']}) is outside wall boundaries (wall_width={wall_width}, wall_height={wall_height})"
            )

        if obs["width"] <= 0 or obs["height"] <= 0:
            raise ValueError(
                f"Obstacle {i + 1} (x={obs['x']}, y={obs['y']}, w={obs['width']}, h={obs['height']}) has non-positive dimensions"
            )

    # Generate trajectory
    grid = create_grid(wall_width, wall_height, cell_size)
    mark_obstacles(grid, obstacles, cell_size)
    path = generate_path(grid)

    # Calculate statistics
    total_cells = grid.size
    obstacle_cells = np.sum(grid)
    free_cells = total_cells - obstacle_cells
    coverage_percentage = (len(path) / free_cells) * 100 if free_cells > 0 else 0

    metadata = {
        "total_cells": int(total_cells),
        "obstacle_cells": int(obstacle_cells),
        "free_cells": int(free_cells),
        "path_points": len(path),
        "coverage_percentage": float(coverage_percentage),
        "grid_dimensions": {"rows": int(grid.shape[0]), "cols": int(grid.shape[1])},
        "cell_size": cell_size,
    }

    logger.info(f"Trajectory generated: {len(path)} points, {coverage_percentage:.1f}% coverage")
    return path, metadata
