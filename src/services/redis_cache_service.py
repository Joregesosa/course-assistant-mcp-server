import os
import json
import time
import redis
import logging
from typing import Any, Optional


class StudentCache:
    """
    A class to manage caching of student course information using Azure Cache for Redis.
    Configured to work exclusively with the 'courses' data type.
    """

    # Module-level Redis client to reuse the connection pool across instances.
    _redis_client: Optional[redis.StrictRedis] = None

    def __init__(self, expiration_time: int = 1800):
        """
        Initialize the StudentCache with a Redis client and expiration time.

        Args:
            expiration_time: The time in seconds for which the data should be cached (default 30 min).
        """
        self.key_prefix = "Pathway_digitalOperations-courseassistant_functions"
        self.expiration_time = expiration_time
        self.data_type = "courses"

        # Initialize shared client once to reduce latency on cold connects
        if StudentCache._redis_client is None:
            try:
                StudentCache._redis_client = redis.StrictRedis(
                    host=os.environ.get("AzureForRedisHost"),
                    port=int(os.environ.get("AzureForRedisPort", 6380)),
                    password=os.environ.get("AzureForRedisPassword"),
                    decode_responses=True,
                    ssl=True,
                    socket_connect_timeout=2,
                    socket_timeout=5,
                    health_check_interval=30,
                )
            except Exception as e:
                logging.error(f"Failed to initialize shared Redis client: {e}")
                StudentCache._redis_client = None

        self.redis_client = StudentCache._redis_client

    def _build_key(self, user_id: str) -> str:
        """
        Generate a Redis key for storing student course data.

        Args:
            user_id: The user's unique identifier.
        Returns:
            A string representing the Redis key.
        """
        return f"{self.key_prefix}:{user_id}:{self.data_type}"

    def set(self, user_id: str, data: Any) -> bool:
        """
        Set student course data in Redis with an expiration time.

        Args:
            user_id: The user's unique identifier.
            data: The data to be stored, which will be serialized to JSON.
        Returns:
            True if the operation was successful, False otherwise.
        """
        key = self._build_key(user_id)
        try:
            start_time = time.time()
            # Using set with 'ex' parameter for atomic set-and-expire operation
            result = self.redis_client.set(
                key, json.dumps(data), ex=self.expiration_time
            )

            elapsed = time.time() - start_time
            logging.debug(f"[PERFORMANCE] Redis SET for {user_id} took {elapsed:.3f}s")
            return bool(result)
        except redis.RedisError as e:
            logging.error(f"Error setting data in Redis for user {user_id}: {e}")
            return False

    def get(self, user_id: str) -> Optional[Any]:
        """
        Get student course data from Redis.

        Args:
            user_id: The user's unique identifier.
        Returns:
            The data retrieved from Redis, deserialized from JSON. Returns None if the key does not exist.
        """
        key = self._build_key(user_id)
        try:
            start_time = time.time()
            data = self.redis_client.get(key)

            elapsed = time.time() - start_time
            logging.debug(f"[PERFORMANCE] Redis GET for {user_id} took {elapsed:.3f}s")

            if data:
                return json.loads(data)
        except (redis.RedisError, json.JSONDecodeError) as e:
            logging.error(
                f"Error getting or decoding data from Redis for user {user_id}: {e}"
            )
        return None

    def exists(self, user_id: str) -> bool:
        """
        Check if the course data for a specific user exists in Redis.

        Args:
            user_id: The user's unique identifier.
        Returns:
            True if the data exists (not expired), False otherwise.
        """
        key = self._build_key(user_id)
        try:
            start_time = time.time()
            # exists returns the number of keys found
            exists = self.redis_client.exists(key)
            result = bool(exists)

            elapsed = time.time() - start_time
            logging.debug(
                f"[PERFORMANCE] Redis EXISTS check for {user_id} took {elapsed:.3f}s"
            )
            return result
        except redis.RedisError as e:
            logging.error(
                f"Error checking key existence in Redis for user {user_id}: {e}"
            )
            return False
