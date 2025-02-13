'''
Run all train or test questions through GPT-3-5 Turbo or GPT-4

Usage: python generate_responses_gpt.py gpt-3.5-turbo|gpt-4 train|test

You need to set environment variable AZUREAI_ENDPOINT_KEY first.
'''

import os
import re
import sys
import time
import traceback

import pandas as pd
import requests

from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential


SUPPORTED_MODELS = {'DeepSeek-R1', 'Mistral-Large-2411'}
SUPPORTED_MODELS_CONCAT = '|'.join(SUPPORTED_MODELS)
COMMAND_LINE_PARAM = f"Usage: python generate_responses_deepseek_via_azure.py {SUPPORTED_MODELS_CONCAT} train|test"

if len(sys.argv) != 3:
    print(COMMAND_LINE_PARAM)
    exit()

if os.environ.get("AZUREAI_ENDPOINT_KEY") == "" or os.environ.get("AZUREAI_ENDPOINT_KEY") is None:
    print("Please set environment variable AZUREAI_ENDPOINT_KEY first.")
    exit()
    

    
MODEL = sys.argv[1]
if MODEL not in SUPPORTED_MODELS:
    print(COMMAND_LINE_PARAM)
    print("Please set model to one of ", " or ".join(SUPPORTED_MODELS))
    exit()
TRAIN_TEST = sys.argv[2]

print(f"Dataset: {TRAIN_TEST}")

df = pd.read_csv(f"{TRAIN_TEST}_questions.csv", encoding="utf-8", sep="\t")


endpoint = "https://ai-thomas3695ai924177264380.services.ai.azure.com/models"
model_name = "DeepSeek-R1"
client = ChatCompletionsClient(endpoint=endpoint, credential=AzureKeyCredential(os.environ["AZUREAI_ENDPOINT_KEY"]), timeout=60*5)

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
        print("attempt calling Azure AI Foundry API:", attempt)
        try:
            response = client.complete(
		  messages=[
		    UserMessage(content=q)
		  ],
		  model = model_name,
		  max_tokens=2000
		)
            r = response.choices[0].message.content
            break
        except:
            print("Try again")
            traceback.print_exc()
            time.sleep(10)
    bot_responses[idx] = re.sub(r'\s+', ' ', r)

    endtime = time.time()
    bot_times[idx] = endtime - starttime
    bot_attempts[idx] = attempt + 1

    print("\tReceived response: ", r)

df["bot_response"] = bot_responses
df["bot_response_time"] = bot_times
df["bot_response_attempts"] = bot_attempts

df.to_csv(f"output_{TRAIN_TEST}_{MODEL}.csv", sep="\t", encoding="utf-8", index=False)
