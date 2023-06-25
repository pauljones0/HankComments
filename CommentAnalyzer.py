import json
import os
import openai
import time
from dotenv import load_dotenv
from TextInput import CSVFileHandler, CommentReader, CommentParser
from TextCleaner import RemoveAscii, RemoveUrls, ReplaceDoubleQuotes
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
    retry_if_exception
)


def should_retry(exception):
    """Return True if we should retry depending on the error"""
    if isinstance(exception, openai.error.APIError) or isinstance(exception, openai.error.Timeout) or isinstance(
            exception, openai.error.RateLimitError) or isinstance(exception, openai.error.ServiceUnavailableError):
        return True
    elif isinstance(exception, openai.error.AuthenticationError) \
            or isinstance(exception, openai.error.APIConnectionError) \
            or isinstance(exception, openai.error.InvalidRequestError):
        return False
    return Exception


def load_environment():
    load_dotenv()  # take environment variables from .env.
    openai.organization = os.getenv("OPENAI_ORGANIZATION")
    openai.api_key = os.getenv("OPENAI_API_KEY")


def get_comments(textfile):
    file_handler = CSVFileHandler(textfile)
    cleaners = [RemoveAscii(), RemoveUrls(), ReplaceDoubleQuotes()]
    parser = CommentParser(cleaners)
    reader = CommentReader(file_handler, parser)
    return reader.read_comments()


def generate_prompt(comments_batch):
    return '\n'.join(comments_batch)


def save_failed_request(request, response):
    # Create a failedRequests directory if it doesn't exist
    if not os.path.exists('failedRequests'):
        os.makedirs('failedRequests')

    # Using a timestamp to ensure each filename is unique
    filename = f"failedRequests/{time.time()}_request_response.txt"

    with open(filename, 'w') as f:
        f.write('Request:\n')
        f.write(json.dumps(request, indent=4))
        f.write('\n\nResponse:\n')
        f.write(json.dumps(response, indent=4))


def parse_response(request, response):
    content = response['choices'][0]['message']['content']
    try:
        suggestions = json.loads(content)  # attempt to parse the JSON content
    except json.JSONDecodeError:
        print(f"Failed to parse JSON response: {content}")
        save_failed_request(request, response)
        suggestions = None
    return suggestions


class CommentAnalyzer:

    def __init__(self):
        load_environment()
        self.INPUT_FILE = "HankGreen.txt"
        self.OUTFILE = "HankGreen.json"
        self.MAX_CHARS_PER_BATCH = 4000
        self.SYSTEM_PROMPT = "Style: Multiple comments with media suggestions.\nCriteria: Real, well-known, mass-produced media including video games, TV shows, books, YouTube channels, and movies.\nOutput: A JSON object with lists of media suggestions in 'Video Games', 'TV Shows', 'Books', 'YouTube Channels', 'Movies'. Each suggestion includes 'name' and 'count'. Avoid double-counting. Correct all names and colloquialisms. Aim to minimize token usage."
        self.result_dict = {'Video Games': {}, 'TV Shows': {}, 'Books': {}, 'YouTube Channels': {}, 'Movies': {}}

    def process_comments(self, comments):
        comment_batch_char_count = 0
        comment_batch = []

        for comment in comments:
            if comment_batch_char_count + len(comment) > self.MAX_CHARS_PER_BATCH:  # assuming 3:1 char-to-token ratio
                self.process_batch(comment_batch)
                comment_batch = []
                comment_batch_char_count = 0

            comment_batch.append(comment)
            comment_batch_char_count += len(comment)

    def process_batch(self, comment_batch):
        prompt = generate_prompt(comment_batch)
        message = self.generate_message(prompt)
        response = self.generate_request(message)
        suggestions = parse_response(message, response)
        self.update_result_dict(suggestions)

    def generate_message(self, prompt):
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

    def update_result_dict(self, suggestions):
        if suggestions is None:
            return

        for category, suggestions_dict in suggestions.items():
            for name, count in suggestions_dict.items():
                if name in self.result_dict[category]:
                    self.result_dict[category][name] += count
                else:
                    self.result_dict[category][name] = count

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6),
           retry=retry_if_exception(should_retry))
    def generate_request(self, messages):
        return openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0,
        )

    def store_results(self):
        with open(self.OUTFILE, 'w') as f:
            json.dump(self.result_dict, f)

    def run(self):
        comments = get_comments(self.INPUT_FILE)
        self.process_comments(comments)
        self.store_results()
