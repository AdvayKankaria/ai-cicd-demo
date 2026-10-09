import json

from fastapi import HTTPException
from sqlalchemy.orm import Session

from services.api.config import settings
from services.api.database import get_redis
from services.api.models.order import Order
from services.api.models.order_item import OrderItem
from services.api.models.product import Product
from services.api.schemas.order import OrderCreate


def create_order_service(
    db: Session, order_data: OrderCreate, idempotency_key: str | None = None
):
    if idempotency_key:
        existing = db.query(Order).filter(Order.idempotency_key == idempotency_key).first()
        if existing:
            return existing

    total_amount = 0.0
    items = []

    for item in order_data.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(
                status_code=404, detail=f"Product {item.product_id} not found"
            )

        # DELIBERATE BUG: "bad demo version" requested by prompt
        # correct: product.price * item.quantity
        if settings.SIMULATE_FAILURE and settings.FAILURE_SCENARIO == "test_failure":
            item_total = product.price + item.quantity
        else:
            item_total = product.price * item.quantity

        total_amount += item_total

        db_item = OrderItem(
            product_id=item.product_id, quantity=item.quantity, price=product.price
        )
        items.append(db_item)

    db_order = Order(
        user_id=order_data.user_id,
        status="PENDING",
        total_amount=total_amount,
        idempotency_key=idempotency_key,
    )
    db.add(db_order)
    db.flush()  # get id

    for db_item in items:
        db_item.order_id = db_order.id
        db.add(db_item)

    db.commit()
    db.refresh(db_order)

    # Queue job for worker
    try:
        redis_client = get_redis()
        job_data = {"order_id": db_order.id}
        redis_client.lpush("order_queue", json.dumps(job_data))
    except Exception as e:  # noqa: BLE001
        import logging

        logging.getLogger(__name__).warning(
            f"Redis queue error: {e}"
        )  # fail gracefully for demo

    return db_order


def update_order_status(db: Session, order_id: int, status: str):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = status
    db.commit()
    db.refresh(order)
    return order