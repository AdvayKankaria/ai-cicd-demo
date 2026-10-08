from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from services.api.database import get_db
from services.api.models.product import Product
from services.api.schemas.product import ProductCreate, ProductResponse
from services.api.services.cache_service import get_cached_products, set_cached_products

router = APIRouter()


@router.post("/", response_model=ProductResponse)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    # Invalidate cache
    set_cached_products(None)
    return db_product


@router.get("/", response_model=list[ProductResponse])
def get_products(db: Session = Depends(get_db)):
    cached = get_cached_products()
    if cached:
        return cached
    products = db.query(Product).all()
    set_cached_products([p.__dict__ for p in products])
    return products


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
