import time
from typing import Dict, Any, Optional, List
from hashlib import sha256
from collections import OrderedDict

class ReplayAttackLogger:
    """
    A service to detect and log potential replay attacks by tracking request signatures.
    
    Replay attacks occur when a valid data transmission is maliciously repeated or delayed.
    This logger helps prevent such attacks by tracking request uniqueness.
    """
    
    def __init__(self, max_cache_size: int = 1000, cache_expiry_seconds: int = 3600):
        """
        Initialize the Replay Attack Logger.
        
        Args:
            max_cache_size (int): Maximum number of request signatures to cache. 
                Defaults to 1000.
            cache_expiry_seconds (int): Time in seconds before a signature expires. 
                Defaults to 1 hour (3600 seconds).
        """
        self._request_timestamps: Dict[str, float] = {}
        self._max_cache_size = max_cache_size
        self._cache_expiry_seconds = cache_expiry_seconds
    
    def _generate_signature(self, request_data: Dict[Any, Any]) -> str:
        """
        Generate a unique signature for a request.
        
        Args:
            request_data (Dict[Any, Any]): The request data to generate a signature for.
        
        Returns:
            str: A SHA-256 hash of the sorted request data.
        """
        # Convert request_data to a sorted, hashable representation
        sorted_data = str(sorted(request_data.items()))
        return sha256(sorted_data.encode()).hexdigest()
    
    def is_replay_request(self, request_data: Dict[Any, Any]) -> bool:
        """
        Check if a request is a potential replay attack.
        
        Args:
            request_data (Dict[Any, Any]): The request data to check.
        
        Returns:
            bool: True if the request appears to be a replay, False otherwise.
        """
        current_time = time.time()
        
        # Clean expired entries
        self._clean_expired_timestamps(current_time)
        
        # Generate signature for the request
        signature = self._generate_signature(request_data)
        
        # Check if signature exists in cache
        if signature in self._request_timestamps:
            return True
        
        # Add new signature to cache
        self._add_signature(signature, current_time)
        return False
    
    def _clean_expired_timestamps(self, current_time: float):
        """
        Remove expired signatures from the cache.
        
        Args:
            current_time (float): Current timestamp.
        """
        expired_signatures = [
            sig for sig, timestamp in list(self._request_timestamps.items())
            if current_time - timestamp >= self._cache_expiry_seconds
        ]
        
        for sig in expired_signatures:
            del self._request_timestamps[sig]
    
    def _add_signature(self, signature: str, timestamp: float):
        """
        Add a signature to the cache, managing maximum cache size.
        
        Args:
            signature (str): Request signature.
            timestamp (float): Time of request.
        """
        # Remove oldest entries if cache is full
        while len(self._request_timestamps) >= self._max_cache_size:
            # Find and remove the oldest timestamp
            oldest_sig = min(
                self._request_timestamps, 
                key=lambda sig: self._request_timestamps[sig]
            )
            del self._request_timestamps[oldest_sig]
        
        # Add new signature
        self._request_timestamps[signature] = timestamp