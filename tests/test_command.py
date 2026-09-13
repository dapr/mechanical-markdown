"""
Copyright (c) Microsoft Corporation.
Licensed under the MIT License.
"""

import os
import tempfile
import threading
import unittest

from unittest.mock import MagicMock, patch

from mechanical_markdown.command import Command


class TestCommandWorkingDirectoryIsolation(unittest.TestCase):
    def test_concurrent_commands_each_run_in_their_own_directory(self):
        # Command.run() used to chdir() the whole process around Popen, which
        # is not thread safe: background steps start multiple Command threads
        # without waiting for each other, so one thread's chdir could race
        # with another's and make it spawn its process in the wrong
        # directory. It now passes cwd directly to Popen instead, which is
        # per call and thread safe. Run two Commands with different working
        # directories concurrently and check each one's Popen call got its
        # own cwd, with the process's actual cwd never touched at all.
        original_cwd = os.getcwd()
        dir_a = tempfile.mkdtemp()
        dir_b = tempfile.mkdtemp()
        self.addCleanup(os.rmdir, dir_a)
        self.addCleanup(os.rmdir, dir_b)

        cmd_a = Command('echo a', dir_a, os.environ, 'bash -c', 5)
        cmd_b = Command('echo b', dir_b, os.environ, 'bash -c', 5)
        seen_cwd = {}

        def fake_popen(args_list, **kwargs):
            proc = MagicMock()
            proc.communicate.return_value = ('', '')
            proc.returncode = 0
            seen_cwd[threading.current_thread()] = kwargs.get('cwd')
            return proc

        with patch('mechanical_markdown.command.Popen', side_effect=fake_popen):
            cmd_a.start()
            cmd_b.start()
            cmd_a.join(timeout=2)
            cmd_b.join(timeout=2)

        self.assertEqual(seen_cwd.get(cmd_a), dir_a)
        self.assertEqual(seen_cwd.get(cmd_b), dir_b)
        self.assertEqual(os.getcwd(), original_cwd)


if __name__ == '__main__':
    unittest.main()
