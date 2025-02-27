import json
import os
import openai
import time
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
    retry_if_exception
)
import config

def should_retry(exception):
    """Return True if we should retry depending on the error"""
    if isinstance(exception, openai.APIError) or isinstance(exception, openai.APITimeoutError) or isinstance(
            exception, openai.RateLimitError) or isinstance(exception, openai.APIStatusError) or isinstance(
        exception, openai.APIConnectionError):
        return True
    elif isinstance(exception, openai.AuthenticationError) \
            or isinstance(exception, openai.BadRequestError):
        return False
    return Exception

def log_error(request, response, error_type=None):
    """Log errors to a file for debugging."""
    os.makedirs(os.path.dirname(config.ERROR_LOG_FILE), exist_ok=True)
    
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    
    with open(config.ERROR_LOG_FILE, 'a') as f:
        f.write(f"\n\n=== ERROR LOG ENTRY: {timestamp} ===\n")
        if error_type:
            f.write(f"Error Type: {error_type}\n")
        f.write('Request:\n')
        f.write(json.dumps(request, indent=4))
        f.write('\n\nResponse:\n')
        f.write(json.dumps(response, indent=4) if isinstance(response, dict) else str(response))

def load_progress():
    """Load progress from a JSON file if it exists."""
    if os.path.exists(config.PROGRESS_FILE):
        with open(config.PROGRESS_FILE, 'r') as f:
            return json.load(f)
    else:
        return {
            'Video Games': {}, 
            'TV Shows': {}, 
            'Books': {}, 
            'YouTube Channels': {},
            'Movies': {}
        }

def save_progress(result_dict):
    """Save progress to a JSON file."""
    os.makedirs(os.path.dirname(config.PROGRESS_FILE), exist_ok=True)
    with open(config.PROGRESS_FILE, 'w') as f:
        json.dump(result_dict, f, indent=4)

def save_analysis(result_dict, filename=None):
    """Save final analysis to a JSON file."""
    if filename is None:
        filename = config.ANALYSIS_FILE
        
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with open(filename, 'w') as f:
        json.dump(result_dict, f, indent=4)
    
    print(f"Saved analysis to {filename}")
    return result_dict

def load_analysis(filename=None):
    """Load analysis from a JSON file if it exists."""
    if filename is None:
        filename = config.ANALYSIS_FILE
        
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            analysis = json.load(f)
        print(f"Loaded analysis from {filename}")
        return analysis
    return None

class CommentAnalyzer:
    def __init__(self):
        # Initialize OpenAI client
        openai.api_key = config.OPENAI_API_KEY
        self.client = openai.OpenAI()
        
        # Load existing progress if any
        self.result_dict = load_progress()
        
        # Define system prompt and response schema
        self.SYSTEM_PROMPT = "Style: Multiple comments with media suggestions.\nCriteria: Real, well-known, " \
                             "mass-produced media including video games, TV shows, books, YouTube channels, " \
                             "and movies.\nOutput: A JSON object with lists of media suggestions in 'Video Games', " \
                             "'TV Shows', 'Books', 'YouTube Channels', 'Movies'. Each suggestion includes 'name' and " \
                             "'count'. Avoid double-counting. Correct all names and colloquialisms. Aim to minimize " \
                             "token usage."
        
        # Define the JSON schema for structured output
        self.response_schema = {
            "type": "json_schema",
            "json_schema": {
                "name": "media_suggestions",
                "schema": {
                    "type": "object",
                    "properties": {
                        "Video Games": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "count": {"type": "integer"}
                                },
                                "required": ["name", "count"],
                                "additionalProperties": False
                            }
                        },
                        "TV Shows": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "count": {"type": "integer"}
                                },
                                "required": ["name", "count"],
                                "additionalProperties": False
                            }
                        },
                        "Books": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "count": {"type": "integer"}
                                },
                                "required": ["name", "count"],
                                "additionalProperties": False
                            }
                        },
                        "YouTube Channels": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "count": {"type": "integer"}
                                },
                                "required": ["name", "count"],
                                "additionalProperties": False
                            }
                        },
                        "Movies": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "count": {"type": "integer"}
                                },
                                "required": ["name", "count"],
                                "additionalProperties": False
                            }
                        }
                    },
                    "required": ["Video Games", "TV Shows", "Books", "YouTube Channels", "Movies"],
                    "additionalProperties": False
                },
                "strict": True
            }
        }
        
        # Maximum characters per batch (staying under token limits)
        self.MAX_CHARS_PER_BATCH = 384000  # ~128k tokens with 3:1 char-to-token ratio

    def generate_prompt(self, comments_batch):
        """Generate a prompt from a batch of comments."""
        return '\n'.join(comments_batch)

    def generate_messages(self, prompt):
        """Generate messages for the OpenAI API."""
        return [
            {
                "role": "system",
                "content": self.SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

    @retry(wait=wait_random_exponential(min=1, max=60), 
           stop=stop_after_attempt(6),
           retry=retry_if_exception(should_retry))
    def generate_request(self, messages):
        """Send a request to the OpenAI API with retry logic."""
        return self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0,
            response_format=self.response_schema
        )

    def parse_response(self, response):
        """Parse the response from the OpenAI API."""
        if response.choices[0].message.content:
            try:
                return json.loads(response.choices[0].message.content)
            except json.JSONDecodeError:
                print(f"Failed to parse JSON response")
                log_error({}, response, "JSONDecodeError")
                return None
        else:
            print("No content in response")
            log_error({}, response, "EmptyContent")
            return None

    def update_result_dict(self, suggestions):
        """Update the result dictionary with new suggestions."""
        print("Updating result dictionary...")
        if suggestions is None:
            return

        for category, suggestions_list in suggestions.items():
            if not isinstance(suggestions_list, list):
                print(f"Unexpected format in suggestions: {suggestions_list}")
                continue

            # Check if the category exists in the result dictionary, if not, create it
            if category not in self.result_dict:
                self.result_dict[category] = {}

            for suggestion in suggestions_list:
                name = suggestion.get('name')
                count = suggestion.get('count')
                
                if not name or not count:
                    print(f"Missing name or count in suggestion: {suggestion}")
                    continue

                if name in self.result_dict[category]:
                    self.result_dict[category][name] += count
                else:
                    self.result_dict[category][name] = count

    def process_batch(self, comment_batch):
        """Process a batch of comments."""
        prompt = self.generate_prompt(comment_batch)
        messages = self.generate_messages(prompt)
        
        print(f"Processing batch of {len(comment_batch)} comments...")
        response = self.generate_request(messages)
        
        # Extract content from response
        suggestions = None
        if hasattr(response.choices[0].message, 'content') and response.choices[0].message.content:
            suggestions = self.parse_response(response)
        
        if suggestions:
            self.update_result_dict(suggestions)
            save_progress(self.result_dict)  # Save progress after each batch
            return True
        return False

    def process_comments(self, comments):
        """Process all comments in batches."""
        comment_batch_char_count = 0
        comment_batch = []
        processed_count = 0

        for comment in comments:
            if comment_batch_char_count + len(comment) > self.MAX_CHARS_PER_BATCH:
                success = self.process_batch(comment_batch)
                processed_count += len(comment_batch) if success else 0
                comment_batch = []
                comment_batch_char_count = 0

            comment_batch.append(comment)
            comment_batch_char_count += len(comment)

        # Process the final batch if not empty
        if comment_batch:
            success = self.process_batch(comment_batch)
            processed_count += len(comment_batch) if success else 0

        print(f"Processed {processed_count} comments out of {len(comments)}")
        return self.result_dict

    def analyze_comments(self, comments=None, force_refresh=False):
        """Analyze comments, with option to use cached results."""
        # Check if we already have the analysis cached
        if not force_refresh:
            cached_analysis = load_analysis()
            if cached_analysis:
                self.result_dict = cached_analysis
                return cached_analysis
        
        # If we need to analyze comments
        if comments:
            self.process_comments(comments)
            return save_analysis(self.result_dict)
        else:
            print("No comments provided for analysis")
            return None 