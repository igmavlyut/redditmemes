# Reddit Memes Parser - Yandex Cloud Function

Serverless function for searching memes in Reddit by keywords via OAuth API.

## Project Structure

- `index.py` - main function code
- `requirements.txt` - dependencies (empty, uses standard libraries)
- `deploy.sh` - deployment script
- `set_env.sh` - environment variables setup script

## Requirements

1. Yandex Cloud CLI installed and configured
2. Reddit application created with obtained `client_id` and `client_secret`
3. Access to folder `reddit-parser` (ID: `b1gduh7hn89hjb3h22sh`)

## Environment Variables Setup

After obtaining keys from Reddit, run:

```bash
chmod +x set_env.sh
./set_env.sh YOUR_CLIENT_ID YOUR_CLIENT_SECRET YOUR_REDDIT_USERNAME
```

Or manually:

```bash
yc serverless function set-environment-variables \
  --name reddit-parse \
  --folder-id b1gduh7hn89hjb3h22sh \
  --environment REDDIT_CLIENT_ID=your_client_id \
  --environment REDDIT_CLIENT_SECRET=your_client_secret \
  --environment REDDIT_USER_AGENT="MemeBot/1.0 by YourUsername" \
  --environment REDDIT_SUBREDDIT=tarotmemes
```

## Deployment

```bash
chmod +x deploy.sh
./deploy.sh
```

Or manually:

```bash
# Create ZIP archive
zip -r function.zip index.py requirements.txt

# Deploy function
yc serverless function version create \
  --function-name reddit-parse \
  --folder-id b1gduh7hn89hjb3h22sh \
  --runtime python312 \
  --entrypoint index.handler \
  --memory 128m \
  --execution-timeout 10s \
  --source-path function.zip

# Remove temporary file
rm function.zip
```

## Usage

Function accepts JSON with parameters:

```json
{
  "keywords": "tarot, reading, cards",
  "subreddit": "tarotmemes",
  "limit": 10
}
```

Returns:

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
        "permalink": "https://www.reddit.com/r/tarotmemes/...",
        "score": 1234,
        "subreddit": "tarotmemes",
        "author": "username",
        "created_utc": 1234567890,
        "keyword": "tarot"
      }
    ]
  }
}
```

## Parameters

- `keywords` (required) - comma-separated keywords
- `subreddit` (optional) - subreddit name, defaults to `REDDIT_SUBREDDIT` environment variable (tarotmemes)
- `limit` (optional) - number of results, defaults to 10

## Environment Variables

- `REDDIT_CLIENT_ID` - Client ID from Reddit application (required)
- `REDDIT_CLIENT_SECRET` - Client Secret from Reddit application (required)
- `REDDIT_USER_AGENT` - User-Agent string for Reddit API (required)
- `REDDIT_SUBREDDIT` - default subreddit name (default: tarotmemes)
