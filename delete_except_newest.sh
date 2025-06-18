#!/bin/bash

# Directory to clean (default to current directory if not provided)
# DIR=${1:-.}
USERNAME=$(whoami)

echo "Running script as user: $USERNAME"

# DIR="/mnt/c/Users/$USERNAME/Downloads/to_delete_test/"
DIR="/home/$USERNAME/Desktop/scout-videos/"

# Ensure the directory exists
if [ ! -d "$DIR" ]; then
  echo "Error: Directory $DIR does not exist."
  exit 1
fi

# Ensure we only delete files and folders inside the specified folder, not the folder itself
if [ "$DIR" == "." ]; then
  echo "Please specify a directory explicitly to avoid accidental deletions."
  exit 1
fi

# Find the newest modification day among the files inside the folder
NEWEST_DAY=$(find "$DIR" -mindepth 1 -maxdepth 1 -type f -printf '%TY-%Tm-%Td %p\n' | sort -n | tail -1 | awk '{print $1}')

if [ -z "$NEWEST_DAY" ]; then
  echo "No files found in $DIR. Deleting all subfolders."
  find "$DIR" -mindepth 1 -maxdepth 1 -type d -exec rm -rf {} +
  echo "All subfolders deleted."
  exit 0
fi

# Iterate through all files inside the folder and delete those not matching the newest day
find "$DIR" -mindepth 1 -maxdepth 1 -type f -printf '%TY-%Tm-%Td %p\n' | while read -r line; do
  FILE_DAY=$(echo "$line" | awk '{print $1}')
  FILE_NAME=$(echo "$line" | awk '{print substr($0, index($0, $2))}')

  if [ "$FILE_DAY" != "$NEWEST_DAY" ]; then
    echo "Deleting $FILE_NAME"
    rm "$FILE_NAME"
  fi

done

# Delete all subfolders in the directory
find "$DIR" -mindepth 1 -maxdepth 1 -type d -exec rm -rf {} +

echo "Cleanup complete. Files with the newest day are preserved and all subfolders are deleted."

