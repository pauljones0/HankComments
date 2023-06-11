import re

class RemoveAscii:
    def __init__(self):
        self.ascii_pattern = re.compile(r'[^\x00-\x7F]+')

    def execute(self, text):
        return self.ascii_pattern.sub(r'', text)

class RemoveUrls:
    def __init__(self):
        self.url_pattern = re.compile(r'https?://\S+')

    def execute(self, text):
        return self.url_pattern.sub(r'', text)

class ReplaceDoubleQuotes:
    def execute(self, text):
        return text.replace('""', '"')