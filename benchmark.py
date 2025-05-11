#!/usr/bin/env python3
"""
Performance benchmarking tool for InsolvencyBot.

This script benchmarks different models and configurations of InsolvencyBot,
measuring response time, token usage, and result quality.
"""

import os
import time
import json
import argparse
import statistics
from typing import Dict, List, Any
import concurrent.futures

import pandas as pd
from tqdm import tqdm

from src.hoi_insolvencybot.insolvency_bot import answer_question
from src.hoi_insolvencybot.logging_config import setup_logging, get_logger

# Set up logging
setup_logging()
logger = get_logger(__name__)

# Default models to benchmark
DEFAULT_MODELS = ["gpt-3.5-turbo", "gpt-4", "gpt-4o"]

def run_benchmark_for_model(model: str, questions: List[str], 
                           parallel: bool = False, runs: int = 1) -> Dict[str, Any]:
    """
    Run benchmark for a specific model.
    
    Args:
        model: Model name to benchmark
        questions: List of questions to process
        parallel: Whether to run questions in parallel
        runs: Number of runs for each question to average results
        
    Returns:
        Dictionary with benchmark results
    """
    logger.info(f"Benchmarking model: {model}")
    results = {
        "model": model,
        "questions": len(questions),
        "parallel": parallel,
        "runs": runs,
        "timings": [],
        "legislation_count": [],
        "cases_count": [],
        "forms_count": [],
        "token_count": [],
        "responses": []
    }
    
    def process_question(question: str) -> Dict[str, Any]:
        """Process a single question and collect metrics."""
        question_result = {
            "question": question,
            "timings": [],
            "responses": []
        }
        
        for run in range(runs):
            start_time = time.time()
            response = answer_question(question, verbose=False, model=model)
            elapsed_time = time.time() - start_time
            
            question_result["timings"].append(elapsed_time)
            question_result["responses"].append(response)
            
        return question_result
    
    if parallel:
        # Run questions in parallel using ThreadPoolExecutor
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(process_question, q) for q in questions]
            for future in tqdm(concurrent.futures.as_completed(futures), total=len(questions), desc=f"Model {model}"):
                question_result = future.result()
                results["timings"].extend(question_result["timings"])
                
                for response in question_result["responses"]:
                    results["legislation_count"].append(len(response.get("legislation", [])))
                    results["cases_count"].append(len(response.get("cases", [])))
                    results["forms_count"].append(len(response.get("forms", [])))
                    results["responses"].append(response)
    else:
        # Run questions sequentially
        for question in tqdm(questions, desc=f"Model {model}"):
            question_result = process_question(question)
            results["timings"].extend(question_result["timings"])
            
            for response in question_result["responses"]:
                results["legislation_count"].append(len(response.get("legislation", [])))
                results["cases_count"].append(len(response.get("cases", [])))
                results["forms_count"].append(len(response.get("forms", [])))
                results["responses"].append(response)
    
    # Calculate statistics
    results["avg_time"] = statistics.mean(results["timings"])
    results["median_time"] = statistics.median(results["timings"])
    results["min_time"] = min(results["timings"])
    results["max_time"] = max(results["timings"])
    results["std_dev_time"] = statistics.stdev(results["timings"]) if len(results["timings"]) > 1 else 0
    
    results["avg_legislation"] = statistics.mean(results["legislation_count"])
    results["avg_cases"] = statistics.mean(results["cases_count"])
    results["avg_forms"] = statistics.mean(results["forms_count"])
    
    logger.info(f"Benchmark completed for {model}. Average time: {results['avg_time']:.2f}s")
    return results

def generate_report(benchmark_results: List[Dict[str, Any]], output_file: str = None):
    """
    Generate a report from benchmark results.
    
    Args:
        benchmark_results: List of benchmark results for each model
        output_file: Optional file to save the report to
    """
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "models_compared": [r["model"] for r in benchmark_results],
        "total_questions": benchmark_results[0]["questions"],
        "runs_per_question": benchmark_results[0]["runs"],
        "results": []
    }
    
    # Create comparison table
    for result in benchmark_results:
        model_report = {
            "model": result["model"],
            "avg_time": result["avg_time"],
            "median_time": result["median_time"],
            "min_time": result["min_time"],
            "max_time": result["max_time"],
            "std_dev_time": result["std_dev_time"],
            "avg_legislation": result["avg_legislation"],
            "avg_cases": result["avg_cases"],
            "avg_forms": result["avg_forms"]
        }
        report["results"].append(model_report)
    
    # Print report
    print("\n=== InsolvencyBot Performance Benchmark Report ===")
    print(f"Date: {report['timestamp']}")
    print(f"Questions: {report['total_questions']}")
    print(f"Runs per question: {report['runs_per_question']}")
    print("\nPerformance by Model:")
    
    df = pd.DataFrame(report["results"])
    print(df.to_string(index=False))
    
    # Save report to file if specified
    if output_file:
        try:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\nReport saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving report: {e}")
            print(f"Error saving report: {e}")
    
    return report

def main():
    """Main entry point for the benchmark script."""
    parser = argparse.ArgumentParser(description='Benchmark InsolvencyBot performance')
    parser.add_argument('--models', nargs='+', default=DEFAULT_MODELS,
                        help='Models to benchmark (default: gpt-3.5-turbo gpt-4 gpt-4o)')
    parser.add_argument('--dataset', choices=['train', 'test'], default='test',
                        help='Dataset to use for benchmarking (default: test)')
    parser.add_argument('--questions', type=int, default=3,
                        help='Number of questions to benchmark (default: 3)')
    parser.add_argument('--runs', type=int, default=1,
                        help='Number of runs per question (default: 1)')
    parser.add_argument('--parallel', action='store_true',
                        help='Run questions in parallel (default: False)')
    parser.add_argument('--output', type=str, default='benchmark_results.json',
                        help='Output file for benchmark results (default: benchmark_results.json)')
    
    args = parser.parse_args()
    
    # Check for API key
    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set.")
        return 1
    
    # Load questions
    input_file = f"data/{args.dataset}_questions.csv"
    if not os.path.exists(input_file):
        print(f"Error: Input file not found: {input_file}")
        return 1
    
    df = pd.read_csv(input_file, sep="\t", encoding="utf-8")
    questions = df['question_text'].tolist()[:args.questions]
    
    print(f"Benchmarking {len(questions)} questions from {args.dataset} dataset")
    print(f"Models to benchmark: {', '.join(args.models)}")
    print(f"Runs per question: {args.runs}")
    print(f"Parallel execution: {args.parallel}")
    
    benchmark_results = []
    
    for model in args.models:
        try:
            result = run_benchmark_for_model(
                model=model, 
                questions=questions, 
                parallel=args.parallel, 
                runs=args.runs
            )
            benchmark_results.append(result)
        except Exception as e:
            logger.error(f"Error benchmarking model {model}: {e}", exc_info=True)
            print(f"Error benchmarking model {model}: {e}")
    
    # Generate report
    generate_report(benchmark_results, args.output)
    return 0

if __name__ == "__main__":
    sys.exit(main())
