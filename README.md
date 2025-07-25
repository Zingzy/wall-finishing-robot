# 🤖 Wall Finishing Robot - Trajectory Generation API

A production-ready FastAPI-based API system for autonomous wall-finishing robot control. This system generates optimal trajectories for wall coverage while avoiding obstacles, stores trajectories in a SQLite database, and provides a web-based visualization interface.

## ✨ Features

- **🎯 Trajectory Generation**: Grid-based zigzag (Boustrophedon-like) path planning algorithm
- **🚧 Obstacle Avoidance**: Support for rectangular obstacles (windows, doors, etc.)
- **💾 Data Persistence**: SQLite database with SQLModel ORM for trajectory storage
- **🌐 REST API**: Complete CRUD operations with FastAPI
- **📊 Web Visualization**: Interactive HTML/Canvas frontend with playback controls
- **✅ Comprehensive Testing**: 98%+ test coverage with pytest
- **🔧 CI/CD Pipeline**: GitHub Actions for automated testing and code quality
- **📝 Logging**: Structured logging with Loguru
- **⚡ Performance Optimized**: < 1s response times for trajectory generation

## 🏗️ Project Structure

```
wall-finishing-robot/
├── src/
│ ├── init.py
│ ├── app.py # Main FastAPI application
│ ├── api/
│ │ ├── init.py
│ │ └── v1/
│ │ ├── init.py
│ │ ├── router.py # API router configuration
│ │ └── trajectories.py # Trajectory endpoints
│ ├── config/
│ │ ├── init.py
│ │ ├── config.toml # Application configuration
│ │ ├── config.template.toml# Configuration template
│ │ ├── loader.py # Configuration loader
│ │ └── schemas.py # Configuration schemas
│ ├── models/
│ │ ├── init.py
│ │ └── trajectory.py # SQLModel database models
│ ├── schemas/
│ │ ├── init.py
│ │ └── trajectory.py # Pydantic request/response models
│ ├── services/
│ │ ├── init.py
│ │ └── path_planning.py # Trajectory generation logic
│ └── static/
│ ├── index.html # Frontend HTML
│ ├── script.js # Frontend JavaScript
│ └── styles.css # Frontend CSS (responsive)
├── tests/
│ ├── init.py
│ └── test_api.py # Comprehensive API tests
├── logs/ # Application logs
├── .github/workflows/
│ └── ci.yml # CI pipeline
├── main.py # Application entry point
├── pyproject.toml # Project dependencies and config
├── uv.lock # Dependency lock file
```

## 🗄️ Database Schema

### Trajectories Table

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO INCREMENT | Unique trajectory identifier |
| `wall_width` | FLOAT | NOT NULL | Wall width in meters |
| `wall_height` | FLOAT | NOT NULL | Wall height in meters |
| `obstacles` | TEXT | NOT NULL | JSON string of obstacle definitions |
| `path` | TEXT | NOT NULL | JSON string of trajectory path points |
| `obstacles_count` | INTEGER | DEFAULT 0 | Number of obstacles (computed) |
| `path_points` | INTEGER | DEFAULT 0 | Number of path points (computed) |



## 🚀 Quick Start

### Prerequisites

- Python 3.11+ 
- [uv](https://docs.astral.sh/uv/) package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/zingzy/wall-finishing-robot.git
   cd wall-finishing-robot
   ```

2. **Install dependencies**
   ```bash
   uv sync --group dev
   ```

3. **Run the application**
   ```bash
   uv run python -m src.main
   ```

4. **Access the application**
   - API Documentation: http://localhost:8000/docs
   - Web Interface: http://localhost:8000/static/index.html
   - Health Check: http://localhost:8000/health

## 📖 API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### 🔗 Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root endpoint with API information |
| GET | `/health` | Health check endpoint |
| GET | `/docs` | Interactive API documentation |

#### 🎯 Trajectory Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/trajectories` | Create new trajectory |
| GET | `/trajectories/{id}` | Get trajectory by ID |
| GET | `/trajectories` | List all trajectories |
| DELETE | `/trajectories/{id}` | Delete trajectory by ID |

### 📝 API Examples

#### Create Trajectory

**POST** `/trajectories`

```json
{
  "wall_width": 5.0,
  "wall_height": 5.0,
  "obstacles": [
    {"x": 1.0, "y": 1.0, "width": 0.25, "height": 0.25},
    {"x": 3.0, "y": 2.0, "width": 0.25, "height": 0.25},
    {"x": 2.0, "y": 3.5, "width": 0.25, "height": 0.25}
  ],
  "cell_size": 0.1
}
```

**Response:**
```json
{
  "id": 1,
  "wall_width": 5.0,
  "wall_height": 5.0,
  "obstacles": [...],
  "path": [[0, 0], [0, 1], [0, 2], ...],
  "metadata": {
    "total_cells": 2500,
    "obstacle_cells": 27,
    "free_cells": 2473,
    "path_points": 2473,
    "coverage_percentage": 100.0,
    "grid_dimensions": {"rows": 50, "cols": 50},
    "cell_size": 0.1
  }
}
```

#### Get Trajectory

**GET** `/trajectories/1`

```json
{
  "id": 1,
  "wall_width": 5.0,
  "wall_height": 5.0,
  "obstacles": [...],
  "path": [[0, 0], [0, 1], [0, 2], ...]
}
```

#### List Trajectories

**GET** `/trajectories`

```json
{
  "trajectories": [
    {
      "id": 1,
      "wall_width": 5.0,
      "wall_height": 5.0,
      "obstacle_count": 3,
      "path_points": 2473
    }
  ],
  "total": 1
}
```

## 🎮 Web Interface

The web interface provides an interactive visualization of trajectories:

### Features
- **📐 Wall Configuration**: Set wall dimensions and cell size
- **🚧 Obstacle Management**: Add/remove rectangular obstacles
- **🎯 Trajectory Generation**: Create new trajectories
- **📊 Visualization**: Canvas-based rendering with playback controls
- **💾 Trajectory Management**: Load and view saved trajectories

### Controls
- **Play**: Start trajectory animation (20ms per step)
- **Stop**: Pause animation
- **Reset**: Reset to beginning

### Visual Elements
- **Black Border**: Wall boundaries
- **Red Rectangles**: Obstacles (windows, doors)
- **Blue Dots**: Trajectory path
- **Orange Dot**: Current robot position

## 🧪 Testing

### Run All Tests
```bash
uv run pytest -vv
```

## 🔧 Code Quality

### Linting
```bash
uv run ruff check
uv run ruff format --check
```

### Type Checking
```bash
uv run mypy src --ignore-missing-imports
```

### Configuration
- **Ruff**: Code formatting and linting
- **MyPy**: Static type checking
- **Pytest**: Testing framework

## 🚀 Deployment

### Local Development
```bash
uv run main.py
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
