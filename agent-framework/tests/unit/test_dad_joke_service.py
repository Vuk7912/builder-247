import pytest
import requests
from unittest.mock import patch
from prometheus_swarm.services.dad_joke_service import DadJokeService

class MockResponse:
    def __init__(self, json_data, status_code=200):
        self.json_data = json_data
        self.status_code = status_code
    
    def json(self):
        return self.json_data
    
    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP Error: {self.status_code}")

def test_get_random_joke_success():
    """Test successful retrieval of a random dad joke."""
    with patch('requests.get') as mock_get:
        mock_joke = {
            "id": "test_joke_id",
            "joke": "A hilarious dad joke"
        }
        mock_get.return_value = MockResponse(mock_joke)
        
        result = DadJokeService.get_random_joke()
        
        assert result['id'] == "test_joke_id"
        assert result['joke'] == "A hilarious dad joke"
        assert result['status'] == 200

def test_get_random_joke_network_error():
    """Test handling of network errors when fetching a random joke."""
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.RequestException("Network error")
        
        result = DadJokeService.get_random_joke()
        
        assert result['id'] == ""
        assert "Error fetching joke" in result['joke']
        assert result['status'] == 500

def test_get_joke_by_id_success():
    """Test successful retrieval of a joke by specific ID."""
    with patch('requests.get') as mock_get:
        mock_joke = {
            "id": "ABC123",
            "joke": "Another hilarious dad joke"
        }
        mock_get.return_value = MockResponse(mock_joke)
        
        result = DadJokeService.get_joke_by_id("ABC123")
        
        assert result['id'] == "ABC123"
        assert result['joke'] == "Another hilarious dad joke"
        assert result['status'] == 200

def test_get_joke_by_id_invalid_id():
    """Test handling of an empty joke ID."""
    result = DadJokeService.get_joke_by_id("")
    
    assert result['id'] == ""
    assert result['joke'] == "Invalid joke ID provided"
    assert result['status'] == 400

def test_get_joke_by_id_network_error():
    """Test handling of network errors when fetching a joke by ID."""
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.RequestException("Network error")
        
        result = DadJokeService.get_joke_by_id("ABC123")
        
        assert result['id'] == "ABC123"
        assert "Error fetching joke" in result['joke']
        assert result['status'] == 500