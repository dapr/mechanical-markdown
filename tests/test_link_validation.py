
"""
Copyright (c) Microsoft Corporation.
Licensed under the MIT License.
"""

import unittest

from mechanical_markdown import MechanicalMarkdown
from fake_http_server import FakeHttpServer
from termcolor import colored


class LinkValidationTests(unittest.TestCase):
    def setUp(self):
        self.command_ouputs = []
        self.server = FakeHttpServer()
        self.server.start()
        self.host_port = f'localhost:{self.server.get_port()}'

    def tearDown(self):
        self.server.shutdown_server()

    def test_link_validation(self):
        test_data = f"""
A link that should work: [Mechanical Markdown](http://{self.host_port}/dapr/mechanical-markdown)
A link that gives other valid status codes: [Mechanical Markdown](http://{self.host_port}/dapr/204)

Relative links not currently supported: [Relative Link](examples/README.md)

"""
        self.server.set_response_codes((200, 204))
        mm = MechanicalMarkdown(test_data)
        success, report = mm.exectute_steps(False, validate_links=True)
        self.assertTrue(success)
        expected_report = f"""
External link validation:
\thttp://{self.host_port}/dapr/mechanical-markdown Status: {colored('200', 'green')}
\thttp://{self.host_port}/dapr/204 Status: {colored('204', 'green')}
"""
        self.assertEqual(expected_report, report)

    def test_link_validation_fails_for_broken_link(self):
        test_data = f"""
A link that should not work: [Mechanical Markdown](http://{self.host_port}/dapr/mechanical-markdown/a_bad_link)
A request to a non-existant host: [Mechanical Markdown](https://0.0.0.0/a_bad_link)
"""
        mm = MechanicalMarkdown(test_data)
        self.server.set_response_codes((404, ))
        success, report = mm.exectute_steps(False, validate_links=True, link_retries=1)
        self.assertFalse(success)
        expected_report = f"""
External link validation:
\thttp://{self.host_port}/dapr/mechanical-markdown/a_bad_link Status: {colored('404', 'red')}
\thttps://0.0.0.0/a_bad_link Status: {colored('Connection Failed', 'red')}
"""
        self.assertEqual(expected_report, report)

    def test_link_validation_ignores_links_marked_ignore(self):
        test_data = f"""
A link that should work: [Mechanical Markdown](http://{self.host_port}/dapr/mechanical-markdown)

<!-- IGNORE_LINKS -->

This link should be ignored: [Mechanical Markdown](https://0.0.0.0/a_bad_link)

<!-- END_IGNORE -->

"""
        mm = MechanicalMarkdown(test_data)
        self.server.set_response_codes((200, ))
        success, report = mm.exectute_steps(False, validate_links=True)
        self.assertTrue(success)
        expected_report = f"""
External link validation:
\thttp://{self.host_port}/dapr/mechanical-markdown Status: {colored('200', 'green')}
\thttps://0.0.0.0/a_bad_link Status: {colored('Ignored', 'yellow')}
"""
        self.assertEqual(expected_report, report)

    def test_failed_links_are_retried(self):
        test_data = f"""
A flaky link: [Mechanical Markdown](http://{self.host_port}/dapr/mechanical-markdown)

"""
        mm = MechanicalMarkdown(test_data)
        self.server.set_response_codes((503, 503, 200))
        success, report = mm.exectute_steps(False, validate_links=True)
        self.assertTrue(success)
        expected_report = f"""
External link validation:
\thttp://{self.host_port}/dapr/mechanical-markdown Status: {colored('200', 'green')}
"""
        self.assertEqual(expected_report, report)
