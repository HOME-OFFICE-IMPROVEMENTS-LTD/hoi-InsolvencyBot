"""
Security utilities for InsolvencyBot API.

This module provides security utilities for the InsolvencyBot API,
including authentication, rate limiting, and other security features.
"""

import hashlib
import hmac
import os
import time
import secrets
from typing import Dict, Optional, Tuple, Union
from fastapi import Request, HTTPException, status

from src.hoi_insolvencybot.config import config
from src.hoi_insolvencybot.logging_config import get_logger

# Initialize logger
logger = get_logger(__name__)

class TokenBucket:
    """
    Simple token bucket rate limiter.
    
    This implements a token bucket algorithm for rate limiting API requests.
    """
    
    def __init__(self, tokens: int, refill_time: float):
        """
        Initialize the token bucket.
        
        Args:
            tokens: Maximum number of tokens in the bucket (max requests)
            refill_time: Time in seconds to refill one token
        """
        self.tokens = tokens
        self.max_tokens = tokens
        self.refill_time = refill_time
        self.last_check = time.time()
    
    def consume(self, tokens: int = 1) -> bool:
        """
        Consume tokens from the bucket.
        
        Args:
            tokens: Number of tokens to consume
            
        Returns:
            bool: True if tokens were consumed, False if not enough tokens
        """
        now = time.time()
        
        # Calculate how many tokens to add based on elapsed time
        elapsed = now - self.last_check
        self.tokens = min(self.max_tokens, self.tokens + elapsed / self.refill_time)
        self.last_check = now
        
        # Check if we have enough tokens
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False


class RateLimiter:
    """
    Rate limiter for the API.
    
    This implements per-client rate limiting based on IP address or API key.
    """
    
    def __init__(self, 
                requests_per_minute: int = 60, 
                requests_per_hour: int = 1000,
                requests_per_day: int = 10000):
        """
        Initialize the rate limiter.
        
        Args:
            requests_per_minute: Maximum requests per minute
            requests_per_hour: Maximum requests per hour
            requests_per_day: Maximum requests per day
        """
        self.per_minute = requests_per_minute
        self.per_hour = requests_per_hour
        self.per_day = requests_per_day
        
        # Token buckets for each client and time window
        self.minute_buckets: Dict[str, TokenBucket] = {}
        self.hour_buckets: Dict[str, TokenBucket] = {}
        self.day_buckets: Dict[str, TokenBucket] = {}
    
    def _get_client_id(self, request: Request) -> str:
        """
        Get a unique ID for the client.
        
        Uses API key if available, otherwise IP address.
        
        Args:
            request: The FastAPI request object
            
        Returns:
            str: A unique identifier for the client
        """
        # Use API key if available
        api_key = request.headers.get("api-key")
        if api_key:
            return hashlib.sha256(api_key.encode()).hexdigest()
        
        # Fall back to IP address
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            # Get the first IP in the forwarded chain (client IP)
            client_ip = forwarded.split(",")[0].strip()
        else:
            client_ip = request.client.host
        
        return client_ip
    
    def check_rate_limit(self, request: Request) -> bool:
        """
        Check if a request should be rate limited.
        
        Args:
            request: The FastAPI request object
            
        Returns:
            bool: True if request is allowed, False if rate limited
        """
        # Skip rate limiting for local development
        if config.debug_mode and request.client.host in ("127.0.0.1", "localhost"):
            return True
        
        client_id = self._get_client_id(request)
        
        # Check minute limit
        if client_id not in self.minute_buckets:
            self.minute_buckets[client_id] = TokenBucket(
                tokens=self.per_minute,
                refill_time=60.0 / self.per_minute
            )
        
        if not self.minute_buckets[client_id].consume():
            return False
        
        # Check hour limit
        if client_id not in self.hour_buckets:
            self.hour_buckets[client_id] = TokenBucket(
                tokens=self.per_hour,
                refill_time=3600.0 / self.per_hour
            )
        
        if not self.hour_buckets[client_id].consume():
            return False
        
        # Check day limit
        if client_id not in self.day_buckets:
            self.day_buckets[client_id] = TokenBucket(
                tokens=self.per_day,
                refill_time=86400.0 / self.per_day
            )
        
        return self.day_buckets[client_id].consume()


def generate_api_key() -> str:
    """
    Generate a secure API key.
    
    Returns:
        str: A secure random API key
    """
    return secrets.token_urlsafe(32)


def verify_hmac_signature(data: str, signature: str, secret: str) -> bool:
    """
    Verify an HMAC signature for webhook authentication.
    
    Args:
        data: The data that was signed
        signature: The signature to verify
        secret: The secret key used for signing
        
    Returns:
        bool: True if signature is valid, False otherwise
    """
    computed_signature = hmac.new(
        secret.encode(),
        data.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(computed_signature, signature)


# Create a global rate limiter
rate_limiter = RateLimiter()
