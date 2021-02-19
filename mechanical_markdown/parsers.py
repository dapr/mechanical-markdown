
"""
Copyright (c) Microsoft Corporation.
Licensed under the MIT License.
"""

import re
import yaml

from html.parser import HTMLParser
from mistune import Renderer
from mechanical_markdown.step import Step

start_token = 'STEP'
end_token = 'END_STEP'

ignore_links_token = 'IGNORE_LINKS'
end_ignore_links_token = 'END_IGNORE'


class MarkdownAnnotationError(Exception):
    pass


class HTMLCommentParser(HTMLParser):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.comment_text = ""

    def handle_comment(self, comment):
        self.comment_text += comment


class RecipeParser(Renderer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_step = None
        self.all_steps = []
        self.external_links = []
        self.ignore_links = False

    def block_code(self, text, lang):
        if lang is not None and lang.strip() in ('bash', 'sh') and self.current_step is not None:
            self.current_step.add_command_block(text)
        return ""

    def block_html(self, text):
        comment_parser = HTMLCommentParser()
        comment_parser.feed(text)

        comment_body = comment_parser.comment_text
        if comment_body.find(end_token) >= 0:
            if self.current_step is None:
                raise MarkdownAnnotationError("Unexpected <!-- {} --> found".format(end_token))
            self.all_steps.append(self.current_step)
            self.current_step = None
            return ""

        elif comment_body.find(ignore_links_token) >= 0:
            self.ignore_links = True

        elif comment_body.find(end_ignore_links_token) >= 0:
            if not self.ignore_links:
                raise MarkdownAnnotationError("Unexpected <!-- {} --> found".format(end_ignore_links_token))
            self.ignore_links = False

        start_pos = comment_body.find(start_token)

        if start_pos < 0:
            return ""

        start_pos += len(start_token)
        self.current_step = Step(yaml.safe_load(comment_body[start_pos:]))

        return ""

    def link(self, link, text=None, title=None):
        if re.match("https?://", link) is not None:
            self.external_links.append((link, self.ignore_links))
