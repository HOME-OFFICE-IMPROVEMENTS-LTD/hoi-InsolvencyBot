#!/usr/bin/env python3
"""
InsolvencyBot Web Demo

A simple Flask web application to demonstrate the InsolvencyBot's capabilities.
This provides a web interface where users can enter insolvency-related questions
and receive legally-informed responses.
"""

import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# App startup timestamp
import time
app.config['START_TIME'] = time.time()
app.config['REQUESTS_SERVED'] = 0

# Get API configuration from environment variables
API_URL = os.environ.get("INSOLVENCYBOT_API_URL", "http://localhost:8000")
API_KEY = os.environ.get("INSOLVENCYBOT_API_KEY", "")

@app.before_request
def count_request():
    """Increment the requests counter before processing each request."""
    app.config['REQUESTS_SERVED'] += 1

# Request middleware for tracking
@app.before_request
def before_request():
    """Execute before each request to track metrics."""
    app.config['REQUESTS_SERVED'] += 1
    
def format_uptime(seconds):
    """
    Format uptime seconds into a human-readable string.
    
    Args:
        seconds: Uptime in seconds
        
    Returns:
        str: Formatted uptime string (e.g. "2d 5h 30m 10s")
    """
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    return f"{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s"

@app.route('/')
def home():
    """Render the home page."""
    # Determine which UI version to use based on environment variable
    use_enhanced_ui = os.environ.get("INSOLVENCYBOT_USE_ENHANCED_UI", "true").lower() == "true"
    template = 'improved_index.html' if use_enhanced_ui else 'index.html'
    return render_template(template)

@app.route('/status')
def status():
    """Render the system status page with diagnostic information."""
    # Get API status
    api_status = {"status": "unknown"}
    try:
        headers = {"Content-Type": "application/json"}
        if API_KEY:
            headers["api-key"] = API_KEY
        
        # Try to connect to the API
        response = requests.get(f"{API_URL}/", headers=headers, timeout=5)
        if response.status_code == 200:
            api_status = {
                "status": "online",
                "version": response.json().get("version", "unknown"),
                "response_time_ms": response.elapsed.total_seconds() * 1000,
                "endpoint": API_URL
            }
        else:
            api_status = {
                "status": "error",
                "status_code": response.status_code,
                "response_time_ms": response.elapsed.total_seconds() * 1000,
                "endpoint": API_URL
            }
    except Exception as e:
        api_status = {
            "status": "offline",
            "error": str(e),
            "endpoint": API_URL
        }
    
    # Get web application status
    import platform
    import sys
    import datetime
    
    # Calculate uptime
    current_time = time.time()
    uptime_seconds = int(current_time - app.config['START_TIME'])
    uptime_formatted = format_uptime(uptime_seconds)
    
    web_status = {
        "python_version": sys.version,
        "platform": platform.platform(),
        "uptime_seconds": uptime_seconds,
        "uptime_formatted": uptime_formatted,
        "requests_served": app.config['REQUESTS_SERVED']
    }
    
    # Diagnostic information
    import psutil
    try:
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        diagnostic = {
            "memory_usage_mb": memory_info.rss / (1024 * 1024),
            "cpu_percent": process.cpu_percent(interval=1.0),
            "threads": process.num_threads(),
            "disk_usage_percent": psutil.disk_usage('/').percent
        }
    except Exception:
        # If psutil is not available or fails
        diagnostic = {
            "error": "Could not retrieve system information",
            "recommendation": "Install psutil for better diagnostics"
        }
    
    # Determine which UI version to use based on environment variable
    use_enhanced_ui = os.environ.get("INSOLVENCYBOT_USE_ENHANCED_UI", "true").lower() == "true"
    template = 'improved_status.html' if use_enhanced_ui else 'status.html'
    
    return render_template(template, 
                          api_status=api_status,
                          web_status=web_status,
                          diagnostic=diagnostic,
                          now=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

@app.route('/api/ask', methods=['POST'])
def ask():
    """API endpoint to handle question submission."""
    data = request.json
    question = data.get('question', '')
    model = data.get('model', 'gpt-3.5-turbo')
    test_connection = data.get('test_connection', False)
    
    # For test connection requests, just verify API connectivity
    if test_connection:
        try:
            headers = {"Content-Type": "application/json"}
            if API_KEY:
                headers["api-key"] = API_KEY
            
            # Make a quick test request to the API
            response = requests.get(f"{API_URL}/", headers=headers, timeout=5)
            
            if response.status_code == 200:
                return jsonify({
                    "_response": "API connection successful",
                    "legislation": [],
                    "cases": [],
                    "forms": []
                })
            else:
                return jsonify({'error': f"API error: {response.status_code}"}), response.status_code
        except requests.RequestException as e:
            return jsonify({'error': f"Failed to connect to API: {str(e)}"}), 500
    
    # Normal question processing
    if not question:
        return jsonify({'error': 'Question is required'}), 400
    
    try:
        # Forward the request to our FastAPI backend
        headers = {"Content-Type": "application/json"}
        if API_KEY:
            headers["api-key"] = API_KEY
        
        api_data = {
            "question": question,
            "model": model
        }
        
        response = requests.post(f"{API_URL}/ask", headers=headers, json=api_data, timeout=60)
        
        if response.status_code != 200:
            error_msg = f"API error: {response.status_code} - {response.text}"
            return jsonify({'error': error_msg}), 500
        
        result = response.json()
        
        # Convert the FastAPI response format to what the UI expects
        return jsonify({
            "response": result.get("response", ""),
            "_response": result.get("response", ""),  # For backward compatibility
            "legislation": result.get("legislation", []),
            "cases": result.get("cases", []),
            "forms": result.get("forms", [])
        })
    except requests.RequestException as e:
        return jsonify({'error': f"Failed to connect to API: {str(e)}"}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """API endpoint to handle user feedback on responses."""
    try:
        data = request.json
        feedback_type = data.get('feedback_type', '')
        question = data.get('question', '')
        model = data.get('model', '')
        app.logger.info(f"Feedback received: {feedback_type} for question: '{question}' using model: {model}")
        return jsonify({"status": "success", "message": "Feedback recorded"})
    except Exception as e:
        app.logger.error(f"Error processing feedback: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Removed duplicate status route implementation and broken code

def format_uptime(seconds):
    """Convert seconds to a human-readable uptime format.
    
    Args:
        seconds: The uptime in seconds
        
    Returns:
        A string representation of the uptime (e.g., "2d 3h 45m 30s")
    """
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    return f"{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s"

# Update the create_templates_folder function to also create the status.html template
def create_templates_folder():
    """Create templates folder with required HTML templates if they don't exist."""
    os.makedirs('templates', exist_ok=True)
    
    # Create a simple HTML template
    html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>InsolvencyBot Demo</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
        }
        h1 {
            color: #333;
            text-align: center.
        }
        .container {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        .form-group {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }
        label {
            font-weight: bold;
        }
        textarea, select {
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-family: inherit;
        }
        button {
            padding: 10px 15px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover {
            background-color: #45a049;
        }
        .response {
            margin-top: 20px;
            border-left: 4px solid #4CAF50;
            padding-left: 10px;
            display: none;
        }
        .response h2 {
            margin-top: 0;
        }
        .citations {
            margin-top: 20px;
            background-color: #f9f9f9;
            padding: 15px;
            border-radius: 4px;
        }
        .loading {
            text-align: center;
            display: none;
        }
        .error {
            color: red;
            border-left: 4px solid red;
            padding-left: 10px;
            margin-top: 20px;
            display: none;
        }
        .status {
            text-align: center;
            font-size: 0.9em;
            color: #666;
            margin-top: 30px;
            padding-top: 15px;
            border-top: 1px solid #eee;
        }
        .status.connected {
            color: #4CAF50;
        }
        .status.disconnected {
            color: #f44336;
        }
    </style>
</head>
<body>
    <h1>InsolvencyBot Demo</h1>
    <p>Ask any question about UK insolvency law and get a response backed by legislation, case law, and relevant forms.</p>
    
    <div class="container">
        <div class="form-group">
            <label for="question">Your Question:</label>
            <textarea id="question" rows="5" placeholder="E.g., What happens if my company can't pay its debts?"></textarea>
        </div>
        
        <div class="form-group">
            <label for="model">Model:</label>
            <select id="model">
                <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                <option value="gpt-4">GPT-4</option>
                <option value="gpt-4o">GPT-4o</option>
            </select>
        </div>
        
        <button onclick="askQuestion()">Get Answer</button>
        
        <div class="loading" id="loading">
            <p>Generating response... This may take a moment.</p>
        </div>
        
        <div class="error" id="error"></div>
        
        <div class="response" id="response">
            <h2>Answer</h2>
            <div id="answer-text"></div>
            
            <div class="citations">
                <h3>References</h3>
                <div>
                    <h4>Legislation</h4>
                    <ul id="legislation"></ul>
                </div>
                <div>
                    <h4>Cases</h4>
                    <ul id="cases"></ul>
                </div>
                <div>
                    <h4>Forms</h4>
                    <ul id="forms"></ul>
                </div>
            </div>
        </div>
        
        <div class="status" id="api-status">
            Checking API status...
        </div>
    </div>
    
    <script>
        // Check API connection on load
        window.addEventListener('DOMContentLoaded', checkApiStatus);
        
        async function checkApiStatus() {
            const statusElement = document.getElementById('api-status');
            try {
                const response = await fetch('/api/ask', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        question: 'test connection', 
                        model: 'gpt-3.5-turbo',
                        test_connection: true 
                    })
                });
                
                if (response.ok) {
                    statusElement.textContent = 'Connected to InsolvencyBot API';
                    statusElement.className = 'status connected';
                } else {
                    statusElement.textContent = 'API connected but returned an error';
                    statusElement.className = 'status disconnected';
                }
            } catch (error) {
                statusElement.textContent = 'Not connected to InsolvencyBot API - backend may be offline';
                statusElement.className = 'status disconnected';
                console.error('API connection error:', error);
            }
        }
        
        async function askQuestion() {
            const question = document.getElementById('question').value.trim();
            const model = document.getElementById('model').value;
            
            if (!question) {
                showError('Please enter a question');
                return;
            }
            
            // Show loading and hide previous results
            document.getElementById('loading').style.display = 'block';
            document.getElementById('response').style.display = 'none';
            document.getElementById('error').style.display = 'none';
            
            try {
                const response = await fetch('/api/ask', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ question, model }),
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.error || 'Failed to get response');
                }
                
                // Update the UI with the response
                document.getElementById('answer-text').innerHTML = data._response.replace(/\\n/g, '<br>');
                
                // Clear previous lists
                document.getElementById('legislation').innerHTML = '';
                document.getElementById('cases').innerHTML = '';
                document.getElementById('forms').innerHTML = '';
                
                // Add legislation
                if (data.legislation && data.legislation.length > 0) {
                    data.legislation.forEach(item => {
                        const li = document.createElement('li');
                        li.textContent = item;
                        document.getElementById('legislation').appendChild(li);
                    });
                } else {
                    document.getElementById('legislation').innerHTML = '<li>None cited</li>';
                }
                
                // Add cases
                if (data.cases && data.cases.length > 0) {
                    data.cases.forEach(item => {
                        const li = document.createElement('li');
                        li.textContent = item;
                        document.getElementById('cases').appendChild(li);
                    });
                } else {
                    document.getElementById('cases').innerHTML = '<li>None cited</li>';
                }
                
                // Add forms
                if (data.forms && data.forms.length > 0) {
                    data.forms.forEach(item => {
                        const li = document.createElement('li');
                        li.textContent = item;
                        document.getElementById('forms').appendChild(li);
                    });
                } else {
                    document.getElementById('forms').innerHTML = '<li>None cited</li>';
                }
                
                // Show the response
                document.getElementById('response').style.display = 'block';
            } catch (error) {
                showError(error.message || 'An error occurred');
            } finally {
                document.getElementById('loading').style.display = 'none';
            }
        }
        
        function showError(message) {
            const errorElement = document.getElementById('error');
            errorElement.textContent = message;
            errorElement.style.display = 'block';
        }
    </script>
</body>
</html>
"""
    
    with open('templates/index.html', 'w') as f:
        f.write(html)
    
    # Create status.html template
    status_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>System Status</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .status-section {
            margin-bottom: 20px;
        }
        .status-section h2 {
            margin-top: 0;
        }
        .status-section pre {
            background-color: #f9f9f9;
            padding: 10px;
            border-radius: 4px;
            overflow-x: auto;
        }
    </style>
</head>
<body>
    <h1>System Status</h1>
    
    <div class="status-section">
        <h2>API Status</h2>
        <pre>{{ api_status | tojson(indent=2) }}</pre>
    </div>
    
    <div class="status-section">
        <h2>Web Application Status</h2>
        <pre>{{ web_status | tojson(indent=2) }}</pre>
    </div>
    
    <div class="status-section">
        <h2>Diagnostic Information</h2>
        <pre>{{ diagnostic | tojson(indent=2) }}</pre>
    </div>
</body>
</html>
"""
    
    with open('templates/status.html', 'w') as f:
        f.write(status_html)

if __name__ == '__main__':
    # Create necessary templates
    create_templates_folder()
    
    # Check for API URL and key
    api_url = os.environ.get("INSOLVENCYBOT_API_URL", "http://localhost:8000")
    
    print(f"Using InsolvencyBot API at {api_url}")
    if os.environ.get("INSOLVENCYBOT_API_KEY"):
        print("API authentication is enabled")
    else:
        print("Warning: API authentication is not enabled. API requests may fail if the API requires authentication.")
    
    # Set the start time for the status page
    from datetime import datetime
    os.environ["FLASK_START_TIME"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Get the port from environment variable or default to 5000
    port = int(os.environ.get("FLASK_PORT", 5000))
    
    # Start the Flask server
    print(f"Starting web interface on http://localhost:{port}")
    app.run(debug=True, host='0.0.0.0', port=port)
