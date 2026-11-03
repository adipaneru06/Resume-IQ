/**
 * Resumely AI — Upload and Micro-Interactions Controller
 * Drives real-time backend progress without fake timers.
 */

function toggleJdSection() {
  const container = document.getElementById('jd-input-container');
  const icon = document.getElementById('jd-toggle-icon');
  if (!container || !icon) return;

  if (container.classList.contains('hidden')) {
    container.classList.remove('hidden');
    icon.textContent = 'remove';
  } else {
    container.classList.add('hidden');
    icon.textContent = 'add';
  }
}

function showError(message) {
  const errorBox = document.getElementById('upload-error-box');
  const errorText = document.getElementById('upload-error-text');
  if (errorBox && errorText) {
    errorText.textContent = message;
    errorBox.classList.remove('hidden');
  }
}

function clearError() {
  const errorBox = document.getElementById('upload-error-box');
  if (errorBox) {
    errorBox.classList.add('hidden');
  }
}

function formatBytes(bytes) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function validateFile(file) {
  clearError();
  const allowedExtensions = ['pdf', 'png', 'jpg', 'jpeg'];
  const ext = file.name.split('.').pop().toLowerCase();

  if (!allowedExtensions.includes(ext)) {
    showError(`Unsupported file format (.${ext}). Only PDF, PNG, and JPG files are accepted.`);
    return false;
  }

  const maxBytes = 5 * 1024 * 1024; // 5MB
  if (file.size > maxBytes) {
    showError(`File size (${formatBytes(file.size)}) exceeds the 5MB limit. Please upload a smaller document.`);
    return false;
  }

  return true;
}

function handleFileSelect(input) {
  if (input.files && input.files[0]) {
    const file = input.files[0];
    if (!validateFile(file)) {
      input.value = '';
      return;
    }

    const label = document.getElementById('file-upload-label');
    const subtext = document.getElementById('file-upload-subtext');
    const dropZone = document.getElementById('drop-zone');

    if (label) {
      label.innerHTML = `Selected file: <strong class="text-primary">${file.name}</strong>`;
    }
    if (subtext) {
      subtext.textContent = `File size: ${formatBytes(file.size)} — Ready for analysis`;
    }
    if (dropZone) {
      dropZone.classList.add('border-primary', 'bg-surface-container-lowest');
    }
  }
}

// Map backend step numbers (1 to 4) to DOM elements
const STEPS_CONFIG = [
  { id: 'step-extract', iconId: 'step-icon-extract', name: 'Extracting text' },
  { id: 'step-ats', iconId: 'step-icon-ats', name: 'Checking ATS format' },
  { id: 'step-match', iconId: 'step-icon-match', name: 'Matching role & keywords' },
  { id: 'step-improve', iconId: 'step-icon-improve', name: 'Finding improvements' }
];

function updateStepUI(currentStep) {
  STEPS_CONFIG.forEach((step, index) => {
    const stepNum = index + 1;
    const el = document.getElementById(step.id);
    const icon = document.getElementById(step.iconId);
    if (!el || !icon) return;

    if (stepNum < currentStep) {
      // Completed step
      el.classList.remove('opacity-50', 'bg-surface');
      el.classList.add('bg-[#EBF5F0]', 'border-[#C4E2D5]');
      icon.className = 'material-symbols-outlined text-primary text-[20px]';
      icon.textContent = 'check_circle';
    } else if (stepNum === currentStep) {
      // Currently active step
      el.classList.remove('opacity-50', 'bg-[#EBF5F0]');
      el.classList.add('bg-surface', 'border-primary');
      icon.className = 'material-symbols-outlined text-primary text-[20px] animate-spin';
      icon.textContent = 'progress_activity';
    } else {
      // Pending step
      el.classList.add('opacity-50');
      el.classList.remove('bg-[#EBF5F0]', 'border-primary');
      icon.className = 'material-symbols-outlined text-outline text-[20px]';
      icon.textContent = 'hourglass_empty';
    }
  });
}

async function handleAnalyzeSubmit() {
  const fileInput = document.getElementById('file-upload-input');
  if (!fileInput.files || fileInput.files.length === 0) {
    const dropZone = document.getElementById('drop-zone');
    if (dropZone) {
      dropZone.classList.add('border-error');
      setTimeout(() => dropZone.classList.remove('border-error'), 1800);
    }
    showError('Please upload or drag a resume document (PDF, PNG, or JPG) to begin analysis.');
    return;
  }

  const file = fileInput.files[0];
  if (!validateFile(file)) return;

  const targetRole = document.getElementById('target-role')?.value || '';
  const jobDescription = document.getElementById('target-jd')?.value || '';

  // Prepare FormData
  const formData = new FormData();
  formData.append('file', file);
  if (targetRole.trim()) {
    formData.append('target_role', targetRole.trim());
  }
  if (jobDescription.trim()) {
    formData.append('job_description', jobDescription.trim());
  }

  // Switch to Analyzing State View
  const formCard = document.getElementById('upload-form');
  const analyzingCard = document.getElementById('analyzing-state');
  if (formCard) formCard.classList.add('hidden');
  if (analyzingCard) analyzingCard.classList.remove('hidden');

  updateStepUI(1);

  try {
    const response = await fetch('/api/analyze', {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.detail || 'Failed to submit resume for analysis.');
    }

    const { job_id } = await response.json();
    if (!job_id) throw new Error('Missing job tracking ID from server.');

    // Poll backend status until complete
    pollJobStatus(job_id);

  } catch (err) {
    if (formCard) formCard.classList.remove('hidden');
    if (analyzingCard) analyzingCard.classList.add('hidden');
    showError(err.message || 'An error occurred while uploading.');
  }
}

function pollJobStatus(jobId) {
  const pollInterval = setInterval(async () => {
    try {
      const res = await fetch(`/api/analyze/status/${jobId}`);
      if (!res.ok) throw new Error('Failed to retrieve job progress.');

      const job = await res.json();

      if (job.step) {
        updateStepUI(job.step);
      }

      if (job.status === 'completed') {
        clearInterval(pollInterval);
        // Mark all steps complete
        updateStepUI(5);
        setTimeout(() => {
          window.location.href = job.redirect_url;
        }, 400);
      } else if (job.status === 'failed') {
        clearInterval(pollInterval);
        const formCard = document.getElementById('upload-form');
        const analyzingCard = document.getElementById('analyzing-state');
        if (formCard) formCard.classList.remove('hidden');
        if (analyzingCard) analyzingCard.classList.add('hidden');
        showError(job.error || 'Analysis process encountered an error.');
      }
    } catch (e) {
      clearInterval(pollInterval);
      const formCard = document.getElementById('upload-form');
      const analyzingCard = document.getElementById('analyzing-state');
      if (formCard) formCard.classList.remove('hidden');
      if (analyzingCard) analyzingCard.classList.add('hidden');
      showError('Lost connection to analysis worker. Please retry.');
    }
  }, 600);
}

// Drag & drop setup
document.addEventListener('DOMContentLoaded', () => {
  const dropZone = document.getElementById('drop-zone');
  if (!dropZone) return;

  ['dragenter', 'dragover'].forEach(eventName => {
    dropZone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropZone.classList.add('border-primary', 'bg-[#FAF8F4]');
    }, false);
  });

  ['dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropZone.classList.remove('bg-[#FAF8F4]');
    }, false);
  });

  dropZone.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    const files = dt.files;
    if (files && files.length > 0) {
      const input = document.getElementById('file-upload-input');
      if (validateFile(files[0])) {
        input.files = files;
        handleFileSelect(input);
      }
    }
  }, false);
});
