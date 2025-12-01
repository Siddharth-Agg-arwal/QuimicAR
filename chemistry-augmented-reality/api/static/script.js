// API Base URL
const API_URL = '';

// DOM Elements
const currentLevelEl = document.getElementById('currentLevel');
const objectiveEl = document.getElementById('objective');
const totalLevelsEl = document.getElementById('totalLevels');
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const uploadBtn = document.getElementById('uploadBtn');
const resultCard = document.getElementById('resultCard');
const resultImage = document.getElementById('resultImage');
const downloadBtn = document.getElementById('downloadBtn');
const levelSelect = document.getElementById('levelSelect');
const prevLevelBtn = document.getElementById('prevLevel');
const nextLevelBtn = document.getElementById('nextLevel');

// File storage
let selectedFile = null;
let processedImageBlob = null;

// Initialize app
async function init() {
    await checkAPIHealth();
    await loadLevelInfo();
    setupEventListeners();
}

// Check API Health
async function checkAPIHealth() {
    try {
        const response = await fetch(`${API_URL}/health`);
        const data = await response.json();

        if (data.status === 'ok') {
            updateAPIStatus('healthStatus', true);
            console.log('API Connected:', data);
        }
    } catch (error) {
        console.error('API Health Check Failed:', error);
        updateAPIStatus('healthStatus', false);
    }
}

// Load Level Information
async function loadLevelInfo() {
    try {
        const response = await fetch(`${API_URL}/levels`);
        const data = await response.json();

        currentLevelEl.textContent = data.current_level;
        objectiveEl.textContent = data.current_objective;
        totalLevelsEl.textContent = data.total_levels;
        levelSelect.value = data.current_level;

        updateAPIStatus('levelsStatus', true);
    } catch (error) {
        console.error('Failed to load level info:', error);
        updateAPIStatus('levelsStatus', false);
    }
}

// Update API Status Indicator
function updateAPIStatus(elementId, isActive) {
    const statusEl = document.getElementById(elementId);
    if (statusEl) {
        statusEl.classList.toggle('active', isActive);
    }
}

// Setup Event Listeners
function setupEventListeners() {
    // Upload area click
    uploadArea.addEventListener('click', () => fileInput.click());

    // File input change
    fileInput.addEventListener('change', handleFileSelect);

    // Drag and drop
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);

    // Upload button
    uploadBtn.addEventListener('click', processImage);

    // Download button
    downloadBtn.addEventListener('click', downloadResult);

    // Level controls
    levelSelect.addEventListener('change', handleLevelChange);
    prevLevelBtn.addEventListener('click', () => changeLevel(-1));
    nextLevelBtn.addEventListener('click', () => changeLevel(1));
}

// Handle file selection
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file && file.type.startsWith('image/')) {
        selectedFile = file;
        showUploadButton(file.name);
    }
}

// Handle drag over
function handleDragOver(event) {
    event.preventDefault();
    uploadArea.classList.add('dragover');
}

// Handle drag leave
function handleDragLeave(event) {
    event.preventDefault();
    uploadArea.classList.remove('dragover');
}

// Handle drop
function handleDrop(event) {
    event.preventDefault();
    uploadArea.classList.remove('dragover');

    const file = event.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
        selectedFile = file;
        fileInput.files = event.dataTransfer.files;
        showUploadButton(file.name);
    }
}

// Show upload button
function showUploadButton(filename) {
    uploadArea.innerHTML = `
        <div class="upload-icon">✓</div>
        <p class="upload-text">${filename}</p>
        <p class="upload-hint">Click upload button to process</p>
    `;
    uploadBtn.style.display = 'block';
}

// Process image
async function processImage() {
    if (!selectedFile) return;

    uploadBtn.disabled = true;
    uploadBtn.innerHTML = '<span>Processing...</span>';

    try {
        const formData = new FormData();
        formData.append('file', selectedFile);

        const response = await fetch(`${API_URL}/process_frame`, {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            processedImageBlob = await response.blob();
            const imageUrl = URL.createObjectURL(processedImageBlob);

            resultImage.src = imageUrl;
            resultCard.style.display = 'block';

            // Scroll to result
            resultCard.scrollIntoView({ behavior: 'smooth' });

            updateAPIStatus('processStatus', true);
        } else {
            alert('Failed to process image');
            updateAPIStatus('processStatus', false);
        }
    } catch (error) {
        console.error('Error processing image:', error);
        alert('Error processing image');
        updateAPIStatus('processStatus', false);
    } finally {
        uploadBtn.disabled = false;
        uploadBtn.innerHTML = '<span>Process Image</span>';
    }
}

// Download result
function downloadResult() {
    if (!processedImageBlob) return;

    const url = URL.createObjectURL(processedImageBlob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'chemistry-ar-result.jpg';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Handle level change
async function handleLevelChange(event) {
    const newLevel = parseInt(event.target.value);
    await setLevel(newLevel);
}

// Change level by offset
async function changeLevel(offset) {
    const currentLevel = parseInt(levelSelect.value);
    const totalLevels = parseInt(totalLevelsEl.textContent);
    let newLevel = currentLevel + offset;

    // Wrap around
    if (newLevel < 0) newLevel = totalLevels - 1;
    if (newLevel >= totalLevels) newLevel = 0;

    levelSelect.value = newLevel;
    await setLevel(newLevel);
}

// Set level
async function setLevel(level) {
    try {
        const response = await fetch(`${API_URL}/set_level/${level}`, {
            method: 'POST'
        });

        if (response.ok) {
            const data = await response.json();
            currentLevelEl.textContent = data.current_level;
            objectiveEl.textContent = data.objective;
            updateAPIStatus('setLevelStatus', true);
        }
    } catch (error) {
        console.error('Failed to set level:', error);
        updateAPIStatus('setLevelStatus', false);
    }
}

// Start the app
init();
