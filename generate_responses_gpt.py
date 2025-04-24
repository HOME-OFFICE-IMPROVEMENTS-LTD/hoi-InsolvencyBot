"""
Run all train or test questions through GPT-3.5 Turbo, GPT-4, or GPT-4o

Usage:
    python generate_responses_gpt.py gpt-3.5-turbo|gpt-4|gpt-4o train|test

Note:
    You need to set environment variable OPENAI_API_KEY first.
    It's recommended to store it in a `.env` file if running locally.
"""

import os
import re
import sys
import time
import traceback
import pandas as pd
import requests
from dotenv import load_dotenv

# ✅ Load environment variables from .env if present
load_dotenv()

# ✅ Validate command-line arguments
SUPPORTED_MODELS = {'gpt-3.5-turbo', 'gpt-4', 'gpt-4o'}
COMMAND_LINE_USAGE = (
    "Usage: python generate_responses_gpt.py "
    + "|".join(SUPPORTED_MODELS)
    + " train|test"
)

if len(sys.argv) != 3:
    print(COMMAND_LINE_USAGE)
    sys.exit(1)

MODEL = sys.argv[1]
TRAIN_TEST = sys.argv[2]

if MODEL not in SUPPORTED_MODELS:
    print(COMMAND_LINE_USAGE)
    print("❌ Invalid model. Please choose from:", ", ".join(SUPPORTED_MODELS))
    sys.exit(1)

if TRAIN_TEST not in {"train", "test"}:
    print("❌ Invalid dataset. Use either 'train' or 'test'.")
    sys.exit(1)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("❌ Please set environment variable OPENAI_API_KEY.")
    sys.exit(1)

print(f"📂 Dataset: {TRAIN_TEST}")
print(f"🤖 Model: {MODEL}")

# ✅ Read questions file (CSV, comma-separated)
try:
    df = pd.read_csv(f"{TRAIN_TEST}_questions.csv", encoding="utf-8")
except FileNotFoundError:
    print(f"❌ File not found: {TRAIN_TEST}_questions.csv")
    sys.exit(1)

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OPENAI_API_KEY}",
}

bot_responses = [""] * len(df)
bot_times = [0] * len(df)
bot_attempts = [0] * len(df)

for idx in range(len(df)):
    q = df.loc[idx, "question_text"]
    q_no = df.loc[idx, "question_no"]

    print(f"\n🟡 Asking {q_no}: {q}")

    starttime = time.time()
    json_data = {
        "model": MODEL,
        "messages": [{"role": "user", "content": q}],
    }

    for attempt in range(3):
        try:
            print(f"🔄 Attempt {attempt + 1}...")
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=json_data
            )
            r = response.json()["choices"][0]["message"]["content"]
            break
        except Exception:
            print("⚠️ Error occurred, retrying...")
            traceback.print_exc()
            time.sleep(10)
    else:
        r = "❌ Failed to get response after 3 attempts."
        print(r)

    bot_responses[idx] = re.sub(r"\s+", " ", r.strip())
    bot_times[idx] = time.time() - starttime
    bot_attempts[idx] = attempt + 1

    print(f"✅ Response received: {r[:100]}...")

# ✅ Save results
df["bot_response"] = bot_responses
df["bot_response_time"] = bot_times
df["bot_response_attempts"] = bot_attempts

output_file = f"output_{TRAIN_TEST}_{MODEL}.csv"
df.to_csv(output_file, encoding="utf-8", index=False)
print(f"\n✅ All responses saved to: {output_file}")


