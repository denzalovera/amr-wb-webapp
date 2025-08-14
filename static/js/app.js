/**
 * AMR-WB Converter Web Application
 * Main JavaScript functionality for file handling, API communication, and UI management
 */

// DOM Elements
const elements = {
    fileInput: document.getElementById('file-input'),
    fileDropZone: document.getElementById('file-drop-zone'),
    fileInfo: document.getElementById('file-info'),
    convertBtn: document.getElementById('convert-btn'),
    analyzeBtn: document.getElementById('analyze-btn'),
    progressSection: document.getElementById('progress-section'),
    resultSection: document.getElementById('result-section'),
    uploadForm: document.getElementById('upload-form')
};

// File handling state
let currentFile = null;

/**
 * Initialize the application
 */
function init() {
    setupEventListeners();
    setupDragAndDrop();
}

/**
 * Set up all event listeners
 */
function setupEventListeners() {
    // File input change
    elements.fileInput.addEventListener('change', handleFileSelect);
    
    // Form submission
    elements.uploadForm.addEventListener('submit', handleFormSubmission);
    
    // Click on drop zone
    elements.fileDropZone.addEventListener('click', () => {
        elements.fileInput.click();
    });
}

/**
 * Set up drag and drop functionality
 */
function setupDragAndDrop() {
    const dropZone = elements.fileDropZone;
    
    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });
    
    // Highlight drop zone on drag
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlightDropZone, false);
    });
    
    // Remove highlight when drag leaves
    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlightDropZone, false);
    });
    
    // Handle file drop
    dropZone.addEventListener('drop', handleFileDrop, false);
}

/**
 * Prevent default drag behaviors
 */
function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

/**
 * Highlight the drop zone during drag
 */
function highlightDropZone() {
    elements.fileDropZone.classList.add('dragover');
}

/**
 * Remove highlight from drop zone
 */
function unhighlightDropZone() {
    elements.fileDropZone.classList.remove('dragover');
}

/**
 * Handle files dropped on the drop zone
 */
function handleFileDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    
    if (files.length > 0) {
        elements.fileInput.files = files;
        handleFileSelect();
    }
}

/**
 * Handle file selection (either from input or drop)
 */
function handleFileSelect() {
    const file = elements.fileInput.files[0];
    
    if (file) {
        currentFile = file;
        displayFileInfo(file);
        enableButtons();
        hideResult();
    }
}

/**
 * Display file information
 */
function displayFileInfo(file) {
    const fileName = file.name;
    const fileSize = (file.size / 1024 / 1024).toFixed(2);
    const fileType = file.name.split('.').pop().toLowerCase();
    
    // Validate file type
    if (!['pcap', 'pcapng'].includes(fileType)) {
        showError('Please select a valid PCAP or PCAPNG file.');
        return;
    }
    
    elements.fileInfo.innerHTML = `
        <strong>Selected file:</strong> ${fileName}<br>
        <strong>Size:</strong> ${fileSize} MB<br>
        <strong>Type:</strong> ${fileType.toUpperCase()}
    `;
    elements.fileInfo.style.display = 'block';
}

/**
 * Enable action buttons
 */
function enableButtons() {
    elements.convertBtn.disabled = false;
    elements.analyzeBtn.disabled = false;
}

/**
 * Handle form submission for conversion
 */
async function handleFormSubmission(e) {
    e.preventDefault();
    
    if (!currentFile) {
        showError('Please select a file first.');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', currentFile);
    formData.append('codec', document.getElementById('codec').value);
    formData.append('framing', document.getElementById('framing').value);
    
    showProgress('Converting audio...');
    
    try {
        const response = await fetch('/api/convert', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            showSuccess(result);
        } else {
            showError(result.error || 'Conversion failed');
        }
    } catch (error) {
        showError('Network error: ' + error.message);
    }
}

/**
 * Handle file analysis
 */
async function analyzeFile() {
    if (!currentFile) {
        showError('Please select a file first.');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', currentFile);
    
    showProgress('Analyzing PCAP structure...');
    
    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            showAnalysis(result);
        } else {
            showError(result.error || 'Analysis failed');
        }
    } catch (error) {
        showError('Network error: ' + error.message);
    }
}

/**
 * Show progress indicator
 */
function showProgress(message = 'Processing your file...') {
    elements.progressSection.style.display = 'block';
    elements.resultSection.style.display = 'none';
    elements.progressSection.querySelector('p').textContent = message;
    elements.convertBtn.disabled = true;
    elements.analyzeBtn.disabled = true;
}

/**
 * Hide progress indicator
 */
function hideProgress() {
    elements.progressSection.style.display = 'none';
    elements.convertBtn.disabled = false;
    elements.analyzeBtn.disabled = false;
}

/**
 * Show success result
 */
function showSuccess(result) {
    hideProgress();
    elements.resultSection.className = 'result-section';
    elements.resultSection.style.display = 'block';
    
    document.getElementById('result-title').textContent = '✅ Conversion Successful!';
    
    let content = `
        <p>${result.message}</p>
        <a href="/api/download/${result.output_file}" class="download-button">
            📥 Download ${result.output_file}
        </a>
    `;
    
    if (result.stats) {
        content += '<div class="stats">';
        Object.entries(result.stats).forEach(([key, value]) => {
            content += `<div><strong>${key}:</strong> ${value}</div>`;
        });
        content += '</div>';
    }
    
    document.getElementById('result-content').innerHTML = content;
}

/**
 * Show error result
 */
function showError(message) {
    hideProgress();
    elements.resultSection.className = 'result-section error';
    elements.resultSection.style.display = 'block';
    
    document.getElementById('result-title').textContent = '❌ Conversion Failed';
    document.getElementById('result-content').innerHTML = `<p>${message}</p>`;
}

/**
 * Show analysis result
 */
function showAnalysis(result) {
    hideProgress();
    elements.resultSection.className = 'result-section';
    elements.resultSection.style.display = 'block';
    
    document.getElementById('result-title').textContent = '📊 PCAP Analysis Results';
    
    let content = '<div class="stats"><pre>' + result.analysis + '</pre></div>';
    
    if (result.error) {
        content += '<div style="color: #721c24; margin-top: 10px;"><strong>Warnings:</strong><br>' + result.error + '</div>';
    }
    
    content += '<p style="margin-top: 15px;"><strong>💡 Next Steps:</strong></p>';
    content += '<ul style="margin-left: 20px;">';
    content += '<li>If you see AMR/AMR-WB/EVS codecs above, try converting with the detected codec</li>';
    content += '<li>If you see G.711, this tool cannot convert it (use other audio tools)</li>';
    content += '<li>If no supported codecs are detected, the file may not contain voice RTP streams</li>';
    content += '</ul>';
    
    document.getElementById('result-content').innerHTML = content;
}

/**
 * Hide result section
 */
function hideResult() {
    elements.resultSection.style.display = 'none';
}

// Make analyzeFile function globally available for onclick
window.analyzeFile = analyzeFile;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', init);
