from fastapi import FastAPI
from services.api.routes import health, products, orders, users
from services.api.config import settings

app = FastAPI(title="Order Management Platform", version=settings.APP_VERSION)

app.include_router(health.router)
app.include_router(products.router, prefix="/products", tags=["products"])
app.include_router(orders.router, prefix="/orders", tags=["orders"])
app.include_router(users.router, prefix="/users", tags=["users"])


@app.get("/metrics-demo")
def metrics_demo():
    return {"status": "ok", "error_rate": "0.2%", "p95": "150ms"}
