
"""
Copyright (c) Microsoft Corporation.
Licensed under the MIT License.
"""

import os
import subprocess
import unittest

from mechanical_markdown import MechanicalMarkdown, MarkdownAnnotationError
from unittest.mock import patch, MagicMock, call
from termcolor import colored


class MechanicalMarkdownTests(unittest.TestCase):
    def setUp(self):
        self.command_ouputs = []

        self.process_mock = MagicMock()

        def pop_command(timeout=None):
            stdout, stderr, return_code = self.command_ouputs.pop(0)
            self.process_mock.returncode = return_code
            return (stdout, stderr)

        self.process_mock.communicate.side_effect = pop_command

        self.popen_mock = MagicMock()
        self.popen_mock.return_value = self.process_mock

        self.patcher = patch('mechanical_markdown.command.Popen', self.popen_mock)
        self.patcher.start()

    def prep_command_ouput(self, stdout, stderr, return_code):
        self.command_ouputs.append((stdout, stderr, return_code))

    def tearDown(self):
        self.patcher.stop()

    def test_basic_success(self):
        test_data = """
<!-- STEP
name: basic test
-->

```bash
echo "test"
```

<!-- END_STEP -->
"""
        self.prep_command_ouput("test", "", 0)
        mm = MechanicalMarkdown(test_data)
        success, report = mm.exectute_steps(False)
        self.assertTrue(success)
        self.popen_mock.assert_called_with(['bash', '-c', 'echo "test"'],
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE,
                                           universal_newlines=True,
                                           env=os.environ)

    @patch("mechanical_markdown.command.os.chdir")
    def test_working_dir_success(self, chdir_mock):
        test_data = """
<!-- STEP
name: basic test
working_dir: "./foo"
-->

```bash
echo "test"
```

<!-- END_STEP -->
"""
        self.prep_command_ouput("test", "", 0)
        mm = MechanicalMarkdown(test_data)
        success, report = mm.exectute_steps(False)
        self.assertTrue(success)
        self.popen_mock.assert_called_with(['bash', '-c', 'echo "test"'],
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE,
                                           universal_newlines=True,
                                           env=os.environ)
        chdir_mock.assert_has_calls([call("./foo"), call(os.getcwd())])

    @patch("mechanical_markdown.step.time.sleep")
    def test_sleep_is_honored(self, sleep_mock):
        test_data = """
<!-- STEP
name: basic test
sleep: 10
-->

```bash
echo "test"
```

<!-- END_STEP -->
"""
        self.prep_command_ouput("test", "", 0)
        mm = MechanicalMarkdown(test_data)
        success, report = mm.exectute_steps(False)
        self.assertTrue(success)
        self.popen_mock.assert_called_with(['bash', '-c', 'echo "test"'],
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE,
                                           universal_newlines=True,
                                           env=os.environ)
        sleep_mock.assert_called_with(10)

    def test_env(self):
        test_data = """
<!-- STEP
name: env test
env:
  ENVA: foo
  ENVB: bar
-->

```bash
echo "test"
```

<!-- END_STEP -->
"""

        expected_env = {"ENVA": "foo", "ENVB": "bar"}
        self.prep_command_ouput("test", "", 0)
        mm = MechanicalMarkdown(test_data)
        success, report = mm.exectute_steps(False)
        self.assertTrue(success)
        self.popen_mock.assert_called_with(['bash', '-c', 'echo "test"'],
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE,
                                           universal_newlines=True,
                                           env=dict(os.environ, **expected_env))

    def test_background_success(self):
        test_data = """
<!-- STEP
name: basic test
background: true
-->

```bash
echo "test"
```

<!-- END_STEP -->
"""
        self.prep_command_ouput("test", "", 0)
        mm = MechanicalMarkdown(test_data)
        success = mm.all_steps[0].run_all_commands(False, "bash -c")
        self.assertTrue(success)
        self.popen_mock.assert_called_with(['bash', '-c', 'echo "test"'],
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE,
                                           universal_newlines=True,
                                           env=os.environ)
        self.process_mock.communicate.assert_not_called()

        success = mm.all_steps[0].wait_for_all_background_commands()
        self.assertTrue(success)
        self.process_mock.communicate.assert_called_with(timeout=60)

    def test_background_failure(self):
        test_data = """
<!-- STEP
name: basic test
background: true
-->

```bash
echo "test"
```

<!-- END_STEP -->
"""
        self.prep_command_ouput("test", "", 1)
        mm = MechanicalMarkdown(test_data)
        success = mm.all_steps[0].run_all_commands(False, "bash -c")
        self.assertTrue(success)
        self.popen_mock.assert_called_with(['bash', '-c', 'echo "test"'],
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE,
                                           universal_newlines=True,
                                           env=os.environ)
        self.process_mock.communicate.assert_not_called()

        success = mm.all_steps[0].wait_for_all_background_commands()
        self.assertFalse(success)
        self.process_mock.communicate.assert_called_with(timeout=60)

    def test_failure_halts_further_executions(self):
        test_data = """
<!-- STEP
name: basic test
-->

```bash
echo "test"
```

```bash
echo "test2"
```

<!-- END_STEP -->
"""
        self.prep_command_ouput("test", "", 1)
        self.prep_command_ouput("test2", "", 0)
        mm = MechanicalMarkdown(test_data)
        success, report = mm.exectute_steps(False)
        self.assertFalse(success)
        self.popen_mock.assert_called_once_with(['bash', '-c', 'echo "test"'],
                                                stdout=subprocess.PIPE,
                                                stderr=subprocess.PIPE,
                                                universal_newlines=True,
                                                env=os.environ)

    def test_missing_expected_line_causes_failure(self):
        test_data = """
<!-- STEP
name: basic test
expected_stdout_lines:
  - green
-->

```bash
echo "test"
```

<!-- END_STEP -->
"""
        self.prep_command_ouput("test", "", 0)
        mm = MechanicalMarkdown(test_data)
        success, report = mm.exectute_steps(False)
        self.assertFalse(success)
        self.popen_mock.assert_called_once_with(['bash', '-c', 'echo "test"'],
                                                stdout=subprocess.PIPE,
                                                stderr=subprocess.PIPE,
                                                universal_newlines=True,
                                                env=os.environ)

    def test_expected_lines_succeed_when_matched(self):
        test_data = """
<!-- STEP
name: basic test
expected_stdout_lines:
  - test
  - test2
expected_stderr_lines:
  - error
-->

```bash
echo "test"
echo "test2"
echo "error" 1>&2
```

<!-- END_STEP -->
"""
        self.prep_command_ouput("test\ntest2", "error", 0)
        mm = MechanicalMarkdown(test_data)
        success, report = mm.exectute_steps(False)
        self.assertTrue(success)
        calls = [call(['bash', '-c', 'echo "test"\necho "test2"\necho "error" 1>&2'],
                      stdout=subprocess.PIPE,
                      stderr=subprocess.PIPE,
                      universal_newlines=True,
                      env=os.environ),
                 call().communicate(timeout=60)]
        self.popen_mock.assert_has_calls(calls)

    def test_timeout_is_respected(self):
        test_data = """
<!-- STEP
name: basic test
expected_stdout_lines:
  - test
timeout_seconds: 5
-->

```bash
echo "test"
```

<!-- END_STEP -->
"""
        self.prep_command_ouput("test", "", 0)
        mm = MechanicalMarkdown(test_data)
        success, report = mm.exectute_steps(False)
        self.assertTrue(success)
        calls = [call(['bash', '-c', 'echo "test"'],
                      stdout=subprocess.PIPE,
                      stderr=subprocess.PIPE,
                      universal_newlines=True,
                      env=os.environ),
                 call().communicate(timeout=5)]
        self.popen_mock.assert_has_calls(calls)

    def test_dryrun(self):
        test_data = """
<!-- STEP
name: basic test
expected_stdout_lines:
  - test
  - test2
-->

```bash
echo "test"
echo "test2"
```

<!-- END_STEP -->

<!-- STEP
name: step 2
expected_stdout_lines:
  - foo
expected_stderr_lines:
  - bar
-->

```bash
echo "foo"
echo "bar" >2
```

<!-- END_STEP -->
"""
        self.prep_command_ouput("test", "", 0)
        mm = MechanicalMarkdown(test_data)
        output = mm.dryrun()

        expected_output = """Step: basic test
\tcommands to run with 'bash -c':
\t\t`echo "test"
echo "test2"`
\tExpected stdout:
\t\ttest
\t\ttest2
\tExpected stderr:
\tExpected return code: 0

Step: step 2
\tcommands to run with 'bash -c':
\t\t`echo "foo"
echo "bar" >2`
\tExpected stdout:
\t\tfoo
\tExpected stderr:
\t\tbar
\tExpected return code: 0

"""
        self.assertEqual(expected_output, output)
        self.popen_mock.assert_not_called()

    @patch("mechanical_markdown.command.time.sleep")
    def test_timed_out_processes_are_killed(self, sleep_mock):
        test_data = """
<!-- STEP
name: basic test
-->

```bash
echo "test"
```

<!-- END_STEP -->
"""

        def raise_timeout(timeout=60):
            raise subprocess.TimeoutExpired("foo", 60.0)

        self.process_mock.communicate.side_effect = raise_timeout
        self.prep_command_ouput("test", "", 0)
        mm = MechanicalMarkdown(test_data)
        success, report = mm.exectute_steps(False)
        self.assertFalse(success)
        self.popen_mock.assert_called_with(['bash', '-c', 'echo "test"'],
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE,
                                           universal_newlines=True,
                                           env=os.environ)
        self.process_mock.terminate.assert_called()
        self.process_mock.kill.assert_called()
        self.process_mock.communicate.assert_has_calls([call(timeout=60), call(timeout=60)])

    @patch("builtins.input")
    def test_pause_waits_for_user_input(self, input_mock):
        test_data = """
<!-- STEP
name: basic test
manual_pause_message: "Stop Here"
-->

```bash
echo "test"
```

<!-- END_STEP -->
"""

        self.prep_command_ouput("test", "", 0)
        input_mock.return_value = 'x'
        mm = MechanicalMarkdown(test_data)
        success, report = mm.exectute_steps(True)
        input_mock.assert_called_with("Stop Here\nType 'x' to exit\n")
        self.assertTrue(success)
        self.popen_mock.assert_called_with(['bash', '-c', 'echo "test"'],
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE,
                                           universal_newlines=True,
                                           env=os.environ)

    def test_different_shell(self):
        test_data = """
<!-- STEP
name: basic test
-->

```bash
echo "test"
```

<!-- END_STEP -->
"""
        self.prep_command_ouput("test", "", 0)
        mm = MechanicalMarkdown(test_data)
        success, report = mm.exectute_steps(False, default_shell='cmd /c')
        self.assertTrue(success)
        self.popen_mock.assert_called_with(['cmd', '/c', 'echo "test"'],
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE,
                                           universal_newlines=True,
                                           env=os.environ)

    def test_missing_end_tag_throws_exception(self):
        test_data = """
<!-- STEP
name: basic test
-->

```bash
echo "test"
```

"""
        with self.assertRaises(MarkdownAnnotationError):
            MechanicalMarkdown(test_data)

        test_data = """
<!-- IGNORE_LINKS -->

"""
        with self.assertRaises(MarkdownAnnotationError):
            MechanicalMarkdown(test_data)

    def test_missing_extra_tag_throws_exception(self):
        test_data = """
<!-- STEP
name: basic test
-->

```bash
echo "test"
```

<!-- END_STEP -->

<!-- END_STEP -->
"""
        with self.assertRaises(MarkdownAnnotationError):
            MechanicalMarkdown(test_data)

        test_data = """
<!-- IGNORE_LINKS -->

<!-- END_IGNORE -->

<!-- END_IGNORE -->

"""
        with self.assertRaises(MarkdownAnnotationError):
            MechanicalMarkdown(test_data)

    def test_expect_status_code_success(self):
        test_data = """
<!-- STEP
name: expect returns 1
expected_return_code: 1
-->

```bash
exit 1
```

<!-- END_STEP -->

<!-- STEP
name: ignore return code
expected_return_code:
-->

```bash
exit 15
```

<!-- END_STEP -->
"""
        self.prep_command_ouput("test", "", 1)
        self.prep_command_ouput("test", "", 15)
        mm = MechanicalMarkdown(test_data)
        success, report = mm.exectute_steps(False)
        self.assertTrue(success)
        calls = [call(['bash', '-c', 'exit 1'],
                      stdout=subprocess.PIPE,
                      stderr=subprocess.PIPE,
                      universal_newlines=True,
                      env=os.environ),
                 call().communicate(timeout=60),
                 call(['bash', '-c', 'exit 15'],
                      stdout=subprocess.PIPE,
                      stderr=subprocess.PIPE,
                      universal_newlines=True,
                      env=os.environ)]
        self.popen_mock.assert_has_calls(calls)

    def test_link_validation(self):
        test_data = """
A link that should work: [Mechanical Markdown](https://github.com/dapr/mechanical-markdown)

Relative links not currently supported: [Relative Link](examples/README.md)

"""
        self.prep_command_ouput("test", "", 0)
        mm = MechanicalMarkdown(test_data)
        success, report = mm.exectute_steps(False, validate_links=True)
        self.assertTrue(success)
        expected_report = f"""
External link validation:
\thttps://github.com/dapr/mechanical-markdown Status: {colored('200', 'green')}
"""
        self.assertEqual(expected_report, report)

    def test_link_validation_fails_for_broken_link(self):
        test_data = """
A link that should not work: [Mechanical Markdown](https://github.com/dapr/mechanical-markdown/a_bad_link)
A request to a non-existant host: [Mechanical Markdown](https://0.0.0.0/a_bad_link)
"""
        self.prep_command_ouput("test", "", 0)
        mm = MechanicalMarkdown(test_data)
        success, report = mm.exectute_steps(False, validate_links=True)
        self.assertFalse(success)
        expected_report = f"""
External link validation:
\thttps://github.com/dapr/mechanical-markdown/a_bad_link Status: {colored('404', 'red')}
\thttps://0.0.0.0/a_bad_link Status: {colored('Connection Failed', 'red')}
"""
        self.assertEqual(expected_report, report)

    def test_link_validation_ignores_links_marked_ignore(self):
        test_data = """
A link that should work: [Mechanical Markdown](https://github.com/dapr/mechanical-markdown)

<!-- IGNORE_LINKS -->

This link should be ignored: [Mechanical Markdown](https://0.0.0.0/a_bad_link)

<!-- END_IGNORE -->

"""
        self.prep_command_ouput("test", "", 0)
        mm = MechanicalMarkdown(test_data)
        success, report = mm.exectute_steps(False, validate_links=True)
        self.assertTrue(success)
        expected_report = f"""
External link validation:
\thttps://github.com/dapr/mechanical-markdown Status: {colored('200', 'green')}
\thttps://0.0.0.0/a_bad_link Status: {colored('Ignored', 'yellow')}
"""
        self.assertEqual(expected_report, report)
