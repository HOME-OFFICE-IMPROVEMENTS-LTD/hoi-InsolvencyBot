#!/usr/bin/env python
"""
Load Testing Script for InsolvencyBot API

This script performs load testing on the InsolvencyBot API by sending
multiple concurrent requests and measuring response times and success rates.

Usage:
  python load_test.py --concurrency 10 --requests 50 --api-url http://localhost:8000

Requirements:
  - Python 3.7+
  - requests
  - argparse
  - matplotlib
  - numpy
"""

import os
import time
import argparse
import concurrent.futures
import json
import statistics
import requests
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Any, Tuple

# Sample insolvency questions for testing
SAMPLE_QUESTIONS = [
    "What happens if my company can't pay its debts?",
    "Can I be personally liable for my limited company's debts?",
    "What is the difference between liquidation and administration?",
    "How do I know if my company is insolvent?",
    "What happens to employees when a company goes into administration?",
    "Can a company continue trading during insolvency?",
    "What are the duties of directors in an insolvent company?",
    "How long does the liquidation process take?",
    "What is a company voluntary arrangement?",
    "How do I close an insolvent company?"
]

def send_request(api_url: str, question: str, model: str = "gpt-3.5-turbo", 
                 api_key: str = None) -> Tuple[Dict[str, Any], float, bool]:
    """
    Send a request to the API and measure response time.
    
    Returns:
        Tuple of (response_data, response_time, success)
    """
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["api-key"] = api_key
        
    data = {
        "question": question,
        "model": model
    }
    
    start_time = time.time()
    success = False
    response_data = {}
    
    try:
        response = requests.post(
            f"{api_url}/ask",
            json=data,
            headers=headers,
            timeout=120  # 2 minute timeout
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        if response.status_code == 200:
            response_data = response.json()
            success = True
        else:
            response_data = {
                "error": f"API Error: {response.status_code}",
                "details": response.text
            }
            
    except requests.exceptions.Timeout:
        end_time = time.time()
        response_time = end_time - start_time
        response_data = {"error": "Request timed out"}
        
    except Exception as e:
        end_time = time.time()
        response_time = end_time - start_time
        response_data = {"error": str(e)}
    
    return response_data, response_time, success

def run_load_test(api_url: str, concurrency: int, num_requests: int, model: str = "gpt-3.5-turbo",
                 api_key: str = None) -> Dict[str, Any]:
    """
    Run a load test with the specified parameters.
    
    Args:
        api_url: The API URL
        concurrency: Number of concurrent requests
        num_requests: Total number of requests to send
        model: The model to use
        api_key: Optional API key
        
    Returns:
        Dictionary with test results
    """
    print(f"Starting load test with {concurrency} concurrent connections, {num_requests} total requests")
    print(f"API URL: {api_url}")
    print(f"Model: {model}")
    
    # Generate requests (cycling through sample questions)
    requests_data = []
    for i in range(num_requests):
        question = SAMPLE_QUESTIONS[i % len(SAMPLE_QUESTIONS)]
        requests_data.append({
            "id": i + 1,
            "question": question
        })
    
    # Process requests concurrently
    results = []
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        future_to_request = {
            executor.submit(send_request, api_url, req["question"], model, api_key): req
            for req in requests_data
        }
        
        for future in concurrent.futures.as_completed(future_to_request):
            req = future_to_request[future]
            try:
                response_data, response_time, success = future.result()
                results.append({
                    "request_id": req["id"],
                    "question": req["question"],
                    "response_time": response_time,
                    "success": success,
                    "response": response_data
                })
                
                status = "✓" if success else "✗"
                print(f"[{req['id']}/{num_requests}] {status} {response_time:.2f}s: {req['question'][:50]}...")
                
            except Exception as e:
                print(f"[{req['id']}/{num_requests}] ✗ Error: {str(e)}")
                results.append({
                    "request_id": req["id"],
                    "question": req["question"],
                    "response_time": 0,
                    "success": False,
                    "error": str(e)
                })
    
    total_time = time.time() - start_time
    
    # Calculate statistics
    response_times = [r["response_time"] for r in results if r["success"]]
    success_count = sum(1 for r in results if r["success"])
    
    if response_times:
        avg_response_time = statistics.mean(response_times)
        min_response_time = min(response_times)
        max_response_time = max(response_times)
        p95_response_time = np.percentile(response_times, 95)
        std_dev = statistics.stdev(response_times) if len(response_times) > 1 else 0
    else:
        avg_response_time = min_response_time = max_response_time = p95_response_time = std_dev = 0
    
    return {
        "total_requests": num_requests,
        "successful_requests": success_count,
        "failed_requests": num_requests - success_count,
        "success_rate": (success_count / num_requests) * 100,
        "total_time": total_time,
        "requests_per_second": num_requests / total_time,
        "avg_response_time": avg_response_time,
        "min_response_time": min_response_time,
        "max_response_time": max_response_time,
        "p95_response_time": p95_response_time,
        "std_dev_response_time": std_dev,
        "concurrency": concurrency,
        "model": model,
        "results": results
    }

def generate_report(test_results: Dict[str, Any], output_dir: str = "load_test_results"):
    """Generate a report with visualizations."""
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Save raw results
    with open(f"{output_dir}/load_test_results.json", "w") as f:
        json.dump(test_results, f, indent=2)
    
    # Generate summary report
    summary = f"""
    # InsolvencyBot API Load Test Report

    ## Test Parameters
    - **Concurrency:** {test_results['concurrency']}
    - **Total Requests:** {test_results['total_requests']}
    - **Model:** {test_results['model']}

    ## Results Summary
    - **Success Rate:** {test_results['success_rate']:.2f}%
    - **Total Test Duration:** {test_results['total_time']:.2f}s
    - **Requests Per Second:** {test_results['requests_per_second']:.2f}
    - **Average Response Time:** {test_results['avg_response_time']:.2f}s
    - **Min Response Time:** {test_results['min_response_time']:.2f}s
    - **Max Response Time:** {test_results['max_response_time']:.2f}s
    - **95th Percentile Response Time:** {test_results['p95_response_time']:.2f}s
    - **Standard Deviation:** {test_results['std_dev_response_time']:.2f}s
    """
    
    with open(f"{output_dir}/summary.md", "w") as f:
        f.write(summary)
    
    # Generate visualizations if there are successful responses
    if test_results["successful_requests"] > 0:
        # Response time distribution
        response_times = [r["response_time"] for r in test_results["results"] if r["success"]]
        
        plt.figure(figsize=(10, 6))
        plt.hist(response_times, bins=20, alpha=0.7)
        plt.xlabel("Response Time (s)")
        plt.ylabel("Number of Requests")
        plt.title("Response Time Distribution")
        plt.axvline(test_results["avg_response_time"], color='r', linestyle='dashed', 
                    linewidth=1, label=f"Mean: {test_results['avg_response_time']:.2f}s")
        plt.axvline(test_results["p95_response_time"], color='g', linestyle='dashed', 
                    linewidth=1, label=f"95th Percentile: {test_results['p95_response_time']:.2f}s")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.savefig(f"{output_dir}/response_time_distribution.png", dpi=300, bbox_inches="tight")
        
        # Response time over request number
        request_ids = [r["request_id"] for r in test_results["results"] if r["success"]]
        
        plt.figure(figsize=(10, 6))
        plt.scatter(request_ids, response_times, alpha=0.7)
        plt.xlabel("Request ID")
        plt.ylabel("Response Time (s)")
        plt.title("Response Time by Request")
        plt.grid(True, alpha=0.3)
        plt.savefig(f"{output_dir}/response_time_by_request.png", dpi=300, bbox_inches="tight")
    
        print(f"Report generated in directory: {output_dir}")

def main():
    parser = argparse.ArgumentParser(description="Load Testing for InsolvencyBot API")
    parser.add_argument("--concurrency", type=int, default=2, 
                        help="Number of concurrent connections")
    parser.add_argument("--requests", type=int, default=10, 
                        help="Total number of requests to make")
    parser.add_argument("--api-url", type=str, default="http://localhost:8000", 
                        help="API URL")
    parser.add_argument("--model", type=str, default="gpt-3.5-turbo", 
                        choices=["gpt-3.5-turbo", "gpt-4", "gpt-4o"],
                        help="Model to use for testing")
    parser.add_argument("--api-key", type=str, default=os.environ.get("INSOLVENCYBOT_API_KEY"), 
                        help="API key (if required)")
    parser.add_argument("--output-dir", type=str, default="load_test_results", 
                        help="Output directory for results")
    
    args = parser.parse_args()
    
    # Run the load test
    results = run_load_test(
        api_url=args.api_url,
        concurrency=args.concurrency,
        num_requests=args.requests,
        model=args.model,
        api_key=args.api_key
    )
    
    # Generate report
    generate_report(results, args.output_dir)
    
    # Print summary
    print("\n--- Load Test Results ---")
    print(f"Success Rate: {results['success_rate']:.2f}%")
    print(f"Requests Per Second: {results['requests_per_second']:.2f}")
    print(f"Average Response Time: {results['avg_response_time']:.2f}s")
    print(f"95th Percentile Response Time: {results['p95_response_time']:.2f}s")
    print(f"Report saved to: {args.output_dir}/")

if __name__ == "__main__":
    main()
