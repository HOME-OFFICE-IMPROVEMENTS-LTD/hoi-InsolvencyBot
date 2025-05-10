#!/usr/bin/env python3
"""
Enhanced Load Testing Script for InsolvencyBot API

This script performs advanced load testing on the InsolvencyBot API by sending
multiple concurrent requests and measuring various performance metrics.

Usage:
  python enhanced_load_test.py --concurrency 10 --requests 50 --api-url http://localhost:8000

Features:
  - Concurrent request handling
  - Response time statistics and visualization
  - Error rate analysis
  - Progressive load testing (ramp up)
  - Performance under sustained load
  - Detailed reporting

Requirements:
  - Python 3.7+
  - requests
  - matplotlib
  - numpy
  - tqdm (for progress bars)
"""

import os
import time
import sys
import argparse
import concurrent.futures
import json
import random
import statistics
from datetime import datetime
import requests
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
from tqdm import tqdm

# Sample insolvency questions for testing with varying complexity
SAMPLE_QUESTIONS = [
    # Simple questions
    "What happens if my company can't pay its debts?",
    "How do I know if my company is insolvent?",
    "What is a company voluntary arrangement?",
    "What is the difference between liquidation and administration?",
    "Can I be personally liable for my limited company's debts?",
    
    # Medium complexity questions
    "What are the duties of directors in an insolvent company?",
    "What happens to employees when a company goes into administration?",
    "Can a company continue trading during insolvency?",
    "What is the process for applying for administration?",
    "How long does the liquidation process take?",
    
    # Complex questions
    "What are the differences between CVA, administration, and liquidation for a company facing financial difficulty?",
    "How does insolvency legislation in the UK handle secured versus unsecured creditors?",
    "What are the wrongful trading provisions under the Insolvency Act and how do they affect directors?",
    "Can you explain the priority order of creditor claims in insolvency proceedings?",
    "What legal remedies are available to creditors when a debtor company becomes insolvent?"
]

# Define question complexity categories for analysis
QUESTION_COMPLEXITY = {
    "simple": SAMPLE_QUESTIONS[:5],
    "medium": SAMPLE_QUESTIONS[5:10],
    "complex": SAMPLE_QUESTIONS[10:]
}

def send_request(api_url: str, question: str, model: str = "gpt-3.5-turbo", 
                 api_key: str = None, timeout: int = 60) -> Tuple[Dict[str, Any], float, bool]:
    """
    Send a request to the API and measure response time.
    
    Args:
        api_url: The URL of the InsolvencyBot API
        question: The insolvency question to ask
        model: The model to use (default: gpt-3.5-turbo)
        api_key: Optional API key for authentication
        timeout: Request timeout in seconds
    
    Returns:
        Tuple of (response_data, response_time, success)
    """
    start_time = time.time()
    success = True
    response_data = {}
    
    try:
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["api-key"] = api_key
            
        payload = {
            "question": question,
            "model": model
        }
        
        response = requests.post(
            f"{api_url.rstrip('/')}/ask",
            headers=headers,
            json=payload,
            timeout=timeout
        )
        
        if response.status_code == 200:
            response_data = response.json()
        else:
            success = False
            response_data = {
                "error": f"API returned status code {response.status_code}",
                "response": response.text[:100]
            }
    except requests.RequestException as e:
        success = False
        response_data = {"error": str(e)}
    except Exception as e:
        success = False
        response_data = {"error": f"Unexpected error: {str(e)}"}
    
    response_time = time.time() - start_time
    return response_data, response_time, success

def run_test(api_url: str, concurrency: int, num_requests: int, model: str,
             api_key: Optional[str] = None, ramp_up: bool = False) -> Dict[str, Any]:
    """
    Run a load test with the specified parameters.
    
    Args:
        api_url: The URL of the InsolvencyBot API
        concurrency: Number of concurrent requests
        num_requests: Total number of requests to send
        model: The model to use
        api_key: Optional API key for authentication
        ramp_up: Whether to gradually increase load
        
    Returns:
        Dictionary with test results
    """
    print(f"\n{'=' * 50}")
    print(f"Starting load test with {concurrency} concurrent users, {num_requests} total requests")
    print(f"API URL: {api_url}, Model: {model}")
    print(f"{'=' * 50}\n")
    
    # Prepare questions (cycle through them if needed)
    questions = []
    for i in range(num_requests):
        questions.append(SAMPLE_QUESTIONS[i % len(SAMPLE_QUESTIONS)])
    
    # Track results
    response_times = []
    success_count = 0
    error_count = 0
    responses = []
    
    # If ramping up, calculate batches
    if ramp_up:
        # Divide into 5 batches with increasing concurrency
        batch_size = num_requests // 5
        max_workers_progression = [
            max(1, int(concurrency * 0.2)),
            max(1, int(concurrency * 0.4)),
            max(1, int(concurrency * 0.6)),
            max(1, int(concurrency * 0.8)),
            concurrency
        ]
        
        batched_questions = []
        for i in range(5):
            start_idx = i * batch_size
            end_idx = start_idx + batch_size if i < 4 else num_requests
            batched_questions.append(questions[start_idx:end_idx])
            
        print("Ramping up load gradually:")
        for i, (batch, max_workers) in enumerate(zip(batched_questions, max_workers_progression)):
            print(f"  Batch {i+1}/5: {len(batch)} requests with {max_workers} concurrent users")
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_question = {
                    executor.submit(send_request, api_url, q, model, api_key): q for q in batch
                }
                
                for future in tqdm(concurrent.futures.as_completed(future_to_question), 
                                  total=len(batch), desc=f"Batch {i+1}"):
                    question = future_to_question[future]
                    try:
                        response_data, response_time, success = future.result()
                        response_times.append(response_time)
                        responses.append({
                            "question": question,
                            "response": response_data,
                            "time": response_time,
                            "success": success
                        })
                        
                        if success:
                            success_count += 1
                        else:
                            error_count += 1
                    except Exception as e:
                        print(f"Exception while processing question: {str(e)}")
                        error_count += 1
                        
            print(f"  Completed batch {i+1} with {max_workers} concurrent users")
            time.sleep(2)  # Brief pause between batches
    else:
        # Standard concurrent execution
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
            future_to_question = {
                executor.submit(send_request, api_url, q, model, api_key): q for q in questions
            }
            
            for future in tqdm(concurrent.futures.as_completed(future_to_question), 
                              total=len(questions), desc="Processing"):
                question = future_to_question[future]
                try:
                    response_data, response_time, success = future.result()
                    response_times.append(response_time)
                    responses.append({
                        "question": question,
                        "response": response_data,
                        "time": response_time,
                        "success": success
                    })
                    
                    if success:
                        success_count += 1
                    else:
                        error_count += 1
                except Exception as e:
                    print(f"Exception while processing question: {str(e)}")
                    error_count += 1
    
    # Calculate statistics
    if response_times:
        avg_response_time = sum(response_times) / len(response_times)
        min_response_time = min(response_times)
        max_response_time = max(response_times)
        median_response_time = statistics.median(response_times)
        p95_response_time = np.percentile(response_times, 95)
        p99_response_time = np.percentile(response_times, 99)
        
        throughput = len(response_times) / sum(response_times) * concurrency
    else:
        avg_response_time = min_response_time = max_response_time = 0
        median_response_time = p95_response_time = p99_response_time = 0
        throughput = 0
    
    # Return results
    return {
        "test_info": {
            "api_url": api_url,
            "concurrency": concurrency,
            "num_requests": num_requests,
            "model": model,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        },
        "statistics": {
            "total_requests": len(responses),
            "successful_requests": success_count,
            "failed_requests": error_count,
            "success_rate": (success_count / len(responses) * 100) if responses else 0,
            "avg_response_time": avg_response_time,
            "min_response_time": min_response_time,
            "max_response_time": max_response_time,
            "median_response_time": median_response_time,
            "p95_response_time": p95_response_time,
            "p99_response_time": p99_response_time,
            "throughput": throughput,  # requests per second
        },
        "raw_data": {
            "response_times": response_times,
            "responses": responses
        }
    }

def generate_report(results: Dict[str, Any], output_dir: str = "./") -> str:
    """
    Generate a detailed HTML report from the test results.
    
    Args:
        results: The test results dictionary
        output_dir: Directory to save the report
        
    Returns:
        Path to the generated report
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Create plots
    create_plots(results, output_dir)
    
    # Format timestamp for filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = os.path.join(output_dir, f"load_test_report_{timestamp}.html")
    
    # Generate HTML report
    with open(report_file, "w") as f:
        f.write(f"""<!DOCTYPE html>
<html>
<head>
    <title>InsolvencyBot API Load Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1, h2 {{ color: #333; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .stats-container {{ display: flex; flex-wrap: wrap; }}
        .stat-box {{ 
            flex: 1 0 200px; 
            margin: 10px; 
            padding: 15px; 
            background-color: #f5f5f5; 
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .stat-value {{ font-size: 24px; font-weight: bold; margin: 10px 0; }}
        .stat-label {{ color: #666; }}
        .success {{ color: #28a745; }}
        .warning {{ color: #ffc107; }}
        .danger {{ color: #dc3545; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #f2f2f2; }}
        tr:hover {{ background-color: #f5f5f5; }}
        .plot {{ margin: 20px 0; text-align: center; }}
        .plot img {{ max-width: 100%; height: auto; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>InsolvencyBot API Load Test Report</h1>
        <p>Generated on {results['test_info']['timestamp']}</p>
        
        <h2>Test Configuration</h2>
        <div class="stats-container">
            <div class="stat-box">
                <div class="stat-label">API URL</div>
                <div class="stat-value">{results['test_info']['api_url']}</div>
            </div>
            <div class="stat-box">
                <div class="stat-label">Concurrency</div>
                <div class="stat-value">{results['test_info']['concurrency']}</div>
            </div>
            <div class="stat-box">
                <div class="stat-label">Total Requests</div>
                <div class="stat-value">{results['test_info']['num_requests']}</div>
            </div>
            <div class="stat-box">
                <div class="stat-label">Model</div>
                <div class="stat-value">{results['test_info']['model']}</div>
            </div>
        </div>
        
        <h2>Test Results</h2>
        <div class="stats-container">
            <div class="stat-box">
                <div class="stat-label">Success Rate</div>
                <div class="stat-value {'success' if results['statistics']['success_rate'] > 95 else 'warning' if results['statistics']['success_rate'] > 80 else 'danger'}">
                    {results['statistics']['success_rate']:.2f}%
                </div>
            </div>
            <div class="stat-box">
                <div class="stat-label">Average Response Time</div>
                <div class="stat-value">
                    {results['statistics']['avg_response_time']:.2f}s
                </div>
            </div>
            <div class="stat-box">
                <div class="stat-label">95th Percentile</div>
                <div class="stat-value">
                    {results['statistics']['p95_response_time']:.2f}s
                </div>
            </div>
            <div class="stat-box">
                <div class="stat-label">Throughput</div>
                <div class="stat-value">
                    {results['statistics']['throughput']:.2f} req/s
                </div>
            </div>
        </div>
        
        <h2>Response Time Statistics</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>Value</th>
            </tr>
            <tr>
                <td>Minimum Response Time</td>
                <td>{results['statistics']['min_response_time']:.2f}s</td>
            </tr>
            <tr>
                <td>Maximum Response Time</td>
                <td>{results['statistics']['max_response_time']:.2f}s</td>
            </tr>
            <tr>
                <td>Average Response Time</td>
                <td>{results['statistics']['avg_response_time']:.2f}s</td>
            </tr>
            <tr>
                <td>Median Response Time</td>
                <td>{results['statistics']['median_response_time']:.2f}s</td>
            </tr>
            <tr>
                <td>95th Percentile Response Time</td>
                <td>{results['statistics']['p95_response_time']:.2f}s</td>
            </tr>
            <tr>
                <td>99th Percentile Response Time</td>
                <td>{results['statistics']['p99_response_time']:.2f}s</td>
            </tr>
        </table>
        
        <h2>Visualizations</h2>
        <div class="plot">
            <h3>Response Time Distribution</h3>
            <img src="response_time_histogram_{timestamp}.png" alt="Response Time Histogram">
        </div>
        <div class="plot">
            <h3>Response Times Over Requests</h3>
            <img src="response_time_scatter_{timestamp}.png" alt="Response Time Scatter Plot">
        </div>
        
        <h2>Error Summary</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>Value</th>
            </tr>
            <tr>
                <td>Successful Requests</td>
                <td>{results['statistics']['successful_requests']} ({results['statistics']['success_rate']:.2f}%)</td>
            </tr>
            <tr>
                <td>Failed Requests</td>
                <td>{results['statistics']['failed_requests']} ({100 - results['statistics']['success_rate']:.2f}%)</td>
            </tr>
        </table>
        
        <p>For detailed individual request data, please refer to the JSON results file.</p>
    </div>
</body>
</html>
""")
    
    # Save raw results to JSON
    json_file = os.path.join(output_dir, f"load_test_results_{timestamp}.json")
    with open(json_file, "w") as f:
        json.dump(results, f, indent=2, default=str)
        
    return report_file

def create_plots(results: Dict[str, Any], output_dir: str) -> None:
    """
    Create visualizations from the test results.
    
    Args:
        results: The test results dictionary
        output_dir: Directory to save the plots
    """
    response_times = results['raw_data']['response_times']
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Set up matplotlib
    plt.figure(figsize=(10, 6))
    
    # Histogram of response times
    plt.hist(response_times, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
    plt.title('Response Time Distribution')
    plt.xlabel('Response Time (seconds)')
    plt.ylabel('Number of Requests')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f"response_time_histogram_{timestamp}.png"))
    plt.close()
    
    # Scatter plot of response times
    plt.figure(figsize=(10, 6))
    plt.scatter(range(len(response_times)), response_times, alpha=0.6, c='blue', edgecolor='black')
    plt.title('Response Times Over Requests')
    plt.xlabel('Request Number')
    plt.ylabel('Response Time (seconds)')
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # Add horizontal lines for statistics
    plt.axhline(y=results['statistics']['avg_response_time'], color='r', linestyle='-', label=f'Average ({results["statistics"]["avg_response_time"]:.2f}s)')
    plt.axhline(y=results['statistics']['median_response_time'], color='g', linestyle='--', label=f'Median ({results["statistics"]["median_response_time"]:.2f}s)')
    plt.axhline(y=results['statistics']['p95_response_time'], color='orange', linestyle='-.', label=f'95th Percentile ({results["statistics"]["p95_response_time"]:.2f}s)')
    
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f"response_time_scatter_{timestamp}.png"))
    plt.close()

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Advanced Load Testing for InsolvencyBot API")
    parser.add_argument("--api-url", default="http://localhost:8000", help="URL of the InsolvencyBot API")
    parser.add_argument("--concurrency", type=int, default=5, help="Number of concurrent requests")
    parser.add_argument("--requests", type=int, default=20, help="Total number of requests to send")
    parser.add_argument("--model", default="gpt-3.5-turbo", help="Model to use for testing")
    parser.add_argument("--api-key", help="API key for authentication")
    parser.add_argument("--output-dir", default="./load_test_results", help="Directory to save results")
    parser.add_argument("--ramp-up", action="store_true", help="Gradually increase load")
    parser.add_argument("--report", action="store_true", help="Generate HTML report")
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.concurrency <= 0:
        print("Error: concurrency must be greater than 0")
        return 1
    
    if args.requests <= 0:
        print("Error: requests must be greater than 0")
        return 1
    
    if args.requests < args.concurrency:
        print("Warning: requests count is less than concurrency. Setting concurrency to requests count.")
        args.concurrency = args.requests
    
    # Run the test
    results = run_test(
        api_url=args.api_url,
        concurrency=args.concurrency,
        num_requests=args.requests,
        model=args.model,
        api_key=args.api_key,
        ramp_up=args.ramp_up
    )
    
    # Print summary results
    print("\nTest Results Summary:")
    print(f"{'=' * 50}")
    print(f"Success Rate: {results['statistics']['success_rate']:.2f}%")
    print(f"Total Requests: {results['statistics']['total_requests']}")
    print(f"Successful: {results['statistics']['successful_requests']}")
    print(f"Failed: {results['statistics']['failed_requests']}")
    print(f"\nResponse Time Statistics:")
    print(f"Average: {results['statistics']['avg_response_time']:.2f}s")
    print(f"Minimum: {results['statistics']['min_response_time']:.2f}s")
    print(f"Maximum: {results['statistics']['max_response_time']:.2f}s")
    print(f"Median: {results['statistics']['median_response_time']:.2f}s")
    print(f"95th Percentile: {results['statistics']['p95_response_time']:.2f}s")
    print(f"99th Percentile: {results['statistics']['p99_response_time']:.2f}s")
    print(f"\nThroughput: {results['statistics']['throughput']:.2f} requests/second")
    print(f"{'=' * 50}")
    
    # Generate report if requested
    if args.report:
        # Ensure output directory exists
        os.makedirs(args.output_dir, exist_ok=True)
        
        # Generate and save report
        report_file = generate_report(results, args.output_dir)
        print(f"\nDetailed HTML report saved to: {report_file}")
        print(f"Raw results saved to: {args.output_dir}/load_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
