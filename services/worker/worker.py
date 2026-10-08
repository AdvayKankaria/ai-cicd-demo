import time
import json
import logging
from services.api.database import get_redis, SessionLocal
from services.api.models.order import Order
from services.api.models.user import User  # noqa: F401
from services.api.models.product import Product  # noqa: F401
from services.api.models.order_item import OrderItem  # noqa: F401

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def process_order(order_id: int):
    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if order and order.status == "PENDING":
            logger.info(f"Processing order {order_id}")
            time.sleep(1)  # simulate work
            order.status = "COMPLETED"
            db.commit()
            logger.info(f"Order {order_id} completed")
    except Exception as e:
        logger.error(f"Error processing order {order_id}: {e}")
    finally:
        db.close()


def main():
    logger.info("Starting worker...")
    while True:
        try:
            redis_client = get_redis()
            job = redis_client.brpop("order_queue", timeout=5)
            if job:
                _, data = job
                job_data = json.loads(data)
                process_order(job_data.get("order_id"))
        except Exception as e:
            logger.error(f"Redis connection error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()
