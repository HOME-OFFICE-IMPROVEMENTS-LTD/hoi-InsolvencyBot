"""
InsolvencyBot Module - Core implementation of the Insolvency Bot using LLMs.

This module provides the functionality to:
1. Process insolvency-related legal queries
2. Generate legally accurate responses using LLMs (GPT-3.5, GPT-4, or GPT-4o)
3. Extract cited legislation, case law, and forms
4. Structure responses in a standardized JSON format

The main entry point is the `answer_question` function.

Example usage:
    >>> from src.hoi_insolvencybot.insolvency_bot import answer_question
    >>> question = "What happens if my company can't pay its debts?"
    >>> response = answer_question(question, model="gpt-4")
    >>> print(response["_response"])
    >>> print("Legislation cited:", response["legislation"])
    >>> print("Cases cited:", response["cases"])
    >>> print("Relevant forms:", response["forms"])

Design:
    The InsolvencyBot utilizes Large Language Models (LLMs) to generate responses to
    insolvency-related legal queries. It structures prompts to elicit legally sound
    advice including relevant UK legislation, case law references, and applicable forms.
    
    The system extracts these references to provide structured data that can be used
    for verification, citation tracking, and further analysis.

Dependencies:
    - OpenAI API (requires an API key set via OPENAI_API_KEY environment variable)
    - Python 3.7+
"""

import json
import os
import time
from typing import Dict, List, Any, Union, Optional

import openai

from src.hoi_insolvencybot.logging_config import get_logger

# Initialize logger
logger = get_logger(__name__)

# Initialize OpenAI API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")
# Log the API key information for debugging (not the key itself)
if openai.api_key:
    logger.info("OPENAI_API_KEY environment variable is set")
else:
    logger.warning("OPENAI_API_KEY environment variable is not set")

def answer_question(
    question_text: str, 
    verbose: bool = False, 
    model: str = "gpt-3.5-turbo",
    max_retries: int = 3
) -> Dict[str, Union[str, List[str]]]:
    """
    Process an insolvency-related legal question and return a structured response.
    
    This function sends the question to an OpenAI LLM, processes the response,
    and extracts relevant legal references including legislation, cases, and forms.
    
    Args:
        question_text: The legal question to be answered
        verbose: If True, print additional debug information
        model: The OpenAI model to use (gpt-3.5-turbo, gpt-4, or gpt-4o)
        max_retries: Maximum number of API call retries on failure
        
    Returns:
        A dictionary containing the response and extracted references:
        {
            "_response": str,          # The main response text
            "legislation": List[str],  # List of cited legislation 
            "cases": List[str],        # List of cited legal cases
            "forms": List[str]         # List of relevant forms
        }
        
    Raises:
        ValueError: If the provided model is not supported
        RuntimeError: If all API call attempts fail after max_retries
    """
    # Validate inputs
    supported_models = ["gpt-3.5-turbo", "gpt-4", "gpt-4o"]
    if model not in supported_models:
        raise ValueError(f"Model {model} not supported. Use one of: {', '.join(supported_models)}")
    
    if not question_text or not question_text.strip():
        raise ValueError("Question text cannot be empty")
    
    # Construct the prompt
    prompt = f"""
You are an expert insolvency law assistant. Given this legal scenario, provide your advice in plain English. Include references to UK statutes, legal cases, and any official forms if applicable.

Question: {question_text}
"""

    if verbose:
        print(f"[Prompt to {model}]: {prompt.strip()}")
        
    # Check if API key is available
    if not openai.api_key:
        raise EnvironmentError("OPENAI_API_KEY environment variable is not set")

    # Send the question to the OpenAI API with retry logic
    answer = None
    last_error = None
    
    for attempt in range(max_retries):
        try:
            logger.info(f"API call attempt {attempt + 1}/{max_retries} using model {model}")
            if verbose:
                print(f"API call attempt {attempt + 1}/{max_retries}")
                
            start_time = time.time()
            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an expert in UK insolvency law."},
                    {"role": "user", "content": prompt.strip()}
                ],
                temperature=0.7,
                max_tokens=1200
            )
            elapsed_time = time.time() - start_time
            
            logger.info(f"API call successful. Response time: {elapsed_time:.2f}s")
            answer = response['choices'][0]['message']['content']
            break  # Success, exit retry loop
            
        except (openai.error.RateLimitError, openai.error.APIError, 
                openai.error.ServiceUnavailableError, openai.error.APIConnectionError) as e:
            # These are retryable errors
            last_error = e
            logger.warning(f"Retryable error on attempt {attempt + 1}: {e}")
            if verbose:
                print(f"Retryable error: {e}. Retrying in {2 ** attempt} seconds...")
                
            # Exponential backoff
            backoff = 2 ** attempt
            logger.info(f"Backing off for {backoff} seconds before retry")
            time.sleep(backoff)
            
        except Exception as e:
            # Non-retryable error
            logger.error(f"Non-retryable error calling OpenAI API: {str(e)}", exc_info=True)
            raise RuntimeError(f"Error calling OpenAI API: {str(e)}")
    
    # If all retries failed
    if answer is None:
        logger.error(f"Failed to get response after {max_retries} attempts. Last error: {last_error}")
        raise RuntimeError(f"Failed to get response after {max_retries} attempts. Last error: {last_error}")
    
    # Extract references from the response
    logger.debug("Extracting references from response")
    extracted = extract_references(answer)
    
    # Create the structured response
    result = {
        "_response": answer,
        "legislation": extracted["legislation"],
        "cases": extracted["cases"],
        "forms": extracted["forms"]
    }
    
    logger.info(f"Question processed successfully. Found {len(extracted['legislation'])} legislation references, "
                f"{len(extracted['cases'])} case references, and {len(extracted['forms'])} form references")
    
    if verbose:
        print(f"Extracted legislation: {extracted['legislation']}")
        print(f"Extracted cases: {extracted['cases']}")
        print(f"Extracted forms: {extracted['forms']}")
    
    logger.debug(f"Extracted legislation: {extracted['legislation']}")
    logger.debug(f"Extracted cases: {extracted['cases']}")
    logger.debug(f"Extracted forms: {extracted['forms']}")
        
    return result

def extract_references(text: str) -> Dict[str, List[str]]:
    """
    Extract legislation, case law, and form references from the given text.
    
    Uses a combination of pattern matching and heuristics to identify typical
    reference patterns in UK legal advice.
    
    Args:
        text: The text to extract references from
        
    Returns:
        Dictionary containing lists of extracted references:
        {
            "legislation": List of legislation references
            "cases": List of case law references
            "forms": List of form references
        }
    """
    import re
    
    # Initialize result
    result = {
        "legislation": [],
        "cases": [],
        "forms": []
    }
    
    # Common UK legislation patterns
    legislation_patterns = [
        r"(?:the )?(?:UK )?(?:Insolvency Act(?: \d{4})?)",
        r"(?:the )?(?:UK )?(?:Companies Act(?: \d{4})?)",
        r"(?:the )?(?:UK )?(?:Enterprise Act(?: \d{4})?)",
        r"(?:the )?(?:UK )?(?:Bankruptcy(?:\sand\sInsolvency)? Act(?: \d{4})?)",
        r"(?:the )?(?:UK )?(?:Company Directors Disqualification Act(?: \d{4})?)",
        r"(?:Section|s\.?|Sec\.?) \d+[A-Za-z]* of the [A-Za-z\s]+ Act(?: \d{4})?"
    ]
    
    # Case law patterns (simplified)
    case_patterns = [
        r"[A-Z][a-z]+(?:\s+[A-Z][a-z]+)* v\.? [A-Z][a-z]+(?:\s+[A-Z][a-z]+)*",
        r"Re \w+(?:\s+\w+)*(?:\s+\[\d{4}\])?(?:\s+[A-Z]+\s+\d+)?",
        r"R \((?:on the application of )?\w+(?:\s+\w+)*\) v\.? \w+(?:\s+\w+)*"
    ]
    
    # Form patterns
    form_patterns = [
        r"Form\s+[0-9.]+(?: \([A-Za-z]+\))?",
        r"(?:Official )?Receiver Form [0-9.]+",
        r"(?:Notice|Statement) of [A-Za-z\s]+"
    ]
    
    # Extract legislation
    for pattern in legislation_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            legislation = match.group(0).strip()
            # Standardize the legislation name
            if "insolvency act" in legislation.lower() and "1986" not in legislation:
                legislation += " 1986"
            if "companies act" in legislation.lower() and "2006" not in legislation:
                legislation += " 2006"
            
            if legislation not in result["legislation"]:
                result["legislation"].append(legislation)
    
    # Extract cases
    for pattern in case_patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            case = match.group(0).strip()
            if case not in result["cases"]:
                result["cases"].append(case)
    
    # Extract forms
    for pattern in form_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            form = match.group(0).strip()
            if form not in result["forms"]:
                result["forms"].append(form)
    
    # If we didn't find any cases but there are likely mentions, try another approach
    if not result["cases"] and ("[" in text and "]" in text):
        # Look for case citations in the format [YYYY] COURT NUMBER
        case_citations = re.finditer(r'\[\d{4}\]\s+[A-Z]+\s+\d+', text)
        for match in case_citations:
            citation = match.group(0).strip()
            # Try to find the case name before this citation
            context = text[:match.start()].strip().split(".")[-1].strip()
            if context and len(context) < 100:  # Reasonable length for case name
                result["cases"].append(f"{context} {citation}")
            else:
                result["cases"].append(citation)
    
    return result
