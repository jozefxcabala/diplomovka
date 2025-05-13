#!/bin/bash

output_file="best_param_payloads.json"
> "$output_file"  # vyčisti súbor

# Fixné hodnoty
threshold=23
confidence_threshold=0.45
top_k=3
batch=32  # 🔒 pevne daný batch size
categories='["a person wearing a helmet and an orange vest is walking","a person wearing a helmet and an orange vest is dancing","a person wearing a helmet and an orange vest is standing in place","a person wearing a helmet and an orange vest is jumping","a person wearing a helmet and an orange vest is running","a person wearing a helmet and an orange vest is fighting","a person wearing a helmet and an orange vest have something in hand","a person wearing a helmet and an orange vest is lying in the ground","a person wearing a helmet and an orange vest is limping","a person wearing a helmet and an orange vest fell to the ground","a person wearing a helmet and an orange vest is sitting","a person wearing a helmet and an orange vest is riding motocycle"]'

# Pre skip_frames=true
for num_skip in 3 5; do
  for frame_rate in 1 2 3 4 5 6 7 8 9 10 12 14 16 18 20; do
    jq -n \
    --argjson skip_frames true \
    --argjson num_of_skip_frames "$num_skip" \
    --argjson threshold "$threshold" \
    --argjson confidence_threshold "$confidence_threshold" \
    --argjson top_k "$top_k" \
    --argjson batch_size "$batch" \
    --argjson frame_sample_rate "$frame_rate" \
    --argjson categories "$categories" \
    '{
      request_data: {
        skip_frames: $skip_frames,
        num_of_skip_frames: $num_of_skip_frames,
        dataset_path: "experiments/UBnormal",
        model_path: "data/models/yolo11n.pt",
        num_segments: 8,
        categories: $categories,
        threshold: $threshold,
        confidence_threshold: $confidence_threshold,
        top_k: $top_k,
        batch_size: $batch_size,
        frame_sample_rate: $frame_sample_rate,
        processing_mode: "sequential"
      }
    }' >> "$output_file"
    echo "," >> "$output_file"
  done
done

# Pre skip_frames=false
for frame_rate in 2 4 8; do
  jq -n \
  --argjson skip_frames false \
  --argjson num_of_skip_frames 0 \
  --argjson threshold "$threshold" \
  --argjson confidence_threshold "$confidence_threshold" \
  --argjson top_k "$top_k" \
  --argjson batch_size "$batch" \
  --argjson frame_sample_rate "$frame_rate" \
  --argjson categories "$categories" \
  '{
    request_data: {
      skip_frames: $skip_frames,
      num_of_skip_frames: $num_of_skip_frames,
      dataset_path: "experiments/UBnormal",
      model_path: "data/models/yolo11n.pt",
      num_segments: 8,
      categories: $categories,
      threshold: $threshold,
      confidence_threshold: $confidence_threshold,
      top_k: $top_k,
      batch_size: $batch_size,
      frame_sample_rate: $frame_sample_rate,
      processing_mode: "sequential"
    }
  }' >> "$output_file"
  echo "," >> "$output_file"
done

# Odstráni poslednú čiarku a zabalí to do poľa
sed -i '' '$ d' "$output_file"  # macOS: odstráň posledný riadok (čiarka)
sed -i '' '1s/^/[/' "$output_file" # pridaj [ na začiatok
echo "]" >> "$output_file"         # a ] na koniec

echo "✅ Generated $(grep -c "request_data" "$output_file") payloads into $output_file"