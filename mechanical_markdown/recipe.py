
"""
Copyright (c) Microsoft Corporation.
Licensed under the MIT License.
"""

import requests
from mistune import Markdown
from mechanical_markdown.parsers import RecipeParser, end_token, end_ignore_links_token, MarkdownAnnotationError
from termcolor import colored


class Recipe:
    def __init__(self, markdown):
        parser = RecipeParser()
        md = Markdown(parser, extensions=('fenced-code',))
        md(markdown)
        if parser.current_step is not None:
            raise MarkdownAnnotationError(f'Reached end of input searching for <!-- {end_token} -->')
        if parser.ignore_links:
            raise MarkdownAnnotationError(f'Reached end of input searching for <!-- {end_ignore_links_token}')
        self.all_steps = parser.all_steps
        self.external_links = parser.external_links

    def exectute_steps(self, manual, default_shell='bash -c', validate_links=False):
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

        if validate_links:
            report += "\nExternal link validation:\n"
            for link, ignore in self.external_links:
                if ignore:
                    report += f'\t{link} Status: {colored("Ignored", "yellow")}\n'
                    continue
                try:
                    response = requests.get(link)
                    if response.status_code >= 400:
                        success = False
                        report += f'\t{link} Status: {colored(response.status_code, "red")}\n'
                    else:
                        report += f'\t{link} Status: {colored(response.status_code, "green")}\n'
                except requests.exceptions.ConnectionError:
                    success = False
                    report += f'\t{link} Status: {colored("Connection Failed", "red")}\n'

        return success, report

    def dryrun(self, default_shell='bash -c'):
        retstr = ""
        for step in self.all_steps:
            retstr += step.dryrun(default_shell)

        return retstr
