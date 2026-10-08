from services.api.services.order_service import create_order_service
from services.api.schemas.order import OrderCreate, OrderItemCreate


class MockProduct:
    def __init__(self, id, price):
        self.id = id
        self.price = price


class MockQuery:
    def __init__(self, product=None):
        self._product = product

    def filter(self, *args, **kwargs):
        return self

    def first(self):
        return self._product


class MockSession:
    def __init__(self, product=None):
        self._product = product
        self.added = []

    def query(self, *args, **kwargs):
        return MockQuery(self._product)

    def add(self, obj):
        self.added.append(obj)

    def flush(self):
        for obj in self.added:
            if not hasattr(obj, "id") or obj.id is None:
                obj.id = 1

    def commit(self):
        pass

    def refresh(self, obj):
        pass


def test_order_calculation(mocker):
    mocker.patch("services.api.services.order_service.get_redis")
    db = MockSession(product=MockProduct(id=1, price=10.0))

    order_data = OrderCreate(
        user_id=1, items=[OrderItemCreate(product_id=1, quantity=2)]
    )

    order = create_order_service(db, order_data)
    # If the bug is active (price + quantity), total is 12.0
    # The correct value is 20.0. This assert will FAIL when SIMULATE_FAILURE=true and test_failure scenario is active.
    assert order.total_amount == 20.0
