import json
from services.api.database import get_redis


def get_cached_products():
    try:
        redis_client = get_redis()
        cached = redis_client.get("products")
        if cached:
            return json.loads(cached)
    except Exception as e:
        import logging

        logging.getLogger(__name__).warning(f"Cache get error: {e}")
    return None


def set_cached_products(products_data):
    try:
        redis_client = get_redis()
        if products_data is None:
            redis_client.delete("products")
        else:
            redis_client.set("products", json.dumps(products_data), ex=300)
    except Exception as e:
        import logging

        logging.getLogger(__name__).warning(f"Cache set error: {e}")
