/**
 * InsolvencyBot Status Page JavaScript
 * Functions for enhancing the system status monitoring page
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize page
    initStatusPage();
    
    // Set up auto-refresh countdown
    setupAutoRefreshCountdown();
});

/**
 * Initialize status page functionality
 */
function initStatusPage() {
    // Format the last updated time
    updateLastUpdatedTime();
    
    // Set up refresh button
    document.getElementById('refresh-btn').addEventListener('click', function() {
        window.location.reload();
    });
    
    // Style progress bars based on their values
    styleProgressBars();
    
    // Setup collapsible sections if they exist
    setupCollapsibleSections();
}

/**
 * Update the last updated timestamp
 */
function updateLastUpdatedTime() {
    const now = new Date();
    const lastUpdatedElement = document.getElementById('last-updated');
    if (lastUpdatedElement) {
        lastUpdatedElement.textContent = now.toLocaleString();
    }
}

/**
 * Style progress bars based on their percentage values
 */
function styleProgressBars() {
    document.querySelectorAll('.progress-bar').forEach(function(bar) {
        const width = parseFloat(bar.style.width);
        if (width < 50) {
            bar.classList.add('progress-low');
        } else if (width < 80) {
            bar.classList.add('progress-medium');
        } else {
            bar.classList.add('progress-high');
        }
    });
}

/**
 * Setup collapsible sections if they exist on the page
 */
function setupCollapsibleSections() {
    document.querySelectorAll('.collapsible-header').forEach(function(header) {
        header.addEventListener('click', function() {
            const content = this.nextElementSibling;
            
            // Toggle the collapsible content
            if (content.style.maxHeight) {
                content.style.maxHeight = null;
                this.classList.remove('active');
            } else {
                content.style.maxHeight = content.scrollHeight + 'px';
                this.classList.add('active');
            }
        });
    });
}

/**
 * Setup auto-refresh countdown timer
 */
function setupAutoRefreshCountdown() {
    const refreshElement = document.getElementById('refresh-countdown');
    if (!refreshElement) return;
    
    // Parse the meta refresh tag to get the seconds (default to 60)
    let countdown = 60;
    const refreshMeta = document.querySelector('meta[http-equiv="refresh"]');
    if (refreshMeta) {
        const content = refreshMeta.getAttribute('content');
        if (content) {
            countdown = parseInt(content, 10) || countdown;
        }
    }
    
    // Save the original countdown value
    const originalCountdown = countdown;
    
    // Show the spinner during the last 5 seconds
    const spinnerElement = document.querySelector('.spinner-sm');
    if (spinnerElement) {
        spinnerElement.style.display = 'none';
    }
    
    // Create and manage refresh progress bar
    const progressBar = setupRefreshProgressBar();
    
    // Update the countdown every second
    const timer = setInterval(function() {
        countdown--;
        refreshElement.textContent = `Page auto-refreshes in ${countdown} seconds`;
        
        // Show spinner during last 5 seconds
        if (spinnerElement && countdown <= 5) {
            spinnerElement.style.display = 'inline-block';
        }
        
        // When countdown reaches zero, refresh the page
        if (countdown <= 0) {
            clearInterval(timer);
            refreshElement.textContent = `Refreshing now...`;
            window.location.reload();
        }
        
        // Update progress as percentage
        const progressPercent = ((originalCountdown - countdown) / originalCountdown) * 100;
        document.documentElement.style.setProperty('--refresh-progress', `${progressPercent}%`);
        progressBar.style.width = `${progressPercent}%`;
    }, 1000);
}

/**
 * Create and manage refresh progress bar
 */
function setupRefreshProgressBar() {
    // Create progress bar element
    const progressBar = document.createElement('div');
    progressBar.style.position = 'fixed';
    progressBar.style.top = '0';
    progressBar.style.left = '0';
    progressBar.style.height = '3px';
    progressBar.style.background = 'linear-gradient(to right, #2563eb, #3b82f6)';
    progressBar.style.width = '0';
    progressBar.style.zIndex = '1000';
    progressBar.style.transition = 'width 1s linear';
    progressBar.id = 'refresh-progress-bar';
    
    // Add to body
    document.body.prepend(progressBar);
    
    return progressBar;
}
