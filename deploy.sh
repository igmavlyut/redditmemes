#!/bin/bash

# Script for deploying function to Yandex Cloud Functions
# Usage: ./deploy.sh

FOLDER_ID="b1gduh7hn89hjb3h22sh"
FUNCTION_NAME="reddit-parse"
FUNCTION_ID="d4erqui9vsdqvh4g78ih"

echo "Preparing to deploy function $FUNCTION_NAME..."

# Create ZIP archive
echo "Creating ZIP archive..."
zip -r function.zip index.py requirements.txt

if [ $? -ne 0 ]; then
    echo "✗ Error creating ZIP archive"
    exit 1
fi

echo "✓ ZIP archive created"

# Deploy function
echo "Deploying function..."
yc serverless function version create \
  --function-name $FUNCTION_NAME \
  --folder-id $FOLDER_ID \
  --runtime python312 \
  --entrypoint index.handler \
  --memory 128m \
  --execution-timeout 10s \
  --source-path function.zip

if [ $? -eq 0 ]; then
    echo "✓ Function successfully deployed!"
    echo ""
    echo "Don't forget to set environment variables:"
    echo "  ./set_env.sh YOUR_CLIENT_ID YOUR_CLIENT_SECRET YOUR_USERNAME"
else
    echo "✗ Error deploying function"
    rm -f function.zip
    exit 1
fi

# Remove temporary file
rm -f function.zip
echo "✓ Temporary files removed"
