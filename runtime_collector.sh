#!/bin/bash

# Set the prefix to search for
prefix="wrfrst_d01"

# Loop through the directories 00 to 31
for dir in {00..31}; do
  # Check if the directory exists
  if [ -d "$dir" ]; then
    # Use find to search for files with the specified prefix
    find "$dir" -name "${prefix}*" -type f -printf "%T@ %Tc %p\n" | sort -n
  fi
done | cut -d ' ' -f 1-  > runtime_output.txt

