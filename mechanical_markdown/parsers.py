
"""
Copyright (c) Microsoft Corporation.
Licensed under the MIT License.
"""

import yaml

from html.parser import HTMLParser
from mistune import Renderer
from mechanical_markdown.step import Step

start_token = 'STEP'
end_token = 'END_STEP'


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

        start_pos = comment_body.find(start_token)

        if start_pos < 0:
            return ""

        start_pos += len(start_token)
        self.current_step = Step(yaml.safe_load(comment_body[start_pos:]))

        return ""
