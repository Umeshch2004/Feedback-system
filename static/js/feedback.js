// Feedback form JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('feedbackForm');
    if (!form) return;
    
    // Form validation
    const strengthsField = document.getElementById('strengths');
    const areasField = document.getElementById('areas_to_improve');
    const sentimentField = document.getElementById('sentiment');
    
    // Character count for text areas
    addCharacterCount(strengthsField, 'strengths-count');
    addCharacterCount(areasField, 'areas-count');
    
    // Form validation on submit
    form.addEventListener('submit', function(e) {
        if (!validateForm()) {
            e.preventDefault();
            return false;
        }
        
        // Show loading state
        const submitButton = form.querySelector('button[type="submit"]');
        const originalText = submitButton.innerHTML;
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Submitting...';
        submitButton.disabled = true;
        
        // Re-enable button after 3 seconds (in case of error)
        setTimeout(() => {
            submitButton.innerHTML = originalText;
            submitButton.disabled = false;
        }, 3000);
    });
    
    // Real-time validation
    [strengthsField, areasField, sentimentField].forEach(field => {
        if (field) {
            field.addEventListener('input', validateField);
            field.addEventListener('blur', validateField);
        }
    });
    
    // Auto-save functionality (optional)
    let saveTimeout;
    [strengthsField, areasField].forEach(field => {
        if (field) {
            field.addEventListener('input', function() {
                clearTimeout(saveTimeout);
                saveTimeout = setTimeout(autosave, 2000);
            });
        }
    });
});

function validateForm() {
    const strengths = document.getElementById('strengths').value.trim();
    const areas = document.getElementById('areas_to_improve').value.trim();
    const sentiment = document.getElementById('sentiment').value;
    
    let isValid = true;
    
    // Validate strengths
    if (strengths.length < 10) {
        showFieldError('strengths', 'Please provide more detailed strengths (at least 10 characters)');
        isValid = false;
    } else {
        clearFieldError('strengths');
    }
    
    // Validate areas to improve
    if (areas.length < 10) {
        showFieldError('areas_to_improve', 'Please provide more detailed improvement areas (at least 10 characters)');
        isValid = false;
    } else {
        clearFieldError('areas_to_improve');
    }
    
    // Validate sentiment
    if (!sentiment) {
        showFieldError('sentiment', 'Please select an overall sentiment');
        isValid = false;
    } else {
        clearFieldError('sentiment');
    }
    
    return isValid;
}

function validateField(e) {
    const field = e.target;
    const value = field.value.trim();
    
    if (field.id === 'strengths' || field.id === 'areas_to_improve') {
        if (value.length > 0 && value.length < 10) {
            showFieldError(field.id, 'Please provide more detail (at least 10 characters)');
        } else {
            clearFieldError(field.id);
        }
    }
}

function showFieldError(fieldId, message) {
    const field = document.getElementById(fieldId);
    const errorDiv = document.getElementById(fieldId + '-error') || createErrorDiv(fieldId);
    
    field.classList.add('is-invalid');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
}

function clearFieldError(fieldId) {
    const field = document.getElementById(fieldId);
    const errorDiv = document.getElementById(fieldId + '-error');
    
    field.classList.remove('is-invalid');
    if (errorDiv) {
        errorDiv.style.display = 'none';
    }
}

function createErrorDiv(fieldId) {
    const field = document.getElementById(fieldId);
    const errorDiv = document.createElement('div');
    errorDiv.id = fieldId + '-error';
    errorDiv.className = 'invalid-feedback';
    errorDiv.style.display = 'none';
    
    field.parentNode.appendChild(errorDiv);
    return errorDiv;
}

function addCharacterCount(field, countId) {
    if (!field) return;
    
    const countDiv = document.createElement('div');
    countDiv.id = countId;
    countDiv.className = 'form-text text-end';
    countDiv.style.fontSize = '0.875rem';
    
    field.parentNode.appendChild(countDiv);
    
    function updateCount() {
        const count = field.value.length;
        countDiv.textContent = `${count} characters`;
        
        if (count < 10) {
            countDiv.className = 'form-text text-end text-warning';
        } else if (count > 500) {
            countDiv.className = 'form-text text-end text-danger';
        } else {
            countDiv.className = 'form-text text-end text-muted';
        }
    }
    
    field.addEventListener('input', updateCount);
    updateCount(); // Initial count
}

function autosave() {
    // This could be implemented to save draft feedback
    // For now, just show a subtle indication
    const form = document.getElementById('feedbackForm');
    if (form) {
        const indicator = document.createElement('small');
        indicator.className = 'text-muted';
        indicator.textContent = 'Draft saved';
        indicator.style.opacity = '0.7';
        
        // Remove any existing indicators
        const existing = form.querySelector('.autosave-indicator');
        if (existing) existing.remove();
        
        indicator.className += ' autosave-indicator';
        form.appendChild(indicator);
        
        // Fade out after 2 seconds
        setTimeout(() => {
            indicator.style.transition = 'opacity 0.5s';
            indicator.style.opacity = '0';
            setTimeout(() => indicator.remove(), 500);
        }, 2000);
    }
}

// Tag input enhancement
document.addEventListener('DOMContentLoaded', function() {
    const tagsInput = document.getElementById('tags');
    if (tagsInput) {
        // Add common tags as suggestions
        const commonTags = [
            'communication', 'leadership', 'teamwork', 'problem-solving',
            'time-management', 'creativity', 'technical-skills', 'collaboration',
            'initiative', 'reliability', 'adaptability', 'mentoring'
        ];
        
        // Create suggestions dropdown
        const suggestionsDiv = document.createElement('div');
        suggestionsDiv.className = 'mt-2';
        suggestionsDiv.innerHTML = '<small class="text-muted">Common tags: </small>';
        
        commonTags.forEach(tag => {
            const tagButton = document.createElement('button');
            tagButton.type = 'button';
            tagButton.className = 'btn btn-sm btn-outline-secondary me-1 mb-1';
            tagButton.textContent = tag;
            tagButton.onclick = () => addTag(tag);
            suggestionsDiv.appendChild(tagButton);
        });
        
        tagsInput.parentNode.appendChild(suggestionsDiv);
    }
});

function addTag(tag) {
    const tagsInput = document.getElementById('tags');
    const currentTags = tagsInput.value.split(',').map(t => t.trim()).filter(t => t);
    
    if (!currentTags.includes(tag)) {
        currentTags.push(tag);
        tagsInput.value = currentTags.join(', ');
    }
}
