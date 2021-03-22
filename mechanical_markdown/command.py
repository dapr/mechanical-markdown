
"""
Copyright (c) Microsoft Corporation.
Licensed under the MIT License.
"""

import os
import time

from subprocess import Popen, PIPE, TimeoutExpired
from threading import Thread


class Command(Thread):
    def __init__(self, command_string, cwd, env, shell, timeout):
        super().__init__()
        self.command = command_string
        self.process = None
        self.return_code = -1
        self.output = {'stdout': '', 'stderr': ''}
        self.env = env
        self.shell = shell
        self.timeout = timeout
        self.cwd = cwd

    def _wait_or_timeout(self):
        try:
            self.output['stdout'], self.output['stderr'] = self.process.communicate(timeout=self.timeout)
        except TimeoutExpired:
            self.process.terminate()
            time.sleep(10)
            self.process.kill()
            try:
                self.output['stdout'], self.output['stderr'] = self.process.communicate(timeout=self.timeout)
            except TimeoutExpired:
                pass

        self.return_code = self.process.returncode

    def run(self):
        args_list = self.shell.split()
        args_list.append(self.command)
        pwd = os.getcwd()
        os.chdir(self.cwd)
        print("Running shell '{}' with command: `{}`".format(self.shell, self.command))
        self.process = Popen(args_list, universal_newlines=True, stdout=PIPE, stderr=PIPE, env=self.env)
        os.chdir(pwd)

        self._wait_or_timeout()

    def wait(self):
        try:
            self.join()
        except RuntimeError:
            pass
