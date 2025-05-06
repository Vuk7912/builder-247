import time
import pytest
from prometheus_swarm.security.replay_attack_logger import ReplayAttackLogger

def test_replay_attack_logger_basic():
    """Test basic replay attack detection functionality."""
    logger = ReplayAttackLogger(max_cache_size=100, cache_expiry_seconds=3600)
    
    # First request should return False (not a replay)
    request1 = {"user_id": 123, "action": "login"}
    assert not logger.is_replay_request(request1)
    
    # Same request again should return True (replay)
    assert logger.is_replay_request(request1)

def test_replay_attack_logger_different_requests():
    """Test that different requests are not considered replays."""
    logger = ReplayAttackLogger(max_cache_size=100, cache_expiry_seconds=3600)
    
    request1 = {"user_id": 123, "action": "login"}
    request2 = {"user_id": 456, "action": "login"}
    
    assert not logger.is_replay_request(request1)
    assert not logger.is_replay_request(request2)
    
    # Ensure the second request is not considered a replay
    assert logger.is_replay_request(request1)
    assert logger.is_replay_request(request2)

def test_replay_attack_logger_cache_expiry():
    """Test that requests expire from the cache."""
    logger = ReplayAttackLogger(max_cache_size=100, cache_expiry_seconds=1)
    
    request = {"user_id": 123, "action": "login"}
    
    assert not logger.is_replay_request(request)
    
    # Wait for cache to expire
    time.sleep(1.1)
    
    # After expiry, the request should no longer be considered a replay
    assert not logger.is_replay_request(request)

def test_replay_attack_logger_max_cache_size():
    """Test that the logger maintains a maximum cache size."""
    max_size = 5
    logger = ReplayAttackLogger(max_cache_size=max_size, cache_expiry_seconds=3600)
    
    # First, add max_size unique requests
    for i in range(max_size):
        request = {"user_id": i, "action": "login"}
        assert not logger.is_replay_request(request)
    
    # Add more requests to exceed cache size
    for i in range(max_size, max_size * 2):
        request = {"user_id": i, "action": "login"}
        assert not logger.is_replay_request(request)
    
    # Verify that only the last max_size requests are cached
    for i in range(max_size):
        request = {"user_id": i, "action": "login"}
        assert not logger.is_replay_request(request)  # These are now too old
    
    for i in range(max_size, max_size * 2):
        request = {"user_id": i, "action": "login"}
        assert logger.is_replay_request(request)  # These are cached

def test_replay_attack_logger_request_order_invariance():
    """Test that request order does not affect replay detection."""
    logger = ReplayAttackLogger(max_cache_size=100, cache_expiry_seconds=3600)
    
    request1 = {"a": 1, "b": 2}
    request2 = {"b": 2, "a": 1}
    
    # First occurrence should not be a replay
    assert not logger.is_replay_request(request1)
    assert logger.is_replay_request(request1)
    
    # Even though keys are in a different order, it should still be considered a replay
    assert logger.is_replay_request(request2)

def test_replay_attack_logger_complex_data():
    """Test replay detection with complex request data."""
    logger = ReplayAttackLogger(max_cache_size=100, cache_expiry_seconds=3600)
    
    complex_request = {
        "user": {
            "id": 123,
            "name": "John Doe"
        },
        "action": "purchase",
        "items": [
            {"id": 1, "name": "Product A"},
            {"id": 2, "name": "Product B"}
        ]
    }
    
    assert not logger.is_replay_request(complex_request)
    assert logger.is_replay_request(complex_request)