// DOM Elements
const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('fileInput');
const previewContainer = document.getElementById('previewContainer');
const imagePreview = document.getElementById('imagePreview');
const clearBtn = document.getElementById('clearBtn');
const analyzeBtn = document.getElementById('analyzeBtn');
const resultsSection = document.getElementById('resultsSection');
const extractedText = document.getElementById('extractedText');
const textContent = document.getElementById('textContent');
const patternsContainer = document.getElementById('patternsContainer');
const patternsList = document.getElementById('patternsList');
const noPatterns = document.getElementById('noPatterns');
const errorMessage = document.getElementById('errorMessage');
const errorText = document.getElementById('errorText');

let selectedFile = null;

// Pattern type display names
const patternNames = {
  forced_continuity: 'Forced Continuity',
  nagging: 'Nagging',
  obstruction: 'Obstruction',
  confirmshaming: 'Confirmshaming',
  privacy_zuckering: 'Privacy Zuckering',
};

// Event Listeners
dropzone.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', handleFileSelect);
clearBtn.addEventListener('click', clearSelection);
analyzeBtn.addEventListener('click', analyzeImage);

// Drag and Drop
dropzone.addEventListener('dragover', (e) => {
  e.preventDefault();
  dropzone.classList.add('dragover');
});

dropzone.addEventListener('dragleave', () => {
  dropzone.classList.remove('dragover');
});

dropzone.addEventListener('drop', (e) => {
  e.preventDefault();
  dropzone.classList.remove('dragover');

  const files = e.dataTransfer.files;
  if (files.length > 0 && files[0].type.startsWith('image/')) {
    handleFile(files[0]);
  }
});

// File Handling
function handleFileSelect(e) {
  const file = e.target.files[0];
  if (file) {
    handleFile(file);
  }
}

function handleFile(file) {
  selectedFile = file;

  // Show preview
  const reader = new FileReader();
  reader.onload = (e) => {
    imagePreview.src = e.target.result;
    previewContainer.hidden = false;
    dropzone.hidden = true;
    analyzeBtn.disabled = false;
  };
  reader.readAsDataURL(file);

  // Hide previous results/errors
  resultsSection.hidden = true;
  hideError();
}

function clearSelection() {
  selectedFile = null;
  fileInput.value = '';
  previewContainer.hidden = true;
  dropzone.hidden = false;
  analyzeBtn.disabled = true;
  resultsSection.hidden = true;
  hideError();
}

// API Call
async function analyzeImage() {
  if (!selectedFile) return;

  setLoading(true);
  hideError();
  resultsSection.hidden = true;

  const formData = new FormData();
  formData.append('file', selectedFile);

  try {
    const response = await fetch('/detect', {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Server error: ${response.status}`);
    }

    const data = await response.json();
    displayResults(data);
  } catch (error) {
    showError(error.message || 'Failed to analyze image. Please try again.');
  } finally {
    setLoading(false);
  }
}

// UI Updates
function setLoading(loading) {
  analyzeBtn.disabled = loading;
  const btnText = analyzeBtn.querySelector('.btn-text');
  const btnLoader = analyzeBtn.querySelector('.btn-loader');

  if (loading) {
    btnText.textContent = 'Analyzing...';
    btnLoader.hidden = false;
  } else {
    btnText.textContent = 'Analyze Screenshot';
    btnLoader.hidden = true;
  }
}

function displayResults(data) {
  resultsSection.hidden = false;

  // Display extracted text
  if (data.extracted_text && data.extracted_text.trim()) {
    textContent.textContent = data.extracted_text;
    extractedText.hidden = false;
  } else {
    extractedText.hidden = true;
  }

  // Display patterns
  if (data.patterns && data.patterns.length > 0) {
    patternsContainer.hidden = false;
    noPatterns.hidden = true;
    renderPatterns(data.patterns);
  } else {
    patternsContainer.hidden = true;
    noPatterns.hidden = false;
  }

  // Scroll to results
  resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function renderPatterns(patterns) {
  patternsList.innerHTML = patterns
    .map((pattern) => {
      const confidencePercent = Math.round(pattern.confidence * 100);
      const confidenceClass =
        pattern.confidence >= 0.8
          ? 'high-confidence'
          : pattern.confidence < 0.5
          ? 'low-confidence'
          : '';

      return `
            <div class="pattern-card ${confidenceClass}">
                <div class="pattern-header">
                    <span class="pattern-type ${pattern.pattern_type}">
                        ${
                          patternNames[pattern.pattern_type] ||
                          pattern.pattern_type
                        }
                    </span>
                    <span class="confidence-badge">${confidencePercent}% confidence</span>
                </div>
                <div class="confidence-bar">
                    <div class="confidence-fill" style="width: ${confidencePercent}%"></div>
                </div>
                <div class="pattern-evidence">"${escapeHtml(
                  pattern.evidence
                )}"</div>
                <div class="pattern-explanation">${escapeHtml(
                  pattern.explanation
                )}</div>
            </div>
        `;
    })
    .join('');
}

function showError(message) {
  errorText.textContent = message;
  errorMessage.hidden = false;
}

function hideError() {
  errorMessage.hidden = true;
}

// Utility
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}
