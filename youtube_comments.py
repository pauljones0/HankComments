import json
import time
import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import config

def get_youtube_service():
    """Create and return a YouTube API service object."""
    try:
        return build(
            "youtube", 
            "v3", 
            developerKey=config.YOUTUBE_API_KEY
        )
    except Exception as e:
        print(f"Error creating YouTube service: {e}")
        raise

def get_comments(youtube, video_id, max_results=100):
    """Fetch comments from a YouTube video."""
    all_comments = []
    next_page_token = None
    
    options = {
        'part': 'snippet,replies',
        'videoId': video_id,
        'maxResults': max_results,
        'textFormat': 'plainText',
        'order': 'time'
    }
    
    while True:
        try:
            if next_page_token:
                options['pageToken'] = next_page_token
                
            response = youtube.commentThreads().list(**options).execute()
            
            for item in response['items']:
                comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
                all_comments.append(comment)
                
                if 'replies' in item:
                    for reply in item['replies']['comments']:
                        all_comments.append(reply['snippet']['textDisplay'])
            
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break
                
            # Respect API rate limits
            time.sleep(1)
            
        except HttpError as e:
            print(f'An error occurred: {e}')
            break
    
    return all_comments

def save_comments(comments, filename=None):
    """Save comments to a JSON file and return them."""
    if filename is None:
        filename = config.COMMENTS_FILE
        
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(comments, f, ensure_ascii=False, indent=4)
    
    print(f"Saved {len(comments)} comments to {filename}")
    return comments

def load_comments(filename=None):
    """Load comments from a JSON file if it exists."""
    if filename is None:
        filename = config.COMMENTS_FILE
        
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            comments = json.load(f)
        print(f"Loaded {len(comments)} comments from {filename}")
        return comments
    return None

def extract_comments(video_id=None, force_refresh=False):
    """Extract comments from YouTube, with option to use cached results."""
    if video_id is None:
        video_id = config.VIDEO_ID
        
    # Check if we already have the comments cached
    if not force_refresh:
        cached_comments = load_comments()
        if cached_comments:
            return cached_comments
    
    # If we need to fetch comments
    youtube = get_youtube_service()
    comments = get_comments(youtube, video_id)
    return save_comments(comments) 