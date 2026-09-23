import pytest
from unittest.mock import patch
from src.task7 import fetch_website_status, requests

@patch("src.task7.requests.get")
def test_fetch_website_status_success(mock_get):
    # Uses a mock status code so it doesn't actually go to the internet
    mock_get.return_value.status_code = 200
    
    status = fetch_website_status("https://example.com")
    
    assert status == 200
    mock_get.assert_called_once_with("https://example.com", timeout=5)

@patch("src.task7.requests.get")
def test_fetch_website_status_failure(mock_get):
    # Mock error
    mock_get.side_effect = requests.RequestException("Simulated Network Error")
    
    status = fetch_website_status("https://this-does-not-exist.com")
    
    assert status is None