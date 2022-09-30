
"""
Copyright (c) Microsoft Corporation.
Licensed under the MIT License.
"""

import requests
from mistune import Markdown
from mechanical_markdown.parsers import RecipeParser, end_token, end_ignore_links_token, MarkdownAnnotationError
from termcolor import colored
from time import sleep


class Recipe:
    def __init__(self, markdown, shell='bash -c'):
        parser = RecipeParser(shell)
        md = Markdown(parser)
        md(markdown)
        if parser.current_step is not None:
            raise MarkdownAnnotationError(f'Reached end of input searching for <!-- {end_token} -->')
        if parser.ignore_links:
            raise MarkdownAnnotationError(f'Reached end of input searching for <!-- {end_ignore_links_token} -->')
        self.all_steps = parser.all_steps
        self.external_links = parser.external_links

    def execute_steps(self, manual, validate_links=False, link_retries=3, tags=[]):
        success = True
        report = ""
        stepsToRun = list(filter(lambda step: self.filter_steps(tags, step), self.all_steps))
        for step in stepsToRun:
            if not step.run_all_commands(manual):
                success = False
                break

        for step in stepsToRun:
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
                retries = link_retries
                while retries > 0:
                    try:
                        response = requests.get(link)
                        if response.status_code >= 400:
                            retries -= 1
                            if retries == 0:
                                success = False
                                report += f'\t{link} Status: {colored(response.status_code, "red")}\n'
                        else:
                            report += f'\t{link} Status: {colored(response.status_code, "green")}\n'
                            break
                    except requests.exceptions.ConnectionError:
                        retries -= 1
                        if retries == 0:
                            success = False
                            report += f'\t{link} Status: {colored("Connection Failed", "red")}\n'
                    sleep(0.5)

        return success, report

    def dryrun(self):
        retstr = ""
        for step in self.all_steps:
            retstr += step.dryrun()

        return retstr

    def filter_steps(self, tags, step):
        if len(tags) == 0 or len(step.tags) == 0:
            return True

        for tag in tags:
            if tag in step.tags:
                return True

        return False
