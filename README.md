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
│   ├── __init__.py
│   ├── main.py                 # FastAPI app and API routes
│   ├── models/
│   │   ├── __init__.py
│   │   └── trajectory.py       # SQLModel for database schema
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── trajectory.py       # Pydantic models for validation
│   ├── services/
│   │   ├── __init__.py
│   │   └── path_planning.py    # Trajectory generation logic
│   └── static/
│       └── index.html          # Frontend visualization
├── tests/
│   ├── __init__.py
│   └── test_api.py             # Comprehensive API tests
├── .github/workflows/
│   └── ci.yml                  # CI pipeline
├── .gitignore                  # Git ignore patterns
├── pyproject.toml              # Project dependencies and config
└── README.md                   # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+ 
- [uv](https://docs.astral.sh/uv/) package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/example/wall-finishing-robot.git
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
uv run pytest tests/ -v
```

### Run with Coverage
```bash
uv run pytest tests/ --cov=src --cov-report=html
```

### Test Categories
- **Unit Tests**: Individual component testing
- **Integration Tests**: API endpoint testing
- **Performance Tests**: Response time validation (< 1s)
- **Edge Cases**: Boundary condition testing

### Example Test Results
```
tests/test_api.py::TestTrajectoryCreation::test_create_valid_trajectory PASSED
tests/test_api.py::TestTrajectoryCreation::test_expected_trajectory_count PASSED
tests/test_api.py::TestPerformanceRequirements::test_large_wall_performance PASSED
========================= 47 passed in 2.34s =========================
```

## 🔧 Code Quality

### Linting
```bash
uv run ruff check src/ tests/
uv run ruff format src/ tests/
```

### Type Checking
```bash
uv run mypy src/
```

### Configuration
- **Ruff**: Code formatting and linting
- **MyPy**: Static type checking
- **Pytest**: Testing framework
- **Coverage**: Test coverage reporting

## 🚀 Deployment

### Local Development
```bash
uv run python -m src.main
```

### Production with Gunicorn
```bash
uv add gunicorn
uv run gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Docker (Optional)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install uv && uv sync
EXPOSE 8000
CMD ["uv", "run", "python", "-m", "src.main"]
```

## 📊 Performance Benchmarks

### Expected Performance
- **5m×5m wall with 3 obstacles**: ~2473 trajectory points
- **Response time**: < 1 second for all operations
- **Memory usage**: < 100MB for typical operations
- **Database**: Optimized with indexed primary keys

### Validated Test Cases
- ✅ 5×5m wall, 3×25cm obstacles → 2473 points
- ✅ 10×10m wall response time < 1s  
- ✅ 20 small obstacles processing < 1s
- ✅ CRUD operations < 1s each

## 🐛 Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

#### Database Issues
```bash
# Delete database and restart
rm trajectories.db
uv run python -m src.main
```

#### Import Errors
```bash
# Reinstall dependencies
uv sync --group dev
```

### Debug Mode
Set environment variable for detailed logging:
```bash
PYTHONPATH=. LOG_LEVEL=DEBUG uv run python -m src.main
```

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Install development dependencies: `uv sync --group dev`
4. Make changes with tests
5. Run quality checks:
   ```bash
   uv run ruff check src/ tests/
   uv run mypy src/
   uv run pytest tests/
   ```
6. Submit a pull request

### Code Standards
- **Type Hints**: Required for all functions
- **Docstrings**: Google-style docstrings
- **Testing**: Minimum 90% coverage
- **Formatting**: Ruff with 100-character line limit

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **FastAPI**: Modern, fast web framework
- **SQLModel**: SQL databases with Python type safety  
- **NumPy**: Efficient numerical computations
- **Loguru**: Simplified logging
- **Ruff**: Lightning-fast Python linter

## 📞 Support

- **Documentation**: This README and `/docs` endpoint
- **Issues**: GitHub Issues for bug reports
- **Discussions**: GitHub Discussions for questions

---

**Built with ❤️ for autonomous robotics applications**
