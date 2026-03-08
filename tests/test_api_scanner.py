import unittest
from unittest.mock import patch, MagicMock
from core.api_scanner import APIScanner
import os

class TestAPIScanner(unittest.TestCase):
    def setUp(self):
        self.scanner = APIScanner("https://api.example.com")

    @patch('requests.get')
    def test_discover_endpoints(self, mock_get):
        # Mocking responses for discovery
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        endpoints = self.scanner.discover_endpoints()
        self.assertGreater(len(endpoints), 0)
        self.assertIn("/api", endpoints)

    @patch('wrappers.ffuf_wrapper.FfufWrapper.is_available')
    @patch('wrappers.ffuf_wrapper.FfufWrapper.fuzz')
    def test_start_fuzzing(self, mock_fuzz, mock_available):
        mock_available.return_value = True
        mock_fuzz.return_value = MagicMock() # Mock process
        
        process = self.scanner.start_fuzzing("/api/v1", "wordlist.txt")
        self.assertIsNotNone(process)
        mock_fuzz.assert_called_once()

if __name__ == "__main__":
    unittest.main()
