
"""
Copyright (c) Microsoft Corporation.
Licensed under the MIT License.
"""

import os
import time

from mechanical_markdown.command import Command
from termcolor import colored

default_timeout_seconds = 60


class Step:
    def __init__(self, parameters):
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

    def add_command_block(self, block):
        self.commands.append(Command(block.strip()))

    def run_all_commands(self, manual, shell):
        if manual and self.pause_message is not None:
            try:
                while True:
                    if input(self.pause_message + "\nType 'x' to exit\n") == 'x':
                        break
            except KeyboardInterrupt:
                pass

        for command in self.commands:
            command.run(self.working_dir, self.env, shell)
            if not self.background:
                command.wait_or_timeout(self.timeout)
                if self.expect_return_code is not None and command.return_code != self.expect_return_code:
                    return False
            if self.sleep:
                time.sleep(self.sleep)

        return True

    def dryrun(self, shell):
        retstr = "Step: {}\n".format(self.name)

        retstr += "\tcommands to run with '{}':\n".format(shell)
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
                command.wait_or_timeout(self.timeout)
                if self.expect_return_code is not None and command.return_code != self.expect_return_code:
                    success = False
        return success

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
                report += "\tcommand: `{}`\n\treturn_code: {}\n".format(c.command, colored(c.return_code, color))

        for out in 'stdout', 'stderr':
            report += "\tExpected {}:\n".format(out)
            for expected in self.expected_lines[out]:
                report += '\t\t' + expected + '\n'
            report += "\tActual {}:\n".format(out)

            for c in self.commands:
                if c.process is not None:
                    for line in c.output[out].split("\n"):
                        if len(self.expected_lines[out]) and self.expected_lines[out][0] == line:
                            report += "\t\t{}\n".format(colored(line, 'green'))
                            self.expected_lines[out] = self.expected_lines[out][1:]
                        else:
                            report += "\t\t{}\n".format(line)

            if len(self.expected_lines[out]):
                success = False
                report += colored("\tERROR expected lines not found:", 'red') + "\n"
                for line in self.expected_lines[out]:
                    report += "\t\t" + colored(line, 'red') + "\n"

        return success, report
