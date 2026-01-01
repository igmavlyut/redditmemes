#!/bin/bash

# Скрипт для развертывания функции в Yandex Cloud Functions
# Использование: ./deploy.sh

FOLDER_ID="b1gduh7hn89hjb3h22sh"
FUNCTION_NAME="reddit-parse"
FUNCTION_ID="d4erqui9vsdqvh4g78ih"

echo "Подготовка к развертыванию функции $FUNCTION_NAME..."

# Создаем ZIP архив
echo "Создание ZIP архива..."
zip -r function.zip index.py requirements.txt

if [ $? -ne 0 ]; then
    echo "✗ Ошибка при создании ZIP архива"
    exit 1
fi

echo "✓ ZIP архив создан"

# Развертываем функцию
echo "Развертывание функции..."
yc serverless function version create \
  --function-name $FUNCTION_NAME \
  --folder-id $FOLDER_ID \
  --runtime python312 \
  --entrypoint index.handler \
  --memory 128m \
  --execution-timeout 10s \
  --source-path function.zip

if [ $? -eq 0 ]; then
    echo "✓ Функция успешно развернута!"
    echo ""
    echo "Не забудьте установить переменные окружения:"
    echo "  ./set_env.sh YOUR_CLIENT_ID YOUR_CLIENT_SECRET YOUR_USERNAME"
else
    echo "✗ Ошибка при развертывании функции"
    rm -f function.zip
    exit 1
fi

# Удаляем временный файл
rm -f function.zip
echo "✓ Временные файлы удалены"

