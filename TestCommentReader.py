import os
from dotenv import load_dotenv
from TextInput import CSVFileHandler, CommentReader, CommentParser
from TextCleaner import RemoveAscii, RemoveUrls, ReplaceDoubleQuotes


def test_comment_reader():
    file_handler = CSVFileHandler("HankGreen.txt")
    cleaners = [RemoveAscii(), RemoveUrls(), ReplaceDoubleQuotes()]
    parser = CommentParser(cleaners)
    reader = CommentReader(file_handler, parser)
    comments = reader.read_comments()
    print(comments)


load_dotenv()
test_comment_reader()
