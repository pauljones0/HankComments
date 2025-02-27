import re

class TextCleaner:
    """Base class for text cleaning operations."""
    def clean(self, text):
        """Clean the text."""
        return text

class RemoveAscii(TextCleaner):
    """Remove non-ASCII characters from text."""
    def __init__(self):
        self.ascii_pattern = re.compile(r'[^\x00-\x7F]+')
        
    def clean(self, text):
        return self.ascii_pattern.sub('', text)

class RemoveUrls(TextCleaner):
    """Remove URLs from text."""
    def __init__(self):
        self.url_pattern = re.compile(r'https?://\S+')
        
    def clean(self, text):
        return self.url_pattern.sub('', text)

class ReplaceDoubleQuotes(TextCleaner):
    """Replace double quotes with single quotes."""
    def clean(self, text):
        return text.replace('""', '"')

def clean_text(text, cleaners=None):
    """Apply a series of cleaners to text."""
    if cleaners is None:
        cleaners = [RemoveAscii(), RemoveUrls(), ReplaceDoubleQuotes()]
        
    for cleaner in cleaners:
        text = cleaner.clean(text)
        
    return text