#!/bin/bash

# Скрипт для установки переменных окружения в Yandex Cloud Function
# Использование: ./set_env.sh YOUR_CLIENT_ID YOUR_CLIENT_SECRET YOUR_USERNAME

FOLDER_ID="b1gduh7hn89hjb3h22sh"
FUNCTION_NAME="reddit-parse"
SUBREDDIT="tarotmemes"

if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ]; then
    echo "Использование: ./set_env.sh CLIENT_ID CLIENT_SECRET REDDIT_USERNAME"
    echo "Пример: ./set_env.sh abc123 xyz789 myusername"
    exit 1
fi

CLIENT_ID=$1
CLIENT_SECRET=$2
USERNAME=$3

echo "Установка переменных окружения для функции $FUNCTION_NAME..."

yc serverless function set-environment-variables \
  --name $FUNCTION_NAME \
  --folder-id $FOLDER_ID \
  --environment REDDIT_CLIENT_ID=$CLIENT_ID \
  --environment REDDIT_CLIENT_SECRET=$CLIENT_SECRET \
  --environment REDDIT_USER_AGENT="MemeBot/1.0 by $USERNAME" \
  --environment REDDIT_SUBREDDIT=$SUBREDDIT

if [ $? -eq 0 ]; then
    echo "✓ Переменные окружения успешно установлены!"
    echo "  - REDDIT_SUBREDDIT: $SUBREDDIT"
else
    echo "✗ Ошибка при установке переменных окружения"
    exit 1
fi

