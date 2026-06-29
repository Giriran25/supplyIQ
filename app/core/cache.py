from cachetools import TTLCache

# Application-wide caches
# 5 minutes TTL for analytics and dashboards to keep it lightweight but responsive
analytics_cache = TTLCache(maxsize=500, ttl=300)
resilience_cache = TTLCache(maxsize=100, ttl=300)
simulation_cache = TTLCache(maxsize=100, ttl=300)
