#!/usr/bin/env python3
"""
Test report generator for InsolvencyBot.

This script runs the tests and generates a simple HTML and text report of the results.
"""

import os
import unittest
import datetime
import time
import sys
from unittest.runner import TextTestRunner
from unittest.loader import defaultTestLoader
from unittest.result import TestResult
from io import StringIO

def generate_test_report():
    """Run the tests and generate a report."""
    # Start time
    start_time = time.time()
    
    # Set up test suite
    loader = defaultTestLoader
    suite = loader.discover('tests')
    
    # Run tests
    result_file = StringIO()
    runner = TextTestRunner(stream=result_file, verbosity=2)
    result = runner.run(suite)
    
    # End time
    end_time = time.time()
    duration = end_time - start_time
    
    # Create report
    report = f"""
InsolvencyBot Test Report
=========================
Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Duration: {duration:.2f} seconds

Summary:
- Tests run: {result.testsRun}
- Errors: {len(result.errors)}
- Failures: {len(result.failures)}
- Skipped: {len(result.skipped)}

Details:
"""
    
    # Add test result details
    if result.errors:
        report += "\nErrors:\n"
        for test, error in result.errors:
            report += f"- {test}: {error}\n"
    
    if result.failures:
        report += "\nFailures:\n"
        for test, failure in result.failures:
            report += f"- {test}: {failure}\n"
    
    if result.skipped:
        report += "\nSkipped:\n"
        for test, reason in result.skipped:
            report += f"- {test}: {reason}\n"
    
    # Include the full output
    report += "\nFull Output:\n"
    report += result_file.getvalue()
    
    # Write text report
    with open('test_report.txt', 'w') as f:
        f.write(report)
    
    # Generate simple HTML report
    html_report = f"""<!DOCTYPE html>
<html>
<head>
    <title>InsolvencyBot Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1, h2 {{ color: #333; }}
        .summary {{ background-color: #f4f4f4; padding: 15px; border-radius: 5px; }}
        .success {{ color: green; }}
        .error {{ color: red; }}
        .details {{ margin-top: 20px; }}
        pre {{ background-color: #f9f9f9; padding: 10px; overflow: auto; }}
    </style>
</head>
<body>
    <h1>InsolvencyBot Test Report</h1>
    <div class="summary">
        <h2>Summary</h2>
        <p>Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Duration: {duration:.2f} seconds</p>
        <p>Tests run: {result.testsRun}</p>
        <p class="{('error' if len(result.errors) > 0 else 'success')}">Errors: {len(result.errors)}</p>
        <p class="{('error' if len(result.failures) > 0 else 'success')}">Failures: {len(result.failures)}</p>
        <p>Skipped: {len(result.skipped)}</p>
    </div>
    
    <div class="details">
        <h2>Details</h2>
        <pre>{result_file.getvalue()}</pre>
    </div>
</body>
</html>"""
    
    with open('test_report.html', 'w') as f:
        f.write(html_report)
    
    # Print summary
    print(f"Test report generated: {os.path.abspath('test_report.txt')}")
    print(f"HTML report generated: {os.path.abspath('test_report.html')}")
    print(f"Summary: {result.testsRun} tests, {len(result.errors)} errors, {len(result.failures)} failures, {len(result.skipped)} skipped")
    
    # Return success status
    if len(result.errors) > 0 or len(result.failures) > 0:
        return False
    return True

if __name__ == "__main__":
    success = generate_test_report()
    if not success:
        sys.exit(1)
