#!/bin/bash

# This script processes an evaluation results JSON file and extracts the top 5 performing configurations for each metric (precision, recall, and F1-score).
#
# Functionality:
# - Defines a helper function to extract and sort metrics per scene.
# - Uses `jq` to filter valid numeric results for each metric across scenes.
# - Displays the top 5 entries per metric with corresponding thresholds, confidence, top_k, and scene name.
#
# Intended for quickly identifying the best experimental runs across multiple metrics.

echo "🔍 Searching for top 5 by precision, recall and f1_score..."

extract_top5_from_results() {
  local key=$1
  local other1 other2

  if [ "$key" == "precision" ]; then
    other1="recall"; other2="f1_score"
  elif [ "$key" == "recall" ]; then
    other1="precision"; other2="f1_score"
  else
    other1="precision"; other2="recall"
  fi

  echo -e "\n🔹 Top 5 by $key (across scenes):"

  # Extract and format relevant metrics and parameters from JSON
  jq -r --arg key "$key" --arg o1 "$other1" --arg o2 "$other2" '
    .[] |
    .request_data as $r |
    .result_data | to_entries[] |
    .key as $scene |
    .value |
    select((.[$key] | type == "number") and (.[$o1] | type == "number") and (.[$o2] | type == "number")) |
    [ .[$key], .[$o1], .[$o2],
      "scene=" + $scene,
      "threshold=" + ($r.threshold|tostring),
      "conf=" + ($r.confidence_threshold|tostring),
      "topk=" + ($r.top_k|tostring)
    ] | @tsv
  ' results.json | 
  # Sort by the primary metric in descending order and take top 5
  sort -grk1 | head -n 5 | while IFS=$'\t' read v1 v2 v3 s t c k; do
    # Print results in a readable format
    printf "%s: %.4f | %s: %.4f | %s: %.4f | %s, %s, %s, %s\n" "$key" "$v1" "$other1" "$v2" "$other2" "$v3" "$s" "$t" "$c" "$k"
  done
}

extract_top5_from_results "precision"
extract_top5_from_results "recall"
extract_top5_from_results "f1_score"