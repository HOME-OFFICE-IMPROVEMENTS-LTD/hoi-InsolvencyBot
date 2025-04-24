'''
Run all train or test questions through Insolvency Bot

Usage: python -m hoi_insolvencybot gpt-3.5-turbo|gpt-4|gpt-4o train|test

Make sure OPENAI_API_KEY is set in your environment.
'''

import os
import re
import sys
import time
import traceback
import pandas as pd
from hoi_insolvencybot.insolvency_bot import answer_question

SUPPORTED_MODELS = {'gpt-3.5-turbo', 'gpt-4', 'gpt-4o'}
SUPPORTED_MODELS_CONCAT = '|'.join(SUPPORTED_MODELS)
COMMAND_LINE_PARAM = f"Usage: python -m hoi_insolvencybot {SUPPORTED_MODELS_CONCAT} train|test"

def main():
    if len(sys.argv) != 3:
        print(COMMAND_LINE_PARAM)
        sys.exit(1)

    if not os.environ.get("OPENAI_API_KEY"):
        print("Please set the environment variable OPENAI_API_KEY.")
        sys.exit(1)

    model = sys.argv[1]
    mode = sys.argv[2]

    if model not in SUPPORTED_MODELS:
        print(COMMAND_LINE_PARAM)
        print("Supported models:", ", ".join(SUPPORTED_MODELS))
        sys.exit(1)

    print(f"Processing dataset: {mode} using model: {model}")

    input_file = f"data/{mode}_questions.csv"
    df = pd.read_csv(input_file, sep="\t", encoding="utf-8")

    bot_responses = [""] * len(df)
    bot_times = [0] * len(df)
    bot_attempts = [0] * len(df)
    bot_statutes = [""] * len(df)
    bot_cases = [""] * len(df)
    bot_forms = [""] * len(df)

    for idx, row in df.iterrows():
        q = row['question_text']
        q_no = row['question_no']
        print(f"Question {q_no}: {q}")

        starttime = time.time()
        for attempt in range(3):
            print("Attempt:", attempt + 1)
            try:
                response_json = answer_question(q, False, model)
                r = response_json["_response"]
                statutes = "|".join(response_json["legislation"])
                cases = "|".join(response_json["cases"])
                forms = "|".join(response_json["forms"])
                break
            except Exception:
                traceback.print_exc()
                time.sleep(10)

        bot_responses[idx] = re.sub(r'\s+', ' ', r)
        bot_times[idx] = time.time() - starttime
        bot_attempts[idx] = attempt + 1
        bot_statutes[idx] = statutes
        bot_cases[idx] = cases
        bot_forms[idx] = forms

        print("\tResponse:", r)

    df["bot_response"] = bot_responses
    df["bot_response_time"] = bot_times
    df["bot_response_attempts"] = bot_attempts
    df["bot_statutes"] = bot_statutes
    df["bot_cases"] = bot_cases
    df["bot_forms"] = bot_forms

    output_file = f"output_{mode}_insolvency_bot_with_{model}.csv"
    df.to_csv(output_file, sep="\t", encoding="utf-8", index=False)
    print(f"Responses saved to {output_file}")

if __name__ == "__main__":
    main()
