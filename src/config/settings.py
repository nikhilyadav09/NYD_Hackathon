class DatabaseConfig:
    """Database configuration settings"""
    CONNECTION_PARAMS = {
        "dbname": "ancient_wisdom",
        "user": "postgres",
        "password": "Nikhil@930",
        "host": "localhost"
    }

class LLMConfig:
    """LLM configuration settings"""
    API_KEY1 = "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"
    API_KEY2 = "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"
    API_KEY3 = "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"
    MODEL_NAME = "llama-3.3-70b-versatile"
    MAX_TOKENS = 500
    TEMPERATURE = 0.7

class CacheConfig:
    ENABLE_CACHE = True
    CACHE_EXPIRY = 3600  # 1 hour