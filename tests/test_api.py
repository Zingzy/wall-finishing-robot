"""Comprehensive tests for Wall Finishing Robot API endpoints."""

import pytest
import time
from fastapi.testclient import TestClient


# Trajectory creation tests
def test_create_valid_trajectory(client: TestClient):
    """Test creating a valid trajectory with standard 5x5 wall and 3 obstacles."""
    payload = {
        "wall_width": 5.0,
        "wall_height": 5.0,
        "obstacles": [
            {"x": 1.0, "y": 1.0, "width": 0.25, "height": 0.25},
            {"x": 3.0, "y": 2.0, "width": 0.25, "height": 0.25},
            {"x": 2.0, "y": 3.5, "width": 0.25, "height": 0.25},
        ],
    }

    start_time = time.perf_counter()
    response = client.post("/api/v1/trajectories", json=payload)
    end_time = time.perf_counter()

    # Check response time (should be < 1s)
    response_time = end_time - start_time
    assert response_time < 1.0, f"Response time {response_time:.3f}s exceeds 1s limit"

    assert response.status_code == 201
    data = response.json()

    # Verify response structure
    assert "id" in data
    assert isinstance(data["id"], int)
    assert data["wall_width"] == 5.0
    assert data["wall_height"] == 5.0
    assert len(data["obstacles"]) == 3
    assert isinstance(data["path"], list)
    assert len(data["path"]) > 2400  # Should be around 2473 points

    # Verify metadata
    assert "metadata" in data
    metadata = data["metadata"]
    assert metadata["total_cells"] == 2500  # 50x50 grid
    assert metadata["coverage_percentage"] > 95.0  # Should cover most free cells
    assert metadata["grid_dimensions"]["rows"] == 50
    assert metadata["grid_dimensions"]["cols"] == 50


def test_create_trajectory_no_obstacles(client: TestClient):
    """Test creating trajectory without obstacles."""
    payload = {"wall_width": 2.0, "wall_height": 2.0, "obstacles": []}

    response = client.post("/api/v1/trajectories", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert len(data["obstacles"]) == 0
    assert len(data["path"]) == 400  # 20x20 grid = 400 cells


def test_create_trajectory_single_obstacle(client: TestClient):
    """Test creating trajectory with single obstacle."""
    payload = {
        "wall_width": 3.0,
        "wall_height": 3.0,
        "obstacles": [{"x": 1.0, "y": 1.0, "width": 1.0, "height": 1.0}],
    }

    response = client.post("/api/v1/trajectories", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert len(data["obstacles"]) == 1
    assert data["metadata"]["obstacle_cells"] == 121


def test_invalid_wall_dimensions(client: TestClient):
    """Test validation of wall dimensions."""
    # Negative width
    payload = {"wall_width": -1.0, "wall_height": 5.0, "obstacles": []}
    response = client.post("/api/v1/trajectories", json=payload)
    assert response.status_code == 422  # Validation error

    # Zero height
    payload = {"wall_width": 5.0, "wall_height": 0.0, "obstacles": []}
    response = client.post("/api/v1/trajectories", json=payload)
    assert response.status_code == 422


def test_obstacles_outside_wall(client: TestClient):
    """Test validation of obstacles outside wall boundaries."""
    payload = {
        "wall_width": 5.0,
        "wall_height": 5.0,
        "obstacles": [
            {"x": 4.5, "y": 1.0, "width": 1.0, "height": 0.5}  # Extends beyond wall width
        ],
    }

    response = client.post("/api/v1/trajectories", json=payload)
    assert response.status_code == 422
    assert "extends beyond wall width" in response.json()["detail"][0]["msg"]


def test_invalid_obstacle_dimensions(client: TestClient):
    """Test validation of obstacle dimensions."""
    # Negative obstacle width
    payload = {
        "wall_width": 5.0,
        "wall_height": 5.0,
        "obstacles": [{"x": 1.0, "y": 1.0, "width": -0.5, "height": 0.5}],
    }
    response = client.post("/api/v1/trajectories", json=payload)
    assert response.status_code == 422

    # Zero obstacle height
    payload = {
        "wall_width": 5.0,
        "wall_height": 5.0,
        "obstacles": [{"x": 1.0, "y": 1.0, "width": 0.5, "height": 0.0}],
    }
    response = client.post("/api/v1/trajectories", json=payload)
    assert response.status_code == 422


# Trajectory retrieval tests
def test_get_existing_trajectory(client: TestClient):
    """Test retrieving an existing trajectory."""
    # First create a trajectory
    payload = {
        "wall_width": 3.0,
        "wall_height": 3.0,
        "obstacles": [{"x": 1.0, "y": 1.0, "width": 0.5, "height": 0.5}],
    }

    create_response = client.post("/api/v1/trajectories", json=payload)
    assert create_response.status_code == 201
    trajectory_id = create_response.json()["id"]

    # Now retrieve it
    start_time = time.perf_counter()
    response = client.get(f"/api/v1/trajectories/{trajectory_id}")
    end_time = time.perf_counter()

    # Check response time
    response_time = end_time - start_time
    assert response_time < 1.0, f"Response time {response_time:.3f}s exceeds 1s limit"

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == trajectory_id
    assert data["wall_width"] == 3.0
    assert data["wall_height"] == 3.0
    assert len(data["obstacles"]) == 1
    assert isinstance(data["path"], list)


def test_get_nonexistent_trajectory(client: TestClient):
    """Test retrieving a non-existent trajectory."""
    response = client.get("/api/v1/trajectories/99999")
    assert response.status_code == 404


def test_get_trajectory_invalid_id(client: TestClient):
    """Test retrieving trajectory with invalid ID format."""
    response = client.get("/api/v1/trajectories/invalid")
    assert response.status_code == 422  # Validation error for non-integer ID


# Trajectory listing tests
def test_list_empty_trajectories(client: TestClient):
    """Test listing when no trajectories exist."""
    response = client.get("/api/v1/trajectories")
    assert response.status_code == 200

    data = response.json()
    assert data["trajectories"] == []
    assert data["total"] == 0


def test_list_multiple_trajectories(client: TestClient):
    """Test listing multiple trajectories."""
    # Create several trajectories
    trajectories_data = [
        {"wall_width": 2.0, "wall_height": 2.0, "obstacles": []},
        {
            "wall_width": 3.0,
            "wall_height": 3.0,
            "obstacles": [{"x": 1.0, "y": 1.0, "width": 0.5, "height": 0.5}],
        },
        {"wall_width": 4.0, "wall_height": 4.0, "obstacles": []},
    ]

    created_ids = []
    for payload in trajectories_data:
        response = client.post("/api/v1/trajectories", json=payload)
        assert response.status_code == 201
        created_ids.append(response.json()["id"])

    # List all trajectories
    start_time = time.perf_counter()
    response = client.get("/api/v1/trajectories")
    end_time = time.perf_counter()

    # Check response time
    response_time = end_time - start_time
    assert response_time < 1.0, f"Response time {response_time:.3f}s exceeds 1s limit"

    assert response.status_code == 200
    data = response.json()

    assert len(data["trajectories"]) == 3
    assert data["total"] == 3

    # Verify trajectory metadata
    for traj in data["trajectories"]:
        assert "id" in traj
        assert "wall_width" in traj
        assert "wall_height" in traj
        assert "obstacle_count" in traj
        assert "path_points" in traj
        assert traj["id"] in created_ids


# Trajectory deletion tests
def test_delete_existing_trajectory(client: TestClient):
    """Test deleting an existing trajectory."""
    # Create a trajectory
    payload = {"wall_width": 2.0, "wall_height": 2.0, "obstacles": []}

    create_response = client.post("/api/v1/trajectories", json=payload)
    assert create_response.status_code == 201
    trajectory_id = create_response.json()["id"]

    # Delete it
    start_time = time.perf_counter()
    response = client.delete(f"/api/v1/trajectories/{trajectory_id}")
    end_time = time.perf_counter()

    # Check response time
    response_time = end_time - start_time
    assert response_time < 1.0, f"Response time {response_time:.3f}s exceeds 1s limit"

    assert response.status_code == 200
    data = response.json()

    assert "successfully" in data["message"].lower()
    assert data["deleted_id"] == trajectory_id

    # Verify it's actually deleted
    get_response = client.get(f"/api/v1/trajectories/{trajectory_id}")
    assert get_response.status_code == 404


def test_delete_nonexistent_trajectory(client: TestClient):
    """Test deleting a non-existent trajectory."""
    response = client.delete("/api/v1/trajectories/99999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_delete_trajectory_invalid_id(client: TestClient):
    """Test deleting trajectory with invalid ID format."""
    response = client.delete("/api/v1/trajectories/invalid")
    assert response.status_code == 422  # Validation error


# Performance tests
@pytest.mark.parametrize("wall_width, wall_height", [(10.0, 10.0), (20.0, 20.0), (30.0, 30.0)])
def test_large_wall_performance(client: TestClient, wall_width: float, wall_height: float):
    """Test performance with larger wall dimensions."""
    payload = {
        "wall_width": wall_width,
        "wall_height": wall_height,
        "obstacles": [
            {"x": 2.0, "y": 2.0, "width": 1.0, "height": 1.0},
            {"x": 5.0, "y": 5.0, "width": 1.0, "height": 1.0},
            {"x": 8.0, "y": 8.0, "width": 1.0, "height": 1.0},
        ],
    }

    start_time = time.perf_counter()
    response = client.post("/api/v1/trajectories", json=payload)
    end_time = time.perf_counter()

    response_time = end_time - start_time
    assert response_time < 1.0, f"Large wall response time {response_time:.3f}s exceeds 1s limit"

    assert response.status_code == 201
    data = response.json()
    assert data["metadata"]["total_cells"] == int(wall_width / 0.1) * int(
        wall_height / 0.1
    )  # Exact calculation of the cells


# End-to-end workflow test
def test_complete_workflow(client: TestClient):
    """Test complete create -> retrieve -> list -> delete workflow."""
    # 1. Create trajectory
    payload = {
        "wall_width": 5.0,
        "wall_height": 5.0,
        "obstacles": [
            {"x": 1.0, "y": 1.0, "width": 0.25, "height": 0.25},
            {"x": 3.0, "y": 2.0, "width": 0.25, "height": 0.25},
            {"x": 2.0, "y": 3.5, "width": 0.25, "height": 0.25},
        ],
    }

    create_response = client.post("/api/v1/trajectories", json=payload)
    assert create_response.status_code == 201

    trajectory_id = create_response.json()["id"]
    expected_path_length = create_response.json()["metadata"]["path_points"]

    # Verify approximately correct number of points for 5x5 wall with 3 obstacles
    assert expected_path_length > 2400
    assert expected_path_length < 2500

    # 2. Retrieve trajectory
    get_response = client.get(f"/api/v1/trajectories/{trajectory_id}")
    assert get_response.status_code == 200

    retrieved_data = get_response.json()
    assert retrieved_data["id"] == trajectory_id
    assert len(retrieved_data["path"]) == expected_path_length

    # 3. List trajectories
    list_response = client.get("/api/v1/trajectories")
    assert list_response.status_code == 200

    list_data = list_response.json()
    assert list_data["total"] >= 1
    assert any(traj["id"] == trajectory_id for traj in list_data["trajectories"])

    # 4. Delete trajectory
    delete_response = client.delete(f"/api/v1/trajectories/{trajectory_id}")
    assert delete_response.status_code == 200

    # 5. Verify deletion
    final_get_response = client.get(f"/api/v1/trajectories/{trajectory_id}")
    assert final_get_response.status_code == 404


# Edge case tests
def test_minimum_wall_size(client: TestClient):
    """Test with minimum wall size."""
    payload = {"wall_width": 0.1, "wall_height": 0.1, "obstacles": []}

    response = client.post("/api/v1/trajectories", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["metadata"]["total_cells"] == 1  # Single cell
    assert len(data["path"]) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
