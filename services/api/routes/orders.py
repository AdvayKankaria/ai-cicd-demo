from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from services.api.database import get_db
from services.api.schemas.order import OrderCreate, OrderStatusUpdate, OrderResponse
from services.api.services.order_service import (
    create_order_service,
    update_order_status,
)
from services.api.models.order import Order

router = APIRouter()


@router.post("/", response_model=OrderResponse)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    return create_order_service(db, order)


@router.get("/", response_model=list[OrderResponse])
def get_orders(db: Session = Depends(get_db)):
    return db.query(Order).all()


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.put("/{order_id}/status", response_model=OrderResponse)
def update_status(
    order_id: int, status_update: OrderStatusUpdate, db: Session = Depends(get_db)
):
    return update_order_status(db, order_id, status_update.status)
