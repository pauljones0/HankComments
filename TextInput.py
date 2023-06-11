class CSVFileHandler:
    def __init__(self, filename):
        self.filename = filename

    def read_file(self):
        with open(self.filename, 'r', encoding='utf-8') as f:
            return f.readlines()


class CommentReader:
    def __init__(self, file_handler, comment_parser):
        self.file_handler = file_handler
        self.comment_parser = comment_parser

    def read_comments(self):
        lines = self.file_handler.read_file()
        return self.comment_parser.clean_and_parse_comments(lines)


def parse_comments(lines):
    comments = []
    comment = ''
    in_multiline_comment = False
    for line in lines:
        line = line.strip()
        if line.startswith('"') and line.endswith('"') and not in_multiline_comment:
            comments.append(line[1:-1])
        elif line.startswith('"') and not in_multiline_comment:
            in_multiline_comment = True
            comment += line[1:]
        elif line.endswith('"') and in_multiline_comment:
            comment += ' ' + line[:-1]
            comments.append(comment)
            comment = ''
            in_multiline_comment = False
        elif in_multiline_comment:
            comment += ' ' + line
        else:
            comments.append(line)
    return comments


class CommentParser:
    def __init__(self, cleaners=None):
        self.cleaners = cleaners if cleaners is not None else []

    def clean_and_parse_comments(self, lines):
        comments = parse_comments(lines)
        cleaned_comments = [self.clean_comments(comment) for comment in comments]
        return cleaned_comments

    def clean_comments(self, text):
        for cleaner in self.cleaners:
            text = cleaner.execute(text)
        return text
