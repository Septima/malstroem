#!/bin/bash

if [ $# -lt 2 ]; then
    echo "Usage: $0 input_dir base_out_dir"
    exit 1
fi

objectid="009.11"
# Directory containing the .tif files
input_dir=$1
# Base directory for output
base_out_dir=$2

# Loop over each .tif file in the input directory
for file in "$input_dir"/*.tif; do
  # Extract the filename without the path and extension
  filename=$(basename "$file" .tif)
  
  # Create a specific output directory for this file
  out_dir="$base_out_dir/$filename"
  
  # Make the output directory if it doesn't already exist
  mkdir -p "$out_dir"
  
  # Run the malstroem command with the current file and its specific output directory
  malstroem complete -mm 20 -filter 'volume > 2.5' -dem "$file" -outdir "$out_dir" -zresolution 0.1
done
