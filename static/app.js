// DOM Elements
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const preview = document.getElementById('preview');
const previewImage = document.getElementById('previewImage');
const clearBtn = document.getElementById('clearBtn');
const analyzeBtn = document.getElementById('analyzeBtn');
const loading = document.getElementById('loading');
const results = document.getElementById('results');
const error = document.getElementById('error');
const errorMessage = document.getElementById('errorMessage');

// State
let selectedFile = null;

// Event Listeners
dropZone.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', handleFileSelect);
clearBtn.addEventListener('click', clearSelection);
analyzeBtn.addEventListener('click', analyzeImage);

// Drag and drop handlers
dropZone.addEventListener('dragover', (e) => {
  e.preventDefault();
  dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
  dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (e) => {
  e.preventDefault();
  dropZone.classList.remove('dragover');
  const file = e.dataTransfer.files[0];
  if (file && file.type.startsWith('image/')) {
    handleFile(file);
  }
});

function handleFileSelect(e) {
  const file = e.target.files[0];
  if (file) {
    handleFile(file);
  }
}

function handleFile(file) {
  selectedFile = file;
  const reader = new FileReader();
  reader.onload = (e) => {
    previewImage.src = e.target.result;
    dropZone.classList.add('hidden');
    preview.classList.remove('hidden');
    analyzeBtn.disabled = false;
  };
  reader.readAsDataURL(file);
  hideResults();
}

function clearSelection() {
  selectedFile = null;
  fileInput.value = '';
  preview.classList.add('hidden');
  dropZone.classList.remove('hidden');
  analyzeBtn.disabled = true;
  hideResults();
}

function hideResults() {
  results.classList.add('hidden');
  error.classList.add('hidden');
}

async function analyzeImage() {
  if (!selectedFile) return;

  loading.classList.remove('hidden');
  hideResults();
  analyzeBtn.disabled = true;

  const formData = new FormData();
  formData.append('file', selectedFile);

  try {
    const response = await fetch('/detect', {
      method: 'POST',
      body: formData,
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || 'Analysis failed');
    }

    displayResults(data);
  } catch (err) {
    showError(err.message);
  } finally {
    loading.classList.add('hidden');
    analyzeBtn.disabled = false;
  }
}

function displayResults(data) {
  results.classList.remove('hidden');

  // Display coercion score
  displayCoercionScore(data.coercion_score || 0);

  // Display extracted text
  const extractedText = document.getElementById('extractedText');
  extractedText.textContent = data.extracted_text || 'No text extracted';

  // Display features
  displayFeatures(data.features);

  // Display patterns
  displayPatterns(data.patterns);
}

function displayCoercionScore(score) {
  const scoreFill = document.getElementById('scoreFill');
  const scoreValue = document.getElementById('scoreValue');
  const scoreDescription = document.getElementById('scoreDescription');

  // Animate score fill
  setTimeout(() => {
    scoreFill.style.width = `${score}%`;
  }, 100);

  // Set color based on score
  if (score >= 70) {
    scoreFill.style.background = 'linear-gradient(90deg, #e53e3e, #c53030)';
    scoreDescription.textContent =
      'High risk - Multiple coercive dark patterns detected';
  } else if (score >= 40) {
    scoreFill.style.background = 'linear-gradient(90deg, #ed8936, #dd6b20)';
    scoreDescription.textContent =
      'Medium risk - Some concerning patterns detected';
  } else if (score > 0) {
    scoreFill.style.background = 'linear-gradient(90deg, #ecc94b, #d69e2e)';
    scoreDescription.textContent = 'Low risk - Minor concerns detected';
  } else {
    scoreFill.style.background = 'linear-gradient(90deg, #48bb78, #38a169)';
    scoreDescription.textContent = 'No dark patterns detected';
  }

  scoreValue.textContent = score.toFixed(1);
}

function displayFeatures(features) {
  const featuresSection = document.getElementById('featuresSection');
  const featuresGrid = document.getElementById('featuresGrid');

  if (!features) {
    featuresSection.classList.add('hidden');
    return;
  }

  featuresSection.classList.remove('hidden');
  featuresGrid.innerHTML = '';

  const featureLabels = {
    length_chars: 'Text Length',
    word_count: 'Word Count',
    forced_continuity_keyword_hits: 'Forced Continuity Keywords',
    nagging_keyword_hits: 'Nagging Keywords',
    obstruction_keyword_hits: 'Obstruction Keywords',
    confirmshaming_keyword_hits: 'Confirmshaming Keywords',
    privacy_zuckering_keyword_hits: 'Privacy Zuckering Keywords',
  };

  for (const [key, value] of Object.entries(features)) {
    const label = featureLabels[key] || key;
    const isKeywordHit = key.includes('keyword_hits');
    const hasHits = isKeywordHit && value > 0;

    const featureItem = document.createElement('div');
    featureItem.className = 'feature-item';
    featureItem.innerHTML = `
            <span class="feature-name">${label}</span>
            <span class="feature-value ${
              hasHits ? 'has-hits' : ''
            }">${value}</span>
        `;
    featuresGrid.appendChild(featureItem);
  }
}

function displayPatterns(patterns) {
  const patternsList = document.getElementById('patternsList');

  if (!patterns || patterns.length === 0) {
    patternsList.innerHTML = `
            <div class="no-patterns">
                <p>✅ No dark patterns detected in this screenshot</p>
            </div>
        `;
    return;
  }

  patternsList.innerHTML = patterns
    .map((pattern) => {
      const confidence = pattern.confidence * 100;
      let confidenceClass = 'confidence-low';
      if (confidence >= 70) confidenceClass = 'confidence-high';
      else if (confidence >= 40) confidenceClass = 'confidence-medium';

      const patternTypeLabel = pattern.pattern_type.replace(/_/g, ' ');

      return `
            <div class="pattern-card">
                <div class="pattern-header">
                    <span class="pattern-type">${patternTypeLabel}</span>
                    <span class="confidence-badge ${confidenceClass}">
                        ${confidence.toFixed(0)}% confidence
                    </span>
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
  error.classList.remove('hidden');
  errorMessage.textContent = message;
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}
