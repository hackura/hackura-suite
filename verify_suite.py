import unittest
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.wrapper import ToolWrapper
from core.web_fuzzer import WebFuzzer
from core.cloud_audit import CloudAuditor
from core.exfiltrator import Exfiltrator
from core.report_engine import report_engine

class TestHackuraSuite(unittest.TestCase):
    def test_tool_wrapper_detection(self):
        # ls is guaranteed on linux
        wrapper = ToolWrapper("ls")
        self.assertTrue(wrapper.is_available())

    def test_web_fuzzer_logic(self):
        fuzzer = WebFuzzer("https://example.com", ["test"])
        self.assertEqual(fuzzer.base_url, "https://example.com")

    def test_report_engine_availability(self):
        self.assertIsNotNone(report_engine)

if __name__ == "__main__":
    unittest.main()
