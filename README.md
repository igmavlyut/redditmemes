# Reddit Memes Parser - Yandex Cloud Function

Функция для поиска мемов в Reddit по ключевым словам через OAuth API.

## Структура проекта

- `index.py` - основной код функции
- `requirements.txt` - зависимости (пустой, используются стандартные библиотеки)
- `deploy.sh` - скрипт для развертывания функции
- `set_env.sh` - скрипт для установки переменных окружения

## Требования

1. Yandex Cloud CLI установлен и настроен
2. Reddit приложение создано с полученными `client_id` и `client_secret`
3. Доступ к каталогу `reddit-parser` (ID: `b1gduh7hn89hjb3h22sh`)

## Установка переменных окружения

После получения ключей от Reddit, выполните:

```bash
chmod +x set_env.sh
./set_env.sh YOUR_CLIENT_ID YOUR_CLIENT_SECRET YOUR_REDDIT_USERNAME
```

Или вручную:

```bash
yc serverless function set-environment-variables \
  --name reddit-parse \
  --folder-id b1gduh7hn89hjb3h22sh \
  --environment REDDIT_CLIENT_ID=your_client_id \
  --environment REDDIT_CLIENT_SECRET=your_client_secret \
  --environment REDDIT_USER_AGENT="MemeBot/1.0 by YourUsername" \
  --environment REDDIT_SUBREDDIT=tarotmemes
```

## Развертывание

```bash
chmod +x deploy.sh
./deploy.sh
```

Или вручную:

```bash
# Создать ZIP архив
zip -r function.zip index.py requirements.txt

# Развернуть функцию
yc serverless function version create \
  --function-name reddit-parse \
  --folder-id b1gduh7hn89hjb3h22sh \
  --runtime python312 \
  --entrypoint index.handler \
  --memory 128m \
  --execution-timeout 10s \
  --source-path function.zip

# Удалить временный файл
rm function.zip
```

## Использование

Функция принимает JSON с параметрами:

```json
{
  "keywords": "tarot, reading, cards",
  "subreddit": "tarotmemes",
  "limit": 10
}
```

Возвращает:

```json
{
  "statusCode": 200,
  "body": {
    "keywords": "tarot, reading, cards",
    "subreddit": "tarotmemes",
    "total_found": 15,
    "images": [
      {
        "title": "Funny meme title",
        "url": "https://i.redd.it/...",
        "permalink": "https://www.reddit.com/r/memes/...",
        "score": 1234,
        "subreddit": "tarotmemes",
        "author": "username",
        "created_utc": 1234567890,
        "keyword": "funny"
      }
    ]
  }
}
```

## Параметры

- `keywords` (обязательно) - ключевые слова через запятую
- `subreddit` (опционально) - название subreddit, по умолчанию из переменной окружения `REDDIT_SUBREDDIT` (tarotmemes)
- `limit` (опционально) - количество результатов, по умолчанию 10

## Переменные окружения

- `REDDIT_CLIENT_ID` - Client ID от Reddit приложения (обязательно)
- `REDDIT_CLIENT_SECRET` - Client Secret от Reddit приложения (обязательно)
- `REDDIT_USER_AGENT` - User-Agent строка для Reddit API (обязательно)
- `REDDIT_SUBREDDIT` - название subreddit по умолчанию (по умолчанию: tarotmemes)

