
"""
Copyright (c) Microsoft Corporation.
Licensed under the MIT License.
"""

import os
import time

from mechanical_markdown.command import Command
from termcolor import colored

default_timeout_seconds = 300

VALID_MATCH_MODES = ('exact', 'substring')

VALID_MATCH_ORDERS = ('sequential', 'none')


class Step:
    def __init__(self, parameters, shell):
        self.observed_output = {
            "stdout": "",
            "stderr": ""
        }
        self.return_values = ""
        self.commands = []
        self.background = False if "background" not in parameters else parameters["background"]
        self.sleep = 0 if "sleep" not in parameters else parameters["sleep"]
        self.name = "" if "name" not in parameters else parameters["name"]
        self.expected_lines = {"stdout": [], "stderr": []}
        if "expected_stdout_lines" in parameters and parameters["expected_stdout_lines"] is not None:
            self.expected_lines['stdout'] = parameters["expected_stdout_lines"]
        if "expected_stderr_lines" in parameters and parameters["expected_stderr_lines"] is not None:
            self.expected_lines['stderr'] = parameters["expected_stderr_lines"]
        self.expect_return_code = 0 if "expected_return_code" not in parameters else parameters["expected_return_code"]
        self.working_dir = os.getcwd() if "working_dir" not in parameters else parameters["working_dir"]
        self.timeout = default_timeout_seconds if "timeout_seconds" not in parameters else parameters["timeout_seconds"]
        self.env = dict(os.environ, **parameters['env']) if "env" in parameters else os.environ
        self.pause_message = None if "manual_pause_message" not in parameters else parameters["manual_pause_message"]
        self.match_mode = 'exact' if "output_match_mode" not in parameters else parameters["output_match_mode"]
        self.match_order = "sequential" if "match_order" not in parameters else parameters["match_order"]
        self.tags = [] if "tags" not in parameters else parameters["tags"]
        self.shell = shell

        if self.match_mode not in VALID_MATCH_MODES:
            from mechanical_markdown.parsers import MarkdownAnnotationError
            raise MarkdownAnnotationError(f'output_match_mode must be one of: {VALID_MATCH_MODES}')

        if self.match_order not in VALID_MATCH_ORDERS:
            from mechanical_markdown.parsers import MarkdownAnnotationError
            raise MarkdownAnnotationError(f'match_order must be one of: {VALID_MATCH_ORDERS}')

    def add_command_block(self, block):
        self.commands.append(Command(block.strip(), self.working_dir, self.env, self.shell, self.timeout + self.sleep))

    def run_all_commands(self, manual):
        if manual and self.pause_message is not None:
            try:
                while True:
                    if input(self.pause_message + "\nType 'x' to exit\n") == 'x':
                        break
            except KeyboardInterrupt:
                pass

        for command in self.commands:
            command.start()
            if not self.background:
                command.wait()
                if self.expect_return_code is not None and command.return_code != self.expect_return_code:
                    return False
            if self.sleep:
                time.sleep(self.sleep)

        return True

    def dryrun(self):
        retstr = "Step: {}\n".format(self.name)

        retstr += "\tcommands to run with '{}':\n".format(self.shell)
        for c in self.commands:
            retstr += "\t\t`{}`\n".format(c.command)

        for out in 'stdout', 'stderr':
            retstr += "\tExpected {}:\n".format(out)
            for expected in self.expected_lines[out]:
                retstr += "\t\t{}\n".format(expected)

        retstr += "\tExpected return code: {}\n".format(self.expect_return_code)

        return retstr + "\n"

    def wait_for_all_background_commands(self):
        success = True
        for command in self.commands:
            if self.background:
                command.wait()
                if self.expect_return_code is not None and command.return_code != self.expect_return_code:
                    success = False
        return success

    @classmethod
    def find_substring_in_list(cls, expected, lines):
        for idx, line in enumerate(lines):
            if expected in line:
                return idx
        return -1

    def validate_and_report(self):
        success = True
        report = ""
        if self.name != "":
            report += "Step: {}\n".format(self.name)

        for c in self.commands:
            if c.process is not None:
                color = 'green'
                if self.expect_return_code is None:
                    color = 'yellow'
                elif c.return_code != self.expect_return_code:
                    color = 'red'
                report += f"\tcommand: `{c.command}`\n"
                report += f"\treturn_code: {colored(c.return_code, color)}\n"
                report += f"\tduration_seconds: {c.duration_seconds:.{3}}\n"

        for out in 'stdout', 'stderr':
            report += "\tExpected {} (output_match_mode: {}, match_order: {}):\n".format(
                out, self.match_mode, self.match_order)
            for expected in self.expected_lines[out]:
                report += '\t\t' + expected + '\n'
            report += "\tActual {}:\n".format(out)

            not_found = {"stdout": [], "stderr": []}  # lines that were expected but not found
            output_found_markers = []  # index of lines that were found in the output

            # Gather output from all commands
            output_lines = []
            for c in self.commands:
                if c.process is not None:
                    output_lines += c.output[out].split("\n")

            # Find expected lines in the output
            output_lines_copy = output_lines[:]
            for expected in self.expected_lines[out]:
                if self.match_mode == 'exact':
                    if expected in output_lines_copy:
                        idx = output_lines_copy.index(expected)
                        # remove the line so it can't be matched again, but keep the index
                        output_lines_copy[idx] = ""
                        output_found_markers.append(idx)
                    else:
                        not_found[out].append(expected)
                elif self.match_mode == 'substring':
                    idx = Step.find_substring_in_list(expected, output_lines_copy)
                    if idx >= 0:
                        # remove the line so it can't be matched again, but keep the index
                        output_lines_copy[idx] = ""
                        output_found_markers.append(idx)
                    else:
                        not_found[out].append(expected)

            for idx, line in enumerate(output_lines):
                if idx in output_found_markers:
                    report += "\t\t{}\n".format(colored(line, 'green'))
                else:
                    report += "\t\t{}\n".format(line)

            if self.match_order == 'sequential' and sorted(output_found_markers) != output_found_markers:
                report += colored("\tERROR expected lines were not found in the correct order", 'red') + "\n"
                success = False

            if len(not_found[out]):
                success = False
                report += colored("\tERROR expected lines not found:", 'red') + "\n"
                for line in not_found[out]:
                    report += "\t\t" + colored(line, 'red') + "\n"

        return success, report
