import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

import search
from search import search_log


class TestSearchLog(unittest.TestCase):
    """search_log prints matches; it does not modify the log. The previous tests
    read the file back and asserted on its contents, which could only ever pass
    for the match case and never for the no-match one."""

    ENTRY = (
        "* Example Entry\n"
        ":PROPERTIES:\n"
        ":URL:       http://example.com\n"
        ":TIMESTAMP: 2023-10-27 10:00:00\n"
        ":END:\n\n"
    )

    def setUp(self):
        handle, self.log_path = tempfile.mkstemp(suffix=".org")
        os.close(handle)
        with open(self.log_path, "w") as f:
            f.write(self.ENTRY)

    def tearDown(self):
        os.unlink(self.log_path)

    def run_search(self, query):
        out = io.StringIO()
        with patch.object(search, "LOG_PATH", self.log_path), redirect_stdout(out):
            search_log(query)
        return out.getvalue()

    def test_a_match_is_printed(self):
        self.assertIn("Example Entry", self.run_search("example"))

    def test_the_search_is_case_insensitive(self):
        self.assertIn("Example Entry", self.run_search("EXAMPLE"))

    def test_a_property_value_matches(self):
        self.assertIn("Example Entry", self.run_search("example.com"))

    def test_no_match_prints_no_entry(self):
        self.assertNotIn("Example Entry", self.run_search("nonexistent"))

    def test_a_missing_log_is_reported_not_raised(self):
        out = io.StringIO()
        with patch.object(search, "LOG_PATH", self.log_path + ".absent"), redirect_stdout(out):
            search_log("anything")
        self.assertIn("No history file found.", out.getvalue())
