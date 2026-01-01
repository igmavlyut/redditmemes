import json
import urllib.request
import urllib.parse
import base64
import os
from typing import List, Dict, Optional

# Get credentials from environment variables
REDDIT_CLIENT_ID = os.environ.get('REDDIT_CLIENT_ID', '')
REDDIT_CLIENT_SECRET = os.environ.get('REDDIT_CLIENT_SECRET', '')
REDDIT_USER_AGENT = os.environ.get('REDDIT_USER_AGENT', 'MemeBot/1.0 by YourUsername')
REDDIT_SUBREDDIT = os.environ.get('REDDIT_SUBREDDIT', 'tarotmemes')


def handler(event, context):
    """
    Yandex Cloud Function handler for searching memes in Reddit via OAuth API
    
    Expected in event:
    - keywords: comma-separated keywords string (required)
    - subreddit: (optional) subreddit name, defaults to REDDIT_SUBREDDIT environment variable
    - limit: (optional) number of results, defaults to 10
    """
    
    try:
        # Check for credentials
        if not REDDIT_CLIENT_ID or not REDDIT_CLIENT_SECRET:
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'error': 'Reddit API credentials not configured',
                    'message': 'Please set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET environment variables'
                }, ensure_ascii=False)
            }
        
        # Get parameters from request
        if isinstance(event, dict):
            keywords = event.get('keywords', '')
            subreddit = event.get('subreddit', REDDIT_SUBREDDIT)
            limit = int(event.get('limit', 10))
        else:
            # If event is a string (e.g., from HTTP request)
            try:
                params = json.loads(event) if isinstance(event, str) else {}
            except json.JSONDecodeError:
                params = {}
            keywords = params.get('keywords', '')
            subreddit = params.get('subreddit', REDDIT_SUBREDDIT)
            limit = int(params.get('limit', 10))
        
        if not keywords:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Keywords parameter is required',
                    'message': 'Please provide keywords separated by comma'
                }, ensure_ascii=False)
            }
        
        # Get access token
        access_token = get_reddit_access_token()
        if not access_token:
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'error': 'Failed to authenticate with Reddit API',
                    'message': 'Could not obtain access token. Please check your credentials.'
                }, ensure_ascii=False)
            }
        
        # Split keywords
        keyword_list = [kw.strip() for kw in keywords.split(',') if kw.strip()]
        
        # Search memes for each keyword
        all_images = []
        for keyword in keyword_list:
            images = search_reddit_memes(keyword, subreddit, limit, access_token)
            all_images.extend(images)
        
        # Remove duplicates by URL
        unique_images = []
        seen_urls = set()
        for img in all_images:
            if img['url'] not in seen_urls:
                seen_urls.add(img['url'])
                unique_images.append(img)
        
        # Sort by score (popularity)
        unique_images.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'keywords': keywords,
                'subreddit': subreddit,
                'total_found': len(unique_images),
                'images': unique_images[:limit]
            }, ensure_ascii=False)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'message': 'Internal server error'
            }, ensure_ascii=False)
        }


def get_reddit_access_token() -> Optional[str]:
    """
    Gets OAuth access token from Reddit using client_credentials flow
    
    Returns:
        Access token string or None in case of error
    """
    url = 'https://www.reddit.com/api/v1/access_token'
    
    # Prepare Basic Auth
    credentials = f"{REDDIT_CLIENT_ID}:{REDDIT_CLIENT_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    data = urllib.parse.urlencode({
        'grant_type': 'client_credentials'
    }).encode()
    
    req = urllib.request.Request(url, data=data, headers={
        'Authorization': f'Basic {encoded_credentials}',
        'User-Agent': REDDIT_USER_AGENT,
        'Content-Type': 'application/x-www-form-urlencoded'
    })
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            access_token = result.get('access_token', '')
            if access_token:
                return access_token
            else:
                print(f"Error: No access token in response: {result}")
                return None
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8') if hasattr(e, 'read') else str(e)
        print(f"HTTP Error getting access token: {e.code} - {error_body}")
        return None
    except Exception as e:
        print(f"Error getting access token: {e}")
        return None


def search_reddit_memes(keyword: str, subreddit: str, limit: int, access_token: str) -> List[Dict]:
    """
    Searches for memes in Reddit by keyword with OAuth authorization
    
    Args:
        keyword: keyword to search for
        subreddit: subreddit name
        limit: maximum number of results
        access_token: OAuth access token
    
    Returns:
        List of dictionaries with meme information
    """
    
    # Use OAuth endpoint
    search_url = f"https://oauth.reddit.com/r/{subreddit}/search"
    params = {
        'q': keyword,
        'restrict_sr': 'true',
        'sort': 'top',
        'limit': min(limit, 25),  # Reddit API limits to 25 per request
        'type': 'link',
        't': 'all'  # time period: all, year, month, week, day
    }
    
    url = f"{search_url}?{urllib.parse.urlencode(params)}"
    
    req = urllib.request.Request(url, headers={
        'Authorization': f'Bearer {access_token}',
        'User-Agent': REDDIT_USER_AGENT
    })
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            images = []
            if 'data' in data and 'children' in data['data']:
                for post in data['data']['children']:
                    post_data = post.get('data', {})
                    
                    # Check if it's an image
                    url = post_data.get('url', '')
                    if is_image_url(url):
                        images.append({
                            'title': post_data.get('title', ''),
                            'url': url,
                            'permalink': f"https://www.reddit.com{post_data.get('permalink', '')}",
                            'score': post_data.get('score', 0),
                            'subreddit': post_data.get('subreddit', ''),
                            'author': post_data.get('author', ''),
                            'created_utc': post_data.get('created_utc', 0),
                            'keyword': keyword
                        })
            
            return images
            
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8') if hasattr(e, 'read') else str(e)
        print(f"HTTP Error searching Reddit: {e.code} - {error_body}")
        return []
    except Exception as e:
        print(f"Error searching Reddit: {e}")
        return []


def is_image_url(url: str) -> bool:
    """
    Checks if URL points to an image
    
    Args:
        url: URL to check
    
    Returns:
        True if URL points to an image, False otherwise
    """
    if not url:
        return False
    
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    url_lower = url.lower()
    
    # Check file extensions
    if any(url_lower.endswith(ext) for ext in image_extensions):
        return True
    
    # Check popular image hosting services
    image_hosts = [
        'i.redd.it',
        'i.imgur.com',
        'imgur.com/a/',
        'imgur.com/gallery/',
        'preview.redd.it'
    ]
    
    # Check if it's not an imgur page but a direct image
    if 'imgur.com' in url_lower:
        # Exclude gallery and album pages
        if '/a/' in url_lower or '/gallery/' in url_lower:
            return False
        # Accept direct image links
        return True
    
    if any(host in url_lower for host in image_hosts):
        return True
    
    return False

