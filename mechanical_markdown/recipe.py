
"""
Copyright (c) Microsoft Corporation.
Licensed under the MIT License.
"""

from mistune import Markdown
from mechanical_markdown.parsers import RecipeParser, end_token, MarkdownAnnotationError


class Recipe:
    def __init__(self, markdown):
        parser = RecipeParser()
        md = Markdown(parser, extensions=('fenced-code',))
        md(markdown)
        if parser.current_step is not None:
            raise MarkdownAnnotationError('Reached end of input searching for <!-- {} -->'.format(end_token))
        self.all_steps = parser.all_steps

    def exectute_steps(self, manual, default_shell='bash -c'):
        success = True
        report = ""
        for step in self.all_steps:
            if not step.run_all_commands(manual, default_shell):
                success = False
                break

        for step in self.all_steps:
            if not step.wait_for_all_background_commands():
                success = False

            s, r = step.validate_and_report()
            if not s:
                success = False
            report += r
        return success, report

    def dryrun(self, default_shell='bash -c'):
        retstr = ""
        for step in self.all_steps:
            retstr += step.dryrun(default_shell)

        return retstr
