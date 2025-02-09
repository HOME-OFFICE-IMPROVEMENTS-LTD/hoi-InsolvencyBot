'''
Run all train or test questions through GPT-3-5 Turbo or GPT-4

Usage: python generate_responses_gpt.py gpt-3.5-turbo|gpt-4 train|test

You need to set environment variable OPENAI_API_KEY first.
'''

import os
import re
import sys
import time
import traceback

import pandas as pd
import requests

from openai import OpenAI

SUPPORTED_MODELS = {'llama3.1-70b'}
SUPPORTED_MODELS_CONCAT = '|'.join(SUPPORTED_MODELS)
COMMAND_LINE_PARAM = f"Usage: python generate_responses_llama.py {SUPPORTED_MODELS_CONCAT} train|test"

if len(sys.argv) != 3:
    print(COMMAND_LINE_PARAM)
    exit()

if os.environ.get("LLAMA_API_TOKEN") == "" or os.environ.get("LLAMA_API_TOKEN") is None:
    print("Please set environment variable LLAMA_API_TOKEN first.")
    exit()

client = OpenAI(
api_key = os.environ.get("LLAMA_API_TOKEN"),
base_url = "https://api.llama-api.com",
timeout = 60 * 4
)
    
MODEL = sys.argv[1]
if MODEL not in SUPPORTED_MODELS:
    print(COMMAND_LINE_PARAM)
    print("Please set model to one of ", " or ".join(SUPPORTED_MODELS))
    exit()
TRAIN_TEST = sys.argv[2]

print(f"Dataset: {TRAIN_TEST}")

df = pd.read_csv(f"{TRAIN_TEST}_questions.csv", encoding="utf-8", sep="\t")

headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + os.environ["OPENAI_API_KEY"],
}

bot_responses = [""] * len(df)
bot_times = [0] * len(df)
bot_attempts = [0] * len(df)
for idx in range(len(df)):
    q = df.question_text.iloc[idx]
    q_no = df.question_no.iloc[idx]
    print(f"Asking question: {q_no}: {q}")

    starttime = time.time()

    json_data = {
        'model': MODEL,
        'messages': [
            {"role": "user", "content": q},
        ],
    }
    for attempt in range(3):
        print("attempt calling Llama API:", attempt)
        try:
            
            response = client.chat.completions.create(
                model="llama3.1-70b",
                messages=[
                    {"role": "user", "content": q},
                ]
            )
            r = response.choices[0].message.content
            break
        except:
            print("Try again")
            traceback.print_exc()
            time.sleep(60)
    bot_responses[idx] = re.sub(r'\s+', ' ', r)

    endtime = time.time()
    bot_times[idx] = endtime - starttime
    bot_attempts[idx] = attempt + 1

    print("\tReceived response: ", r)

df["bot_response"] = bot_responses
df["bot_response_time"] = bot_times
df["bot_response_attempts"] = bot_attempts

df.to_csv(f"output_{TRAIN_TEST}_{MODEL}.csv", sep="\t", encoding="utf-8", index=False)
