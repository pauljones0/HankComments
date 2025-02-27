import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_DEVELOPER_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Video configuration
VIDEO_ID = "x6a4hMyiwBo"  # Default video ID (Hank Green's video)
VIDEO_URL = f"https://www.youtube.com/watch?v={VIDEO_ID}"

# File paths
DATA_DIR = "data"
COMMENTS_FILE = os.path.join(DATA_DIR, f"comments_{VIDEO_ID}.json")
ANALYSIS_FILE = os.path.join(DATA_DIR, f"analysis_{VIDEO_ID}.json")
PROGRESS_FILE = os.path.join(DATA_DIR, "progress.json")
ERROR_LOG_FILE = os.path.join(DATA_DIR, "error_log.txt")

# Visualization settings
OUTPUT_DIR = "graphs"
GIF_OUTPUT = "hank_green_recommendations.gif"
ITEMS_TO_REMOVE = [
    'The Fault in Our Stars', 
    'Crash Course', 
    'SciShow', 
    'Sci Show', 
    'Dear Hank and John', 
    'Vlogbrothers', 
    'Hank Green', 
    'The Fault In Our Stars by John Green'
]
CATEGORIES = ['Video Games', 'TV Shows', 'Movies', 'Books', 'YouTube Channels']

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True) 