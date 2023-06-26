import os
import json
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

load_dotenv()
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'
VIDEO_ID = 'x6a4hMyiwBo'
DEVELOPER_KEY = os.getenv("YOUTUBE_API_DEVELOPER_KEY")  # replace with your actual key


def get_youtube_service():
    return build(API_SERVICE_NAME, API_VERSION, developerKey=DEVELOPER_KEY)


def get_comments(youtube, video_id, num_comments=100):
    all_comments = []
    next_page_token = None
    options = {
        'part': 'snippet,replies',
        'videoId': video_id,
        'maxResults': num_comments,
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

            next_page_token = response.get('next_page_token')
            if not next_page_token:
                break
        except HttpError as e:
            print(f'An error occurred: {e}')
            break

    return all_comments


def save_comments_to_file(comments, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(comments, f, ensure_ascii=False, indent=4)


def main():
    youtube = get_youtube_service()
    comments = get_comments(youtube, VIDEO_ID)
    save_comments_to_file(comments, f'comments_{VIDEO_ID}.json')


if __name__ == "__main__":
    # TODO This python file currently doesn't connect up to the rest of the project. It's just a standalone script.
    #  In the future, update the rest of the project to connect to this file.
    main()
