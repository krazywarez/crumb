import json
import os
import tempfile
import unittest
from unittest.mock import patch

from server import app


class TestServer(unittest.TestCase):
    """The POST handler appends to LOG_PATH, which defaults to the developer's
    own ~/.crumb/history.org. Every test here patches it at a temporary file:
    without that, running the suite writes into real browsing history."""

    def setUp(self):
        self.client = app.test_client()
        handle, self.log_path = tempfile.mkstemp(suffix=".org")
        os.close(handle)

    def tearDown(self):
        os.unlink(self.log_path)

    def test_log_visit_post_writes_an_entry(self):
        data = {
            "title": "Test Visit",
            "url": "https://test.com",
            "hostname": "test.com",
            "path": "/",
            "query": "test",
            "tabId": 123,
            "windowId": 456,
            "favIconUrl": "https://example.com/favicon.ico",
        }

        # json=, not data=: with data= Flask sends it form-encoded regardless of
        # content_type, request.json comes back empty and the handler 400s.
        with patch("server.LOG_PATH", self.log_path):
            response = self.client.post("/", json=data)

        self.assertEqual(response.status_code, 204)

        with open(self.log_path) as f:
            written = f.read()
        self.assertIn("* Test Visit", written)
        self.assertIn(":URL:       https://test.com", written)
        self.assertIn(":QUERY:     test", written)
        self.assertIn(":END:", written)

    def test_optional_fields_are_omitted_when_empty(self):
        with patch("server.LOG_PATH", self.log_path):
            response = self.client.post("/", json={"title": "Bare", "url": "https://x"})

        self.assertEqual(response.status_code, 204)
        with open(self.log_path) as f:
            written = f.read()
        self.assertNotIn(":QUERY:", written)
        self.assertNotIn(":FAVICON:", written)

    def test_log_visit_options(self):
        response = self.client.options("/")
        self.assertEqual(response.status_code, 204)

    def test_cors_headers_are_present(self):
        response = self.client.options("/")
        self.assertEqual(response.headers["Access-Control-Allow-Origin"], "*")
        self.assertEqual(response.headers["Access-Control-Allow-Headers"], "Content-Type")
