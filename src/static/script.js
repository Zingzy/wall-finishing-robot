// Global variables
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
let currentTrajectory = null;
let currentStep = 0;
let animationId = null;
let isPlaying = false;
let scale = 100; // Canvas pixels per meter, will be set dynamically
const CANVAS_MAX_SIZE = 500; // px, max canvas width/height
const showScaleCheckbox = document.getElementById('showScale');

// UI Elements
const statusEl = document.getElementById('status');
const playBtn = document.getElementById('playBtn');
const stopBtn = document.getElementById('stopBtn');
const resetBtn = document.getElementById('resetBtn');
const createBtn = document.getElementById('createTrajectory');
const loadBtn = document.getElementById('loadTrajectories');
const addObstacleBtn = document.getElementById('addObstacle');
const messageEl = document.getElementById('message');
const trajectoryInfoEl = document.getElementById('trajectoryInfo');
const trajectoryListEl = document.getElementById('trajectoryList');

// Initialize
updateStatus('Ready');
loadTrajectoryList();

// Event listeners
playBtn.addEventListener('click', playAnimation);
stopBtn.addEventListener('click', stopAnimation);
resetBtn.addEventListener('click', resetAnimation);
createBtn.addEventListener('click', createTrajectory);
loadBtn.addEventListener('click', loadTrajectoryList);
addObstacleBtn.addEventListener('click', addObstacle);
showScaleCheckbox.addEventListener('change', drawScene);

// Obstacle management
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('remove-obstacle')) {
        e.target.parentElement.remove();
    }
});

function addObstacle() {
    const obstacleList = document.getElementById('obstacleList');
    const obstacleRow = document.createElement('div');
    obstacleRow.className = 'obstacle-row';
    obstacleRow.innerHTML = `
        <input type="number" placeholder="X (m)" value="1.0" step="0.1" min="0">
        <input type="number" placeholder="Y (m)" value="1.0" step="0.1" min="0">
        <input type="number" placeholder="Width (m)" value="0.25" step="0.1" min="0.1">
        <input type="number" placeholder="Height (m)" value="0.25" step="0.1" min="0.1">
        <button type="button" class="remove-obstacle">Remove</button>
    `;
    obstacleList.appendChild(obstacleRow);
}

function getObstacles() {
    const obstacles = [];
    const obstacleRows = document.querySelectorAll('.obstacle-row');
    
    obstacleRows.forEach(row => {
        const inputs = row.querySelectorAll('input');
        if (inputs.length === 4) {
            obstacles.push({
                x: parseFloat(inputs[0].value) || 0,
                y: parseFloat(inputs[1].value) || 0,
                width: parseFloat(inputs[2].value) || 0.1,
                height: parseFloat(inputs[3].value) || 0.1
            });
        }
    });
    
    return obstacles;
}

async function createTrajectory() {
    try {
        updateStatus('Generating trajectory...');
        showMessage('Creating trajectory...', 'success');
        
        const wallWidth = parseFloat(document.getElementById('wallWidth').value);
        const wallHeight = parseFloat(document.getElementById('wallHeight').value);
        const obstacles = getObstacles();

        const payload = {
            wall_width: wallWidth,
            wall_height: wallHeight,
            obstacles: obstacles
        };

        const response = await fetch('/api/v1/trajectories', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail[0].msg || 'Failed to create trajectory');
        }

        const data = await response.json();
        currentTrajectory = data;
        currentStep = 0;
        
        showMessage(`Trajectory created successfully! ID: ${data.id}, Points: ${data.path.length}`, 'success');
        updateStatus('Trajectory loaded');
        drawScene();
        showTrajectoryInfo(data);
        loadTrajectoryList(); // Refresh the list

    } catch (error) {
        console.error('Error creating trajectory:', error);
        showMessage(`Error: ${error.message}`, 'error');
        updateStatus('Error');
    }
}

async function loadTrajectory(id) {
    try {
        updateStatus('Loading trajectory...');
        
        const response = await fetch(`/api/v1/trajectories/${id}`);
        if (!response.ok) {
            throw new Error('Trajectory not found');
        }

        const data = await response.json();
        currentTrajectory = data;
        currentStep = 0;
        
        updateStatus('Trajectory loaded');
        drawScene();
        showTrajectoryInfo(data);

        // Update form fields
        document.getElementById('wallWidth').value = data.wall_width;
        document.getElementById('wallHeight').value = data.wall_height;
        
        // Clear and populate obstacles
        const obstacleList = document.getElementById('obstacleList');
        obstacleList.innerHTML = '';
        data.obstacles.forEach(obs => {
            const obstacleRow = document.createElement('div');
            obstacleRow.className = 'obstacle-row';
            obstacleRow.innerHTML = `
                <input type="number" placeholder="X (m)" value="${obs.x}" step="0.1" min="0">
                <input type="number" placeholder="Y (m)" value="${obs.y}" step="0.1" min="0">
                <input type="number" placeholder="Width (m)" value="${obs.width}" step="0.1" min="0.1">
                <input type="number" placeholder="Height (m)" value="${obs.height}" step="0.1" min="0.1">
                <button type="button" class="remove-obstacle">Remove</button>
            `;
            obstacleList.appendChild(obstacleRow);
        });

    } catch (error) {
        console.error('Error loading trajectory:', error);
        showMessage(`Error loading trajectory: ${error.message}`, 'error');
        updateStatus('Error');
    }
}

async function loadTrajectoryList() {
    try {
        const response = await fetch('/api/v1/trajectories');
        if (!response.ok) {
            throw new Error('Failed to load trajectories');
        }

        const data = await response.json();
        
        trajectoryListEl.innerHTML = '';
        
        if (data.trajectories.length === 0) {
            trajectoryListEl.innerHTML = '<div style="padding: 20px; text-align: center; color: #666;">No trajectories found</div>';
            return;
        }

        data.trajectories.forEach(traj => {
            const item = document.createElement('div');
            item.className = 'trajectory-item';
            item.innerHTML = `
                <strong>ID: ${traj.id}</strong><br>
                Wall: ${traj.wall_width}m  ${traj.wall_height}m<br>
                Obstacles: ${traj.obstacle_count}, Points: ${traj.path_points}
            `;
            item.addEventListener('click', () => {
                // Remove previous selection
                document.querySelectorAll('.trajectory-item').forEach(el => el.classList.remove('selected'));
                item.classList.add('selected');
                loadTrajectory(traj.id);
            });
            trajectoryListEl.appendChild(item);
        });

    } catch (error) {
        console.error('Error loading trajectory list:', error);
        trajectoryListEl.innerHTML = '<div style="padding: 20px; text-align: center; color: #f44336;">Error loading trajectories</div>';
    }
}

function drawScene() {
    if (!currentTrajectory) return;

    const { wall_width, wall_height, obstacles, path } = currentTrajectory;
    let margin = showScaleCheckbox.checked ? 40 : 0;
    // Get container size if scale is hidden
    let containerWidth = 500;
    let containerHeight = 500;
    if (!showScaleCheckbox.checked) {
        const container = canvas.parentElement;
        containerWidth = container.offsetWidth;
        containerHeight = container.offsetHeight;
    }
    // Dynamically set scale and canvas size
    if (showScaleCheckbox.checked) {
        scale = Math.min((CANVAS_MAX_SIZE) / wall_width, (CANVAS_MAX_SIZE) / wall_height);
        canvas.width = Math.ceil(wall_width * scale) + margin;
        canvas.height = Math.ceil(wall_height * scale) + margin;
    } else {
        scale = Math.min((containerWidth) / wall_width, (containerHeight) / wall_height);
        canvas.width = Math.ceil(wall_width * scale);
        canvas.height = Math.ceil(wall_height * scale);
    }
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw X and Y axes with scale
    ctx.save();
    ctx.strokeStyle = '#888';
    ctx.lineWidth = 1;
    ctx.beginPath();
    // X axis
    ctx.moveTo(margin ? 30 : 0, canvas.height - (margin ? 30 : 0));
    ctx.lineTo(canvas.width - (margin ? 5 : 0), canvas.height - (margin ? 30 : 0));
    // Y axis
    ctx.moveTo(margin ? 30 : 0, canvas.height - (margin ? 30 : 0));
    ctx.lineTo(margin ? 30 : 0, margin ? 5 : 0);
    ctx.stroke();
    if (showScaleCheckbox.checked) {
        ctx.font = '12px Arial';
        ctx.fillStyle = '#444';
        ctx.textAlign = 'center';
        // X axis scale
        for (let x = 0; x <= wall_width; x += 1) {
            const px = 30 + x * scale;
            ctx.beginPath();
            ctx.moveTo(px, canvas.height - 30);
            ctx.lineTo(px, canvas.height - 25);
            ctx.stroke();
            ctx.fillText(x.toFixed(0), px, canvas.height - 10);
        }
        // Y axis scale
        ctx.textAlign = 'right';
        for (let y = 0; y <= wall_height; y += 1) {
            const py = canvas.height - 30 - y * scale;
            ctx.beginPath();
            ctx.moveTo(30, py);
            ctx.lineTo(25, py);
            ctx.stroke();
            ctx.fillText(y.toFixed(0), 20, py + 4);
        }
    }
    ctx.restore();

    // Draw wall boundary
    ctx.strokeStyle = '#333';
    ctx.lineWidth = 2;
    ctx.strokeRect(margin ? 30 : 0, canvas.height - (margin ? 30 : 0) - wall_height * scale, wall_width * scale, wall_height * scale);

    // Draw obstacles (red rectangles)
    ctx.fillStyle = '#f44336';
    obstacles.forEach(obs => {
        ctx.fillRect(
            (margin ? 30 : 0) + obs.x * scale,
            canvas.height - (margin ? 30 : 0) - (obs.y + obs.height) * scale,
            obs.width * scale,
            obs.height * scale
        );
    });

    // Draw trajectory path (blue dots)
    ctx.fillStyle = '#2196F3';
    for (let i = 0; i < Math.min(currentStep, path.length); i++) {
        const [row, col] = path[i];
        ctx.beginPath();
        ctx.arc(
            (margin ? 30 : 0) + col * scale * 0.1 + scale * 0.1 / 2,
            canvas.height - (margin ? 30 : 0) - (row * scale * 0.1 + scale * 0.1 / 2),
            2,
            0,
            2 * Math.PI
        );
        ctx.fill();
    }
    // Draw current position (larger red dot)
    if (currentStep > 0 && currentStep <= path.length) {
        const [row, col] = path[currentStep - 1];
        ctx.fillStyle = '#ff5722';
        ctx.beginPath();
        ctx.arc(
            (margin ? 30 : 0) + col * scale * 0.1 + scale * 0.1 / 2,
            canvas.height - (margin ? 30 : 0) - (row * scale * 0.1 + scale * 0.1 / 2),
            4,
            0,
            2 * Math.PI
        );
        ctx.fill();
    }
}

function playAnimation() {
    if (!currentTrajectory || isPlaying) return;
    
    isPlaying = true;
    updateStatus('Playing');
    
    function animate() {
        if (!isPlaying || currentStep >= currentTrajectory.path.length) {
            if (currentStep >= currentTrajectory.path.length) {
                updateStatus('Completed');
                isPlaying = false;
            }
            return;
        }
        
        currentStep++;
        drawScene();
        
        animationId = setTimeout(animate, 20); // 20ms per step as specified
    }
    
    animate();
}

function stopAnimation() {
    isPlaying = false;
    if (animationId) {
        clearTimeout(animationId);
        animationId = null;
    }
    updateStatus('Stopped');
}

function resetAnimation() {
    stopAnimation();
    currentStep = 0;
    drawScene();
    updateStatus('Ready');
}

function updateStatus(status) {
    statusEl.textContent = status;
    statusEl.className = 'status';
    
    if (status === 'Playing') {
        statusEl.classList.add('playing');
    } else if (status === 'Stopped') {
        statusEl.classList.add('stopped');
    } else if (status === 'Completed') {
        statusEl.classList.add('completed');
    }
}

function showMessage(message, type) {
    messageEl.innerHTML = `<div class="${type}">${message}</div>`;
    setTimeout(() => {
        messageEl.innerHTML = '';
    }, 5000);
}

function showTrajectoryInfo(data) {
    if (data.metadata) {
        trajectoryInfoEl.innerHTML = `
            <h4>Trajectory Information</h4>
            <p><strong>ID:</strong> ${data.id}</p>
            <p><strong>Wall Dimensions:</strong> ${data.wall_width}m  ${data.wall_height}m</p>
            <p><strong>Total Cells:</strong> ${data.metadata.total_cells}</p>
            <p><strong>Obstacle Cells:</strong> ${data.metadata.obstacle_cells}</p>
            <p><strong>Free Cells:</strong> ${data.metadata.free_cells}</p>
            <p><strong>Path Points:</strong> ${data.metadata.path_points}</p>
            <p><strong>Coverage:</strong> ${data.metadata.coverage_percentage.toFixed(1)}%</p>
            <p><strong>Grid Size:</strong> ${data.metadata.grid_dimensions.rows}  ${data.metadata.grid_dimensions.cols}</p>
        `;
        trajectoryInfoEl.style.display = 'block';
    }
}

// Initial canvas setup
ctx.fillStyle = '#f5f5f5';
ctx.fillRect(0, 0, canvas.width, canvas.height);
ctx.strokeStyle = '#ddd';
ctx.strokeRect(0, 0, canvas.width, canvas.height);

// Add some instructions
ctx.fillStyle = '#666';
ctx.font = '16px Arial';
ctx.textAlign = 'center';
ctx.fillText('Create or load a trajectory to begin visualization', canvas.width / 2, canvas.height / 2); 