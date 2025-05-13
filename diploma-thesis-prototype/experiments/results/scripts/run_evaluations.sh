#!/bin/bash

start_time=$(date '+%H:%M:%S – %d.%m.%Y')
echo "🟢 Started at $start_time"

thresholds=$(seq 16 1 27)
confidences=(0.3 0.45 0.6 0.75)
top_ks=$(seq 1 1 5)

total_runs=0
for threshold in $thresholds; do
  for conf in "${confidences[@]}"; do
    for topk in $top_ks; do
      total_runs=$((total_runs + 1))
    done
  done
done

current_run=0
echo "[" > results.json

for threshold in $thresholds; do
  for conf in "${confidences[@]}"; do
    for topk in $top_ks; do
      current_run=$((current_run + 1))
      echo -ne "⏳ Running $current_run/$total_runs: threshold=$threshold, conf=$conf, top_k=$topk\r"

      # Run Python and capture raw JSON output
      # raw_result=$(python evaluate.py --threshold "$threshold" --confidence_threshold "$conf" --top_k "$topk")
      raw_result=$(python evaluate_per_scenes.py --threshold "$threshold" --confidence_threshold "$conf" --top_k "$topk")

      # Extract only statistics or wrap into desired structure
      echo "  {" >> results.json
      echo "    \"request_data\": {\"threshold\": $threshold, \"confidence_threshold\": $conf, \"top_k\": $topk}," >> results.json
      echo "    \"result_data\": $raw_result" >> results.json

      # Add comma unless it's the last item
      if [ $current_run -lt $total_runs ]; then
        echo "  }," >> results.json
      else
        echo "  }" >> results.json
      fi
    done
  done
done

echo "]" >> results.json

end_time=$(date '+%H:%M:%S – %d.%m.%Y')
echo ""
echo "✅ Finished at $end_time"