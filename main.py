import json
import os
import openai
from dotenv import load_dotenv
from TextInput import CSVFileHandler, CommentReader, CommentParser
from TextCleaner import RemoveAscii, RemoveUrls, ReplaceDoubleQuotes

MAX_CHARS_PER_BATCH = int(os.getenv("MAX_CHARS_PER_BATCH"))
SYSTEM_PROMPT = os.getenv("PROMPT")


def get_comments(textfile):
    file_handler = CSVFileHandler(textfile)
    cleaners = [RemoveAscii(), RemoveUrls(), ReplaceDoubleQuotes()]
    parser = CommentParser(cleaners)
    reader = CommentReader(file_handler, parser)
    comments = reader.read_comments()
    return comments


def setup():
    load_dotenv()  # take environment variables from .env.
    openai.organization = os.getenv("OPENAI_ORGANIZATION")
    openai.api_key = os.getenv("OPENAI_API_KEY")


def main():
    store_results(get_suggestions_from_comments(get_comments(os.getenv("INPUT_FILE"))))


def generate_prompt(comments_batch):
    prompt = ""
    for comment in comments_batch:
        prompt += '\n' + comment
    return prompt


def parse_response(response):
    content = response['choices'][0]['message']['content']
    try:
        suggestions = json.loads(content)  # attempt to parse the JSON content
    except json.JSONDecodeError:
        print(f"Failed to parse JSON response: {content}")
        suggestions = None
    return suggestions


def get_suggestions_from_comments(comments):
    result_dict = {'Video Games': {}, 'TV Shows': {}, 'Books': {}, 'YouTube Channels': {}, 'Movies': {}}
    comment_batch_char_count = 0
    comment_batch = []

    for comment in comments:
        if comment_batch_char_count + len(comment) > MAX_CHARS_PER_BATCH:  # assuming 3:1 char-to-token ratio
            suggestions = get_suggestions_for_batch(comment_batch)

            # Clear comment_batch and reset size
            comment_batch = []
            comment_batch_char_count = 0

            # Update the result_dict with the new data
            if suggestions is not None:
                result_dict = update_result_dict(result_dict, suggestions)

        comment_batch.append(comment)
        comment_batch_char_count += len(comment)

    return result_dict


def get_suggestions_for_batch(comment_batch):
    prompt = generate_prompt(comment_batch)
    message = generate_message(prompt)
    response = generate_request(message)
    return parse_response(response)


def update_result_dict(result_dict, suggestions):
    for category, suggestions_dict in suggestions.items():
        for name, count in suggestions_dict.items():
            if name in result_dict[category]:
                result_dict[category][name] += count
            else:
                result_dict[category][name] = count
    return result_dict


def generate_message(prompt):
    return [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": prompt
        }
    ]


def generate_request(messages):
    return openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0,
    )


def store_results(result_dict):
    with open(os.getenv("OUTFILE"), 'w') as f:
        json.dump(result_dict, f)


# json.dump(f)


def create_message(user_message):
    return [
        {
            "role": "system",
            "content": {os.getenv("PROMPT")}
        },
        {
            "role": "user",
            "content": user_message
        }
    ]


if __name__ == '__main__':
    setup()
    main()
