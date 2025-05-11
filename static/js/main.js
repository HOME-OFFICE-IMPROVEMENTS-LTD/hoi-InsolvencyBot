/**
 * InsolvencyBot Frontend JS
 * Provides functionality for the improved InsolvencyBot UI
 */

document.addEventListener('DOMContentLoaded', function() {
    // Check API connection on page load
    checkAPIConnection();

    // Form submission handling
    document.getElementById('questionForm').addEventListener('submit', function(e) {
        e.preventDefault();
        submitQuestion();
    });

    // New question button
    document.getElementById('new-question-btn').addEventListener('click', function() {
        resetForm();
    });
    
    // Feedback buttons
    if (document.getElementById('feedback-helpful')) {
        document.getElementById('feedback-helpful').addEventListener('click', function() {
            provideFeedback('helpful');
        });
        
        document.getElementById('feedback-not-helpful').addEventListener('click', function() {
            provideFeedback('not_helpful');
        });
    }

    // Example question links
    document.querySelectorAll('.example-question').forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            document.getElementById('question').value = this.textContent;
            document.getElementById('question').focus();
            // Scroll to form
            document.querySelector('.question-section').scrollIntoView({ behavior: 'smooth' });
        });
    });
});

/**
 * Check API connection and update status indicators
 */
function checkAPIConnection() {
    const statusDot = document.getElementById('status-dot');
    const statusText = document.getElementById('status-text');
    
    if (!statusDot || !statusText) return; // Elements not found
    
    // Set status to connecting
    statusDot.className = 'status-indicator status-warning';
    statusText.textContent = 'Connecting to API...';
    
    fetch('/api/ask', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            test_connection: true
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data._response) {
            statusDot.className = 'status-indicator status-online';
            statusText.textContent = 'API Connected';
        } else {
            throw new Error('API response format invalid');
        }
    })
    .catch(error => {
        statusDot.className = 'status-indicator status-offline';
        statusText.textContent = 'API Not Connected';
        console.error('API Connection Error:', error);
    });
}

/**
 * Submit a question to the API and display the response
 */
function submitQuestion() {
    const question = document.getElementById('question').value.trim();
    const model = document.getElementById('model').value;
    const submitBtn = document.getElementById('submitBtn');
    
    if (!question) {
        showError('Please enter a question.');
        return;
    }
    
    // Show loading states
    document.getElementById('loading').style.display = 'block';
    document.getElementById('error').style.display = 'none';
    document.getElementById('response-container').style.display = 'none';
    
    // Update button to show loading state
    const originalBtnText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="bi bi-arrow-repeat spin"></i> Processing...';
    submitBtn.classList.add('btn-loading');
    
    // Start a timer to estimate completion
    const startTime = new Date();
    let dots = "";
    const loadingInterval = setInterval(() => {
        dots = dots.length >= 3 ? "" : dots + ".";
        document.getElementById('loading').querySelector('p').textContent = `Processing your question${dots} (${Math.round((new Date() - startTime)/1000)}s)`;
    }, 1000);
    
    // Submit to API
    fetch('/api/ask', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            question: question,
            model: model
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        displayResponse(data);
    })
    .catch(error => {
        showError('Failed to get a response: ' + error.message);
    })
    .finally(() => {
        // Reset UI states
        clearInterval(loadingInterval);
        document.getElementById('loading').style.display = 'none';
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalBtnText;
        submitBtn.classList.remove('btn-loading');
    });
}

/**
 * Display the API response in the UI
 */
function displayResponse(data) {
    // Calculate response time
    const endTime = new Date();
    const responseTime = data.processing_time ? 
                        (data.processing_time / 1000).toFixed(2) : 
                        'unknown';
    
    // Hide loading
    document.getElementById('loading').style.display = 'none';
    
    // Show response container
    const responseContainer = document.getElementById('response-container');
    responseContainer.style.display = 'block';
    
    // Set response text - handle different response formats
    const responseText = data.response || data._response || '';
    document.getElementById('response-text').innerHTML = formatText(responseText);
    
    // Add response metadata if container exists
    const metadataContainer = document.getElementById('response-metadata');
    if (metadataContainer) {
        const model = data.model || document.getElementById('model').value;
        metadataContainer.innerHTML = `
            <div class="response-meta-item">
                <i class="bi bi-clock"></i> Response time: <strong>${responseTime}s</strong>
            </div>
            <div class="response-meta-item">
                <i class="bi bi-cpu"></i> Model: <strong>${model}</strong>
            </div>
            <div class="response-meta-item">
                <i class="bi bi-calendar3"></i> Date: <strong>${new Date().toLocaleDateString()}</strong>
            </div>
        `;
    }
    
    // Clear previous citation lists
    ['legislation-list', 'cases-list', 'forms-list'].forEach(listId => {
        if (document.getElementById(listId)) {
            document.getElementById(listId).innerHTML = '';
        }
    });
    
    // Helper function to populate citation lists
    function populateCitationList(listId, items) {
        const list = document.getElementById(listId);
        if (!list) return;
        
        if (items && items.length) {
            items.forEach(item => {
                const li = document.createElement('li');
                li.className = 'citation-item';
                li.textContent = item;
                list.appendChild(li);
            });
        } else {
            const li = document.createElement('li');
            li.className = 'citation-item citation-none';
            li.textContent = 'None cited';
            list.appendChild(li);
        }
    }
    
    // Populate all citation lists
    populateCitationList('legislation-list', data.legislation);
    populateCitationList('cases-list', data.cases);
    populateCitationList('forms-list', data.forms);
    
    // Reset feedback status
    if (document.getElementById('feedback-thanks')) {
        document.getElementById('feedback-thanks').style.display = 'none';
        document.getElementById('feedback-thanks').className = 'feedback-thanks mt-2';
    }
    
    // Re-enable any disabled feedback buttons
    document.querySelectorAll('.feedback-section button').forEach(button => {
        button.disabled = false;
        button.classList.remove('btn-disabled');
    });
    
    // Scroll to response
    responseContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

/**
 * Format the text response with markdown-like formatting
 */
function formatText(text) {
    if (!text) return '';
    
    // Handle code blocks first (to avoid conflicts with other formatters)
    text = text.replace(/```([^`]*?)```/g, '<pre class="code-block">$1</pre>');
    
    // Handle inline code
    text = text.replace(/`([^`]*?)`/g, '<code>$1</code>');
    
    // Convert headers (## Header)
    text = text.replace(/^## (.*?)$/gm, '<h2>$1</h2>');
    text = text.replace(/^### (.*?)$/gm, '<h3>$1</h3>');
    text = text.replace(/^#### (.*?)$/gm, '<h4>$1</h4>');
    
    // Bold text
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Italicize text
    text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    // Handle bullet lists
    text = text.replace(/^\s*-\s+(.*?)$/gm, '<li>$1</li>');
    text = text.replace(/(<li>.*?<\/li>)\n(<li>.*?<\/li>)/gs, '$1$2');
    text = text.replace(/(<li>.*?<\/li>)+/g, '<ul>$&</ul>');
    
    // Convert line breaks to paragraphs (skip if inside lists)
    const paragraphs = [];
    const segments = text.split(/(<\/?ul>|<h[2-4]>.*?<\/h[2-4]>|<pre.*?<\/pre>)/g);
    
    segments.forEach(segment => {
        if (segment.startsWith('<ul>') || 
            segment.startsWith('</ul>') || 
            segment.startsWith('<h') || 
            segment.startsWith('<pre')) {
            // Keep HTML elements as-is
            paragraphs.push(segment);
        } else {
            // Process normal text
            paragraphs.push(segment.split('\n\n')
                .map(para => para.trim() ? `<p>${para}</p>` : '')
                .join(''));
        }
    });
    
    text = paragraphs.join('');
    
    // Handle single line breaks (outside of special blocks)
    text = text.replace(/(<\/p>)<p>/g, '$1\n<p>');
    text = text.replace(/\n(?![<])/g, '<br>');
    
    return text;
}

/**
 * Show an error message with details if available
 * @param {string} message - Main error message
 * @param {Error|null} error - Optional Error object for details
 */
function showError(message, error = null) {
    const errorDiv = document.getElementById('error');
    const errorMessage = document.getElementById('error-message');
    let displayMessage = message;
    
    // Add error details if available
    if (error && error.message) {
        const errorDetails = document.createElement('div');
        errorDetails.className = 'error-details';
        errorDetails.innerHTML = `
            <small class="text-muted">
                <strong>Details:</strong> ${error.message}
                ${error.stack ? `<br><a href="#" class="toggle-stack">Show technical details</a>
                <div class="stack-trace" style="display: none;"><pre>${error.stack}</pre></div>` : ''}
            </small>
        `;
        
        // Set main message
        errorMessage.textContent = message;
        
        // Clear and append details
        while (errorMessage.nextSibling) {
            errorMessage.parentNode.removeChild(errorMessage.nextSibling);
        }
        errorMessage.parentNode.appendChild(errorDetails);
        
        // Add event listener for toggling stack trace
        const toggleStackLink = errorDetails.querySelector('.toggle-stack');
        if (toggleStackLink) {
            toggleStackLink.addEventListener('click', function(e) {
                e.preventDefault();
                const stackTrace = this.nextElementSibling;
                if (stackTrace.style.display === 'none') {
                    stackTrace.style.display = 'block';
                    this.textContent = 'Hide technical details';
                } else {
                    stackTrace.style.display = 'none';
                    this.textContent = 'Show technical details';
                }
            });
        }
    } else {
        // Simple error without details
        errorMessage.textContent = message;
    }
    
    // Show error and scroll to it
    errorDiv.style.display = 'block';
    errorDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
    
    // Log to console
    console.error('Error:', message, error || '');
}

/**
 * Reset the form to ask another question
 */
function resetForm() {
    // Clear the question input
    document.getElementById('question').value = '';
    
    // Hide response and error
    document.getElementById('response-container').style.display = 'none';
    document.getElementById('error').style.display = 'none';
    
    // Hide feedback thank you message if it exists
    if (document.getElementById('feedback-thanks')) {
        document.getElementById('feedback-thanks').style.display = 'none';
    }
    
    // Focus back on question input
    document.getElementById('question').focus();
    
    // Scroll back to question section
    document.querySelector('.question-section').scrollIntoView({ behavior: 'smooth' });
}

/**
 * Send feedback about the response
 */
function provideFeedback(feedbackType) {
    // Log the feedback type
    console.log(`Feedback provided: ${feedbackType}`);
    
    // Get elements
    const thanksElement = document.getElementById('feedback-thanks');
    const feedbackButtons = document.querySelectorAll('.feedback-section button');
    
    // Disable feedback buttons to prevent multiple submissions
    feedbackButtons.forEach(button => {
        button.disabled = true;
        button.classList.add('btn-disabled');
    });
    
    // Show thank you message with loading state
    thanksElement.innerHTML = '<i class="bi bi-arrow-repeat spin"></i> Submitting feedback...';
    thanksElement.style.display = 'block';
    
    // Send feedback to server
    fetch('/api/feedback', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            feedback_type: feedbackType,
            question: document.getElementById('question').value,
            model: document.getElementById('model').value
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // Show success message
        thanksElement.innerHTML = '<i class="bi bi-check-circle"></i> Thank you for your feedback!';
        thanksElement.classList.add('text-success');
    })
    .catch(error => {
        // Show error message
        console.error('Feedback submission error:', error);
        thanksElement.innerHTML = '<i class="bi bi-exclamation-triangle"></i> Could not submit feedback';
        thanksElement.classList.add('text-error');
        
        // Re-enable buttons
        feedbackButtons.forEach(button => {
            button.disabled = false;
            button.classList.remove('btn-disabled');
        });
    });
}
