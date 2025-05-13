#!/bin/bash

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

  echo -e "\n🔹 Top 5 by $key:"

  # Zisti, či je to objekt alebo pole
  jq_type=$(jq -r 'if type=="array" then "array" else "object" end' results.json)

  if [ "$jq_type" == "array" ]; then
    # Pre pole
    jq -r --arg key "$key" --arg o1 "$other1" --arg o2 "$other2" '
      .[] |
      select(.result_data and .result_data.statistics) |
      [.result_data.statistics[$key], .result_data.statistics[$o1], .result_data.statistics[$o2],
       "threshold=" + (.request_data.threshold|tostring),
       "conf=" + (.request_data.confidence_threshold|tostring),
       "topk=" + (.request_data.top_k|tostring)] | @tsv
    ' results.json | sort -grk1 | head -n 5 | while IFS=$'\t' read v1 v2 v3 t c k; do
      echo "$key: $v1 | $other1: $v2 | $other2: $v3 | $t, $c, $k"
    done
  else
    # Pre jeden objekt
    jq -r --arg key "$key" --arg o1 "$other1" --arg o2 "$other2" '
      [ .result_data.statistics[$key], .result_data.statistics[$o1], .result_data.statistics[$o2],
        "threshold=" + (.request_data.threshold|tostring),
        "conf=" + (.request_data.confidence_threshold|tostring),
        "topk=" + (.request_data.top_k|tostring) ] | @tsv
    ' results.json | while IFS=$'\t' read v1 v2 v3 t c k; do
      echo "$key: $v1 | $other1: $v2 | $other2: $v3 | $t, $c, $k"
    done
  fi
}

extract_top5_from_results "precision"
extract_top5_from_results "recall"
extract_top5_from_results "f1_score"