
"""
Copyright (c) Microsoft Corporation.
Licensed under the MIT License.
"""

import os
import time

from subprocess import Popen, PIPE, TimeoutExpired


class Command:
    def __init__(self, command_string):
        self.command = command_string
        self.process = None
        self.return_code = -1
        self.output = {'stdout': '', 'stderr': ''}

    def wait_or_timeout(self, timeout):
        if self.process is None:
            return
        try:
            self.output['stdout'], self.output['stderr'] = self.process.communicate(timeout=timeout)
        except TimeoutExpired:
            self.process.terminate()
            time.sleep(10)
            self.process.kill()
            try:
                self.output['stdout'], self.output['stderr'] = self.process.communicate(timeout=timeout)
            except TimeoutExpired:
                pass

        self.return_code = self.process.returncode

    def run(self, cwd, env, shell):
        args_list = shell.split()
        args_list.append(self.command)
        pwd = os.getcwd()
        os.chdir(cwd)
        print("Running shell '{}' with command: `{}`".format(shell, self.command))
        self.process = Popen(args_list, stdout=PIPE, stderr=PIPE, universal_newlines=True, env=env)
        os.chdir(pwd)
