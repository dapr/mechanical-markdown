
"""
Copyright (c) Microsoft Corporation.
Licensed under the MIT License.
"""

import os
import subprocess
import unittest

from mechanical_markdown import MechanicalMarkdown, MarkdownAnnotationError
from unittest.mock import patch, MagicMock, call

DEFAULT_TIMEOUT = 300


class MechanicalMarkdownTests(unittest.TestCase):
    def setUp(self):
        self.command_outputs = []

        self.process_mock = MagicMock()

        def pop_command(timeout=None):
            stdout, stderr, return_code = self.command_outputs.pop(0)
            self.process_mock.returncode = return_code
            return (stdout, stderr)

        self.process_mock.communicate.side_effect = pop_command

        self.popen_mock = MagicMock()
        self.popen_mock.return_value = self.process_mock

        self.patcher = patch('mechanical_markdown.command.Popen', self.popen_mock)
        self.patcher.start()

    def prep_command_output(self, stdout, stderr, return_code):
        self.command_outputs.append((stdout, stderr, return_code))

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
        self.prep_command_output("test", "", 0)
        mm = MechanicalMarkdown(test_data)
        success, report = mm.execute_steps(False)
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
        self.prep_command_output("test", "", 0)
        mm = MechanicalMarkdown(test_data)
        success, report = mm.execute_steps(False)
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
        self.prep_command_output("test", "", 0)
        mm = MechanicalMarkdown(test_data)
        success, report = mm.execute_steps(False)
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
        self.prep_command_output("test", "", 0)
        mm = MechanicalMarkdown(test_data)
        success, report = mm.execute_steps(False)
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
        self.prep_command_output("test", "", 0)
        mm = MechanicalMarkdown(test_data)
        success = mm.all_steps[0].run_all_commands(False)
        self.assertTrue(success)
        success = mm.all_steps[0].wait_for_all_background_commands()
        self.assertTrue(success)
        self.popen_mock.assert_called_with(['bash', '-c', 'echo "test"'],
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE,
                                           universal_newlines=True,
                                           env=os.environ)

        self.process_mock.communicate.assert_called_with(timeout=DEFAULT_TIMEOUT)

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
        self.prep_command_output("test", "", 1)
        mm = MechanicalMarkdown(test_data)
        success = mm.all_steps[0].run_all_commands(False)
        self.assertTrue(success)
        success = mm.all_steps[0].wait_for_all_background_commands()
        self.assertFalse(success)
        self.popen_mock.assert_called_with(['bash', '-c', 'echo "test"'],
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE,
                                           universal_newlines=True,
                                           env=os.environ)

        self.process_mock.communicate.assert_called_with(timeout=DEFAULT_TIMEOUT)

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

<!-- STEP
name: should not be executed
background: true
-->

We had a bug where we were calling join() on threads that never actually got executed. This test tickles that bug.

```bash
echo "This should not be executed"
```

<!-- END_STEP -->

"""
        self.prep_command_output("test", "", 1)
        self.prep_command_output("test2", "", 0)
        mm = MechanicalMarkdown(test_data)
        success, report = mm.execute_steps(False)
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
        self.prep_command_output("test", "", 0)
        mm = MechanicalMarkdown(test_data)
        success, report = mm.execute_steps(False)
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
        self.prep_command_output("test\ntest2", "error", 0)
        mm = MechanicalMarkdown(test_data)
        success, report = mm.execute_steps(False)
        self.assertTrue(success)
        calls = [call(['bash', '-c', 'echo "test"\necho "test2"\necho "error" 1>&2'],
                      stdout=subprocess.PIPE,
                      stderr=subprocess.PIPE,
                      universal_newlines=True,
                      env=os.environ),
                 call().communicate(timeout=DEFAULT_TIMEOUT)]
        self.popen_mock.assert_has_calls(calls)

    def test_expected_lines_succeed_when_matched_substr(self):
        test_data = """
<!-- STEP
name: basic test
output_match_mode: substring
expected_stdout_lines:
  - substring
expected_stderr_lines:
-->

```bash
echo "Match a substring"
```

<!-- END_STEP -->
"""
        self.prep_command_output("Match a substring", "", 0)
        mm = MechanicalMarkdown(test_data)
        success, report = mm.execute_steps(False)
        self.assertTrue(success)
        calls = [call(['bash', '-c', 'echo "Match a substring"'],
                      stdout=subprocess.PIPE,
                      stderr=subprocess.PIPE,
                      universal_newlines=True,
                      env=os.environ),
                 call().communicate(timeout=DEFAULT_TIMEOUT)]
        self.popen_mock.assert_has_calls(calls)

    def test_expected_lines_succeed_when_matched_order(self):
        test_data = """
<!-- STEP
    name: match order {0} test
    match_order: {0}
    expected_stdout_lines:
    - 'line 1'
    - 'line 2'
-->

```bash
echo "line 2"
echo "line 1"
```

<!-- END_STEP -->
    """
        for match_order in ("sequential", "none"):
            self.prep_command_output("line 2\nline 1", "", 0)
            mm = MechanicalMarkdown(test_data.format(match_order))
            success, _ = mm.execute_steps(False)
            if match_order == "sequential":
                self.assertFalse(success, "sequential match order should fail")
            else:
                self.assertTrue(success, "none match order should succeed")
            calls = [call(['bash', '-c', 'echo "line 2"\necho "line 1"'],
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                          universal_newlines=True,
                          env=os.environ),
                     call().communicate(timeout=DEFAULT_TIMEOUT)]
            self.popen_mock.assert_has_calls(calls)

    def test_exception_raised_for_invalid_match_order(self):
        test_data = """
<!-- STEP
name: basic test
match_order: foo
-->

<!-- END_STEP -->
"""

        with self.assertRaises(MarkdownAnnotationError):
            MechanicalMarkdown(test_data)

    def test_exception_raised_for_invalid_match_mode(self):
        test_data = """
<!-- STEP
name: basic test
output_match_mode: foo
-->

<!-- END_STEP -->
"""

        with self.assertRaises(MarkdownAnnotationError):
            MechanicalMarkdown(test_data)

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
        self.prep_command_output("test", "", 0)
        mm = MechanicalMarkdown(test_data)
        success, report = mm.execute_steps(False)
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
        self.prep_command_output("test", "", 0)
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

        def raise_timeout(timeout=DEFAULT_TIMEOUT):
            raise subprocess.TimeoutExpired("foo", 60.0)

        self.process_mock.communicate.side_effect = raise_timeout
        self.prep_command_output("test", "", 0)
        mm = MechanicalMarkdown(test_data)
        success, report = mm.execute_steps(False)
        self.assertFalse(success)
        self.popen_mock.assert_called_with(['bash', '-c', 'echo "test"'],
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE,
                                           universal_newlines=True,
                                           env=os.environ)
        self.process_mock.terminate.assert_called()
        self.process_mock.kill.assert_called()
        self.process_mock.communicate.assert_has_calls([call(timeout=DEFAULT_TIMEOUT), call(timeout=DEFAULT_TIMEOUT)])

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

        self.prep_command_output("test", "", 0)
        input_mock.return_value = 'x'
        mm = MechanicalMarkdown(test_data)
        success, report = mm.execute_steps(True)
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
        self.prep_command_output("test", "", 0)
        mm = MechanicalMarkdown(test_data, shell='cmd /c')
        success, report = mm.execute_steps(False)
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

    def test_missmatched_start_and_end_tags_throws_exception(self):
        test_data = """
<!-- STEP
name: basic test
-->

```bash
echo "test"
```

<!-- STEP
name: another basic test
-->

```bash
echo "another test"
```

<!-- END_STEP -->

"""
        with self.assertRaises(MarkdownAnnotationError):
            MechanicalMarkdown(test_data)

        test_data = """
<!-- IGNORE_LINKS -->

<!-- IGNORE_LINKS -->

<!-- END_IGNORE -->

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
        self.prep_command_output("test", "", 1)
        self.prep_command_output("test", "", 15)
        mm = MechanicalMarkdown(test_data)
        success, report = mm.execute_steps(False)
        self.assertTrue(success)
        calls = [call(['bash', '-c', 'exit 1'],
                      stdout=subprocess.PIPE,
                      stderr=subprocess.PIPE,
                      universal_newlines=True,
                      env=os.environ),
                 call().communicate(timeout=DEFAULT_TIMEOUT),
                 call(['bash', '-c', 'exit 15'],
                      stdout=subprocess.PIPE,
                      stderr=subprocess.PIPE,
                      universal_newlines=True,
                      env=os.environ)]
        self.popen_mock.assert_has_calls(calls)

    def test_steps_with_no_matching_tags_are_skipped(self):
        test_data = """
<!-- STEP
name: foo bar
tags:
  - foo
  - bar
-->

```bash
echo tag foo
echo tag bar
```

<!-- END_STEP -->

<!-- STEP
name: tag match
tags:
  - blag
-->

```bash
echo blag
```

<!-- END_STEP -->
"""
        self.prep_command_output("blag", "", 0)
        mm = MechanicalMarkdown(test_data)
        success, report = mm.execute_steps(False, tags=("blag",))
        self.assertTrue(success, report)
        calls = [call(['bash', '-c', 'echo blag'],
                      stdout=subprocess.PIPE,
                      stderr=subprocess.PIPE,
                      universal_newlines=True,
                      env=os.environ),
                 call().communicate(timeout=DEFAULT_TIMEOUT)]
        self.popen_mock.assert_has_calls(calls)

    def test_all_steps_with_matching_tags_are_executed(self):
        test_data = """
<!-- STEP
name: foo bar
tags:
  - foo
  - bar
-->

```bash
echo tag foo
echo tag bar
```

<!-- END_STEP -->

<!-- STEP
name: foo2
tags:
  - foo
-->

```bash
echo foo2
```

<!-- END_STEP -->
"""
        self.prep_command_output("tag foo\ntag bar", "", 0)
        self.prep_command_output("foo2", "", 0)
        mm = MechanicalMarkdown(test_data)
        success, report = mm.execute_steps(False)
        self.assertTrue(success)
        calls = [call(['bash', '-c', 'echo tag foo\necho tag bar'],
                      stdout=subprocess.PIPE,
                      stderr=subprocess.PIPE,
                      universal_newlines=True,
                      env=os.environ),
                 call().communicate(timeout=DEFAULT_TIMEOUT),
                 call(['bash', '-c', 'echo foo2'],
                      stdout=subprocess.PIPE,
                      stderr=subprocess.PIPE,
                      universal_newlines=True,
                      env=os.environ)]
        self.popen_mock.assert_has_calls(calls)
