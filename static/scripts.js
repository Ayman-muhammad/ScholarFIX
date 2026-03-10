/**
 * ScholarFix Main JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    const popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // File upload handling
    const fileUpload = document.getElementById('fileUpload');
    if (fileUpload) {
        fileUpload.addEventListener('change', handleFileSelect);
    }
    
    // Document processing form
    const processForm = document.getElementById('processForm');
    if (processForm) {
        processForm.addEventListener('submit', handleDocumentProcessing);
    }
    
    // Mode selection
    const modeSelectors = document.querySelectorAll('.mode-selector');
    modeSelectors.forEach(selector => {
        selector.addEventListener('change', updateProcessingOptions);
    });
    
    // Initialize dashboard
    initDashboard();
});

/**
 * Handle file selection
 */
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const fileInfo = document.getElementById('fileInfo');
    const processBtn = document.getElementById('processBtn');
    
    if (fileInfo) {
        const fileSize = formatFileSize(file.size);
        fileInfo.innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-file-alt me-2"></i>
                <strong>${file.name}</strong> (${fileSize})
                <br>
                <small class="text-muted">Ready to process</small>
            </div>
        `;
    }
    
    if (processBtn) {
        processBtn.disabled = false;
    }
}

/**
 * Handle document processing
 */
async function handleDocumentProcessing(event) {
    event.preventDefault();
    
    const form = event.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    
    // Disable button and show processing
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
    
    // Show processing indicator
    const processingIndicator = document.getElementById('processingIndicator');
    if (processingIndicator) {
        processingIndicator.classList.remove('d-none');
    }
    
    try {
        const formData = new FormData(form);
        
        const response = await fetch('/process', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Show success message
            showAlert('Document processed successfully!', 'success');
            
            // Update UI with results
            updateResultsUI(result);
            
            // Reset form after delay
            setTimeout(() => {
                form.reset();
                if (processingIndicator) {
                    processingIndicator.classList.add('d-none');
                }
            }, 3000);
            
        } else {
            throw new Error(result.error || 'Processing failed');
        }
        
    } catch (error) {
        showAlert(`Error: ${error.message}`, 'danger');
        console.error('Processing error:', error);
        
    } finally {
        // Reset button
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
        
        // Hide processing indicator
        if (processingIndicator) {
            processingIndicator.classList.add('d-none');
        }
    }
}

/**
 * Update processing options based on selected mode
 */
function updateProcessingOptions(event) {
    const mode = event.target.value;
    const citationOptions = document.getElementById('citationOptions');
    const cvOptions = document.getElementById('cvOptions');
    
    // Show/hide citation options for academic mode
    if (citationOptions) {
        if (mode === 'academic') {
            citationOptions.classList.remove('d-none');
        } else {
            citationOptions.classList.add('d-none');
        }
    }
    
    // Show/hide CV options for cv mode
    if (cvOptions) {
        if (mode === 'cv') {
            cvOptions.classList.remove('d-none');
        } else {
            cvOptions.classList.add('d-none');
        }
    }
}

/**
 * Update UI with processing results
 */
function updateResultsUI(result) {
    // Update preview
    const previewContainer = document.getElementById('previewContainer');
    if (previewContainer && result.preview) {
        previewContainer.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <div class="preview-panel">
                        <h6 class="preview-title">
                            <i class="fas fa-file-alt me-2"></i>Original
                        </h6>
                        <div class="preview-content">
                            ${escapeHtml(result.preview.original || 'No preview available')}
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="preview-panel">
                        <h6 class="preview-title">
                            <i class="fas fa-check-circle me-2 text-success"></i>Refined
                        </h6>
                        <div class="preview-content">
                            ${escapeHtml(result.preview.processed || 'No preview available')}
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="text-center mt-3">
                <a href="${result.download_url}" class="btn btn-success">
                    <i class="fas fa-download me-2"></i>Download Refined Document
                </a>
                <button class="btn btn-outline-primary ms-2" onclick="showDetailedResults(${JSON.stringify(result).replace(/"/g, '&quot;')})">
                    <i class="fas fa-chart-bar me-2"></i>View Detailed Results
                </button>
            </div>
        `;
        previewContainer.classList.remove('d-none');
    }
    
    // Update metrics
    const metricsContainer = document.getElementById('metricsContainer');
    if (metricsContainer && result.metrics) {
        const metrics = result.metrics;
        metricsContainer.innerHTML = `
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">${metrics.grammar_fixes || 0}</div>
                    <div class="stat-label">Grammar Fixes</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${metrics.clarity_improvements || 0}</div>
                    <div class="stat-label">Clarity Improvements</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${metrics.tone_adjustments || 0}</div>
                    <div class="stat-label">Tone Adjustments</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${metrics.formatting_changes || 0}</div>
                    <div class="stat-label">Formatting Changes</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${metrics.improvement_percentage || 0}%</div>
                    <div class="stat-label">Overall Improvement</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${formatDuration(metrics.processing_time || 0)}</div>
                    <div class="stat-label">Processing Time</div>
                </div>
            </div>
        `;
        metricsContainer.classList.remove('d-none');
    }
}

/**
 * Show detailed results in modal
 */
function showDetailedResults(result) {
    const modal = new bootstrap.Modal(document.getElementById('resultsModal'));
    const modalBody = document.getElementById('resultsModalBody');
    
    if (modalBody) {
        modalBody.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <h6>Processing Summary</h6>
                    <ul class="list-group">
                        <li class="list-group-item d-flex justify-content-between">
                            <span>Mode:</span>
                            <span class="text-capitalize">${result.mode}</span>
                        </li>
                        <li class="list-group-item d-flex justify-content-between">
                            <span>Total Changes:</span>
                            <span class="badge bg-primary">${result.metrics.total_changes || 0}</span>
                        </li>
                        <li class="list-group-item d-flex justify-content-between">
                            <span>Processing Time:</span>
                            <span>${formatDuration(result.metrics.processing_time || 0)}</span>
                        </li>
                        <li class="list-group-item d-flex justify-content-between">
                            <span>Improvement:</span>
                            <span class="text-success">${result.metrics.improvement_percentage || 0}%</span>
                        </li>
                    </ul>
                </div>
                
                <div class="col-md-6">
                    <h6>Readability Analysis</h6>
                    ${result.metrics.readability ? `
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">${result.metrics.readability.readability_level}</h5>
                            <p class="card-text">
                                Flesch Reading Ease: ${result.metrics.readability.flesch_reading_ease}<br>
                                Average Sentence Length: ${result.metrics.readability.average_sentence_length}<br>
                                Average Word Length: ${result.metrics.readability.average_word_length}
                            </p>
                        </div>
                    </div>
                    ` : '<p class="text-muted">No readability data available</p>'}
                </div>
            </div>
            
            ${result.metrics.recommendations ? `
            <div class="mt-4">
                <h6>Recommendations</h6>
                <div class="list-group">
                    ${result.metrics.recommendations.map(rec => `
                        <div class="list-group-item">
                            <i class="fas fa-lightbulb text-warning me-2"></i>
                            ${escapeHtml(rec)}
                        </div>
                    `).join('')}
                </div>
            </div>
            ` : ''}
        `;
    }
    
    modal.show();
}

/**
 * Initialize dashboard functionality
 */
function initDashboard() {
    // Load user documents
    loadUserDocuments();
    
    // Update dashboard stats
    updateDashboardStats();
    
    // Setup event listeners for document actions
    setupDocumentActions();
}

/**
 * Load user documents
 */
async function loadUserDocuments() {
    try {
        const response = await fetch('/documents');
        const result = await response.json();
        
        if (result.success && result.documents) {
            updateDocumentsTable(result.documents);
        }
    } catch (error) {
        console.error('Error loading documents:', error);
    }
}

/**
 * Update documents table
 */
function updateDocumentsTable(documents) {
    const tableBody = document.getElementById('documentsTableBody');
    if (!tableBody) return;
    
    if (documents.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center py-4">
                    <i class="fas fa-file-alt fa-3x text-muted mb-3"></i>
                    <h5>No documents yet</h5>
                    <p class="text-muted">Upload your first document to get started!</p>
                </td>
            </tr>
        `;
        return;
    }
    
    tableBody.innerHTML = documents.map(doc => `
        <tr>
            <td>
                <i class="fas fa-file-${getFileIcon(doc.original_filename)} text-primary me-2"></i>
                ${truncateText(doc.original_filename, 30)}
            </td>
            <td>
                <span class="badge bg-${getModeBadgeColor(doc.mode)}">
                    ${doc.mode}
                </span>
            </td>
            <td>
                <span class="badge bg-${getStatusBadgeColor(doc.status)}">
                    ${doc.status}
                </span>
            </td>
            <td>${formatDate(doc.created_at)}</td>
            <td>
                ${doc.metrics ? `
                <span class="badge bg-info">
                    ${JSON.parse(doc.metrics).total_changes || 0} changes
                </span>
                ` : ''}
            </td>
            <td>
                <div class="btn-group btn-group-sm">
                    ${doc.status === 'completed' ? `
                    <a href="/download/${doc.file_id}" class="btn btn-outline-success" title="Download">
                        <i class="fas fa-download"></i>
                    </a>
                    <button class="btn btn-outline-info preview-document" 
                            data-file-id="${doc.file_id}" title="Preview">
                        <i class="fas fa-eye"></i>
                    </button>
                    ` : ''}
                    <button class="btn btn-outline-danger delete-document" 
                            data-doc-id="${doc.id}" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
    
    // Attach event listeners to new buttons
    attachDocumentEventListeners();
}

/**
 * Attach event listeners to document action buttons
 */
function attachDocumentEventListeners() {
    // Preview buttons
    document.querySelectorAll('.preview-document').forEach(btn => {
        btn.addEventListener('click', function() {
            const fileId = this.dataset.fileId;
            previewDocument(fileId);
        });
    });
    
    // Delete buttons
    document.querySelectorAll('.delete-document').forEach(btn => {
        btn.addEventListener('click', function() {
            const docId = this.dataset.docId;
            deleteDocument(docId);
        });
    });
}

/**
 * Preview document
 */
async function previewDocument(fileId) {
    try {
        const response = await fetch(`/preview/${fileId}`);
        const result = await response.json();
        
        if (result.success) {
            const modal = new bootstrap.Modal(document.getElementById('previewModal'));
            const modalBody = document.getElementById('previewModalBody');
            
            if (modalBody && result.preview) {
                modalBody.innerHTML = `
                    <div class="row">
                        <div class="col-md-6">
                            <h6>Original Preview</h6>
                            <div class="border rounded p-3 bg-light" style="max-height: 300px; overflow-y: auto;">
                                <pre class="mb-0">${escapeHtml(result.preview.original || 'No preview available')}</pre>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <h6>Refined Preview</h6>
                            <div class="border rounded p-3 bg-light" style="max-height: 300px; overflow-y: auto;">
                                <pre class="mb-0">${escapeHtml(result.preview.processed || 'No preview available')}</pre>
                            </div>
                        </div>
                    </div>
                `;
            }
            
            modal.show();
        }
    } catch (error) {
        console.error('Error previewing document:', error);
        showAlert('Error loading document preview', 'danger');
    }
}

/**
 * Delete document
 */
async function deleteDocument(docId) {
    if (!confirm('Are you sure you want to delete this document?')) {
        return;
    }
    
    try {
        const response = await fetch(`/document/${docId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert('Document deleted successfully', 'success');
            loadUserDocuments(); // Reload documents list
        } else {
            throw new Error(result.error || 'Delete failed');
        }
    } catch (error) {
        console.error('Error deleting document:', error);
        showAlert(`Error: ${error.message}`, 'danger');
    }
}

/**
 * Update dashboard statistics
 */
async function updateDashboardStats() {
    try {
        const response = await fetch('/api/stats');
        const result = await response.json();
        
        if (result.success) {
            // Update stats cards
            const stats = result.stats;
            
            // Update today's documents
            const todayEl = document.getElementById('todayDocuments');
            if (todayEl && stats.today_documents !== undefined) {
                todayEl.textContent = stats.today_documents;
            }
            
            // Update total documents
            const totalEl = document.getElementById('totalDocuments');
            if (totalEl && stats.total_documents !== undefined) {
                totalEl.textContent = stats.total_documents;
            }
            
            // Update grammar fixes
            const grammarEl = document.getElementById('grammarFixes');
            if (grammarEl && stats.grammar_fixes !== undefined) {
                grammarEl.textContent = stats.grammar_fixes;
            }
            
            // Update remaining documents
            const remainingEl = document.getElementById('remainingDocuments');
            if (remainingEl && stats.documents_left !== undefined) {
                remainingEl.textContent = stats.documents_left;
                const progressEl = document.getElementById('documentsProgress');
                if (progressEl) {
                    const progress = ((stats.today_documents || 0) / (stats.max_documents || 5)) * 100;
                    progressEl.style.width = `${Math.min(progress, 100)}%`;
                }
            }
        }
    } catch (error) {
        console.error('Error loading dashboard stats:', error);
    }
}

/**
 * Setup document action handlers
 */
function setupDocumentActions() {
    // File upload drag and drop
    const dropArea = document.getElementById('dropArea');
    if (dropArea) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, preventDefaults, false);
        });
        
        ['dragenter', 'dragover'].forEach(eventName => {
            dropArea.addEventListener(eventName, highlight, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, unhighlight, false);
        });
        
        dropArea.addEventListener('drop', handleDrop, false);
    }
}

/**
 * Show alert message
 */
function showAlert(message, type = 'info') {
    // Remove existing alerts
    const existingAlerts = document.querySelectorAll('.alert-dismissible');
    existingAlerts.forEach(alert => {
        const bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
    });
    
    // Create alert
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 end-0 m-3`;
    alertDiv.style.zIndex = '9999';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            const bsAlert = new bootstrap.Alert(alertDiv);
            bsAlert.close();
        }
    }, 5000);
}

/**
 * Utility functions
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatDuration(seconds) {
    if (seconds < 60) {
        return `${seconds.toFixed(1)}s`;
    } else if (seconds < 3600) {
        return `${(seconds / 60).toFixed(1)}m`;
    } else {
        return `${(seconds / 3600).toFixed(1)}h`;
    }
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
}

function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength - 3) + '...';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function getFileIcon(filename) {
    if (filename.endsWith('.pdf')) return 'pdf';
    if (filename.endsWith('.docx')) return 'word';
    if (filename.endsWith('.txt')) return 'alt';
    return 'file';
}

function getModeBadgeColor(mode) {
    switch (mode) {
        case 'academic': return 'primary';
        case 'cv': return 'success';
        case 'professional': return 'info';
        case 'personal': return 'warning';
        default: return 'secondary';
    }
}

function getStatusBadgeColor(status) {
    switch (status) {
        case 'completed': return 'success';
        case 'processing': return 'warning';
        case 'failed': return 'danger';
        default: return 'secondary';
    }
}

/**
 * Drag and drop handlers
 */
function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function highlight() {
    const dropArea = document.getElementById('dropArea');
    if (dropArea) {
        dropArea.classList.add('highlight');
    }
}

function unhighlight() {
    const dropArea = document.getElementById('dropArea');
    if (dropArea) {
        dropArea.classList.remove('highlight');
    }
}

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    
    const fileInput = document.getElementById('fileUpload');
    if (fileInput && files.length > 0) {
        fileInput.files = files;
        handleFileSelect({ target: fileInput });
    }
}

/**
 * Export functions to global scope
 */
window.ScholarFix = {
    showAlert,
    formatFileSize,
    formatDuration,
    previewDocument,
    showDetailedResults
};