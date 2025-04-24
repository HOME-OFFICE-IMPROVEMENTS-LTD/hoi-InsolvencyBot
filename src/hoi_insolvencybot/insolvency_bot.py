import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def answer_question(question_text: str, verbose: bool = False, model: str = "gpt-3.5-turbo"):
    prompt = f"""
You are an expert insolvency law assistant. Given this legal scenario, provide your advice in plain English. Include references to UK statutes, legal cases, and any official forms if applicable.

Question: {question_text}
"""

    if verbose:
        print(f"[Prompt to {model}]: {prompt.strip()}")

    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are an expert in UK insolvency law."},
            {"role": "user", "content": prompt.strip()}
        ],
        temperature=0.7,
        max_tokens=1200
    )

    answer = response['choices'][0]['message']['content']

    # Simulated extraction (improve later if needed)
    return {
        "_response": answer,
        "legislation": ["Insolvency Act 1986"],
        "cases": ["Salomon v A Salomon & Co Ltd"],
        "forms": ["Form 4.19 (Scot)"]
    }
