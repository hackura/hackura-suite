import unittest
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.wrapper import ToolWrapper
from core.web_fuzzer import WebFuzzer
from core.cloud_audit import CloudAuditor
from core.exfiltrator import Exfiltrator
from core.reporting import ReportGenerator

class TestHackuraSuite(unittest.TestCase):
    def test_tool_wrapper_detection(self):
        # Nmap is expected on most systems for this test
        wrapper = ToolWrapper("ls") # 'ls' is guaranteed on linux
        self.assertTrue(wrapper.is_available())

    def test_web_fuzzer_logic(self):
        # We won't run a real network request here to keep it fast
        fuzzer = WebFuzzer("https://example.com", ["test"])
        self.assertEqual(fuzzer.base_url, "https://example.com")

    def test_reporting_generation(self):
        output_dir = "test_reports"
        gen = ReportGenerator(output_dir)
        findings = [{"title": "Test Finding", "severity": "High", "description": "Demo"}]
        path = gen.generate("Test Client", "Unit Test", findings)
        self.assertTrue(os.path.exists(path))
        # Cleanup
        os.remove(path)
        os.rmdir(output_dir)

if __name__ == "__main__":
    unittest.main()
