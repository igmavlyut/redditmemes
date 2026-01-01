#!/bin/bash

# Script for setting environment variables in Yandex Cloud Function
# Usage: ./set_env.sh YOUR_CLIENT_ID YOUR_CLIENT_SECRET YOUR_USERNAME

FOLDER_ID="b1gduh7hn89hjb3h22sh"
FUNCTION_NAME="reddit-parse"
SUBREDDIT="tarotmemes"

if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ]; then
    echo "Usage: ./set_env.sh CLIENT_ID CLIENT_SECRET REDDIT_USERNAME"
    echo "Example: ./set_env.sh abc123 xyz789 myusername"
    exit 1
fi

CLIENT_ID=$1
CLIENT_SECRET=$2
USERNAME=$3

echo "Setting environment variables for function $FUNCTION_NAME..."

yc serverless function set-environment-variables \
  --name $FUNCTION_NAME \
  --folder-id $FOLDER_ID \
  --environment REDDIT_CLIENT_ID=$CLIENT_ID \
  --environment REDDIT_CLIENT_SECRET=$CLIENT_SECRET \
  --environment REDDIT_USER_AGENT="MemeBot/1.0 by $USERNAME" \
  --environment REDDIT_SUBREDDIT=$SUBREDDIT

if [ $? -eq 0 ]; then
    echo "✓ Environment variables successfully set!"
    echo "  - REDDIT_SUBREDDIT: $SUBREDDIT"
else
    echo "✗ Error setting environment variables"
    exit 1
fi
