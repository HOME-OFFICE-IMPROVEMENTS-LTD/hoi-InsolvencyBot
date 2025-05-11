#!/bin/bash
# Run all models and modes for both GPT and Insolvency Bot scripts
# Usage: bash run_all_models.sh

set -e

MODELS=(gpt-3.5-turbo gpt-4 gpt-4o)
MODES=(train test)

for MODEL in "${MODELS[@]}"; do
  for MODE in "${MODES[@]}"; do
    echo "Running generate_responses_gpt.py $MODEL $MODE"
    python generate_responses_gpt.py "$MODEL" "$MODE"
    echo "Running generate_responses_insolvency_bot.py $MODEL $MODE"
    python generate_responses_insolvency_bot.py "$MODEL" "$MODE"
  done
  echo

done
