#!/usr/bin/env python3
"""
Interactive CLI for InsolvencyBot.

This script provides a command-line interface for users to interact
with InsolvencyBot, ask questions, and get responses in real-time.
"""

import os
import sys
import argparse
import textwrap
from typing import Dict, List, Any
import colorama
from colorama import Fore, Style, Back

from src.hoi_insolvencybot.insolvency_bot import answer_question
from src.hoi_insolvencybot.logging_config import setup_logging, get_logger

# Set up logging
setup_logging()
logger = get_logger(__name__)

# Initialize colorama
colorama.init()

# Default model to use
DEFAULT_MODEL = "gpt-3.5-turbo"

def print_header():
    """Print the InsolvencyBot CLI header."""
    header = """
╔══════════════════════════════════════════════════════════════════╗
║                      InsolvencyBot CLI                           ║
║                                                                  ║
║  Ask questions about UK insolvency law and get expert responses  ║
╚══════════════════════════════════════════════════════════════════╝
    """
    print(Fore.CYAN + header + Style.RESET_ALL)
    print(f"Using model: {Fore.GREEN}{DEFAULT_MODEL}{Style.RESET_ALL}")
    print("Type 'quit', 'exit', or press Ctrl+C to exit.")
    print("Type 'model <name>' to change the model (e.g., 'model gpt-4').")
    print("Type 'help' to see these instructions again.")
    print()

def print_response(response: Dict[str, Any]):
    """
    Print a formatted response from InsolvencyBot.
    
    Args:
        response: The response from answer_question
    """
    # Print the main response with clean formatting
    print(Fore.WHITE + Style.BRIGHT + "\n=== Response ===\n" + Style.RESET_ALL)
    
    # Format and print the main response with proper line wrapping
    formatted_text = textwrap.fill(
        response["_response"], 
        width=80, 
        initial_indent="  ", 
        subsequent_indent="  "
    )
    print(formatted_text + "\n")
    
    # Print cited legislation
    print(Fore.YELLOW + Style.BRIGHT + "Legislation Cited:" + Style.RESET_ALL)
    if response["legislation"]:
        for legislation in response["legislation"]:
            print(f"  • {legislation}")
    else:
        print("  None cited")
    
    # Print cited cases
    print(Fore.YELLOW + Style.BRIGHT + "\nCase Law Cited:" + Style.RESET_ALL)
    if response["cases"]:
        for case in response["cases"]:
            print(f"  • {case}")
    else:
        print("  None cited")
    
    # Print relevant forms
    print(Fore.YELLOW + Style.BRIGHT + "\nRelevant Forms:" + Style.RESET_ALL)
    if response["forms"]:
        for form in response["forms"]:
            print(f"  • {form}")
    else:
        print("  None cited")
    
    print("\n" + "─" * 80 + "\n")

def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description='Interactive CLI for InsolvencyBot')
    parser.add_argument('--model', type=str, default=DEFAULT_MODEL,
                        help='Model to use (default: gpt-3.5-turbo)')
    
    args = parser.parse_args()
    
    # Check for API key
    if not os.environ.get("OPENAI_API_KEY"):
        print(f"{Fore.RED}Error: OPENAI_API_KEY environment variable not set.{Style.RESET_ALL}")
        return 1
    
    global DEFAULT_MODEL
    DEFAULT_MODEL = args.model
    
    print_header()
    
    # Interactive loop
    try:
        while True:
            try:
                # Get input from user
                question = input(f"{Fore.GREEN}> {Style.RESET_ALL}")
                
                # Check for special commands
                if question.lower() in ('quit', 'exit'):
                    print(f"{Fore.CYAN}Thank you for using InsolvencyBot CLI!{Style.RESET_ALL}")
                    break
                
                elif question.lower() == 'help':
                    print_header()
                    continue
                
                elif question.lower().startswith('model '):
                    model_name = question.split(' ', 1)[1].strip()
                    # Validate model name
                    if model_name in ('gpt-3.5-turbo', 'gpt-4', 'gpt-4o'):
                        DEFAULT_MODEL = model_name
                        print(f"Model changed to: {Fore.GREEN}{DEFAULT_MODEL}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}Invalid model name. Use gpt-3.5-turbo, gpt-4, or gpt-4o.{Style.RESET_ALL}")
                    continue
                
                elif not question.strip():
                    continue
                
                # Get response
                print(f"{Fore.CYAN}Thinking...{Style.RESET_ALL}")
                logger.info(f"Processing question: {question}")
                
                response = answer_question(question, verbose=False, model=DEFAULT_MODEL)
                print_response(response)
                
            except KeyboardInterrupt:
                print(f"\n{Fore.CYAN}Thank you for using InsolvencyBot CLI!{Style.RESET_ALL}")
                break
                
            except Exception as e:
                logger.error(f"Error processing question: {e}", exc_info=True)
                print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
    
    except KeyboardInterrupt:
        print(f"\n{Fore.CYAN}Thank you for using InsolvencyBot CLI!{Style.RESET_ALL}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
