# Simulated contract test
# In a real environment, this might use pact-python or just httpx calls to a mocked/running catalog service.


def test_catalog_product_contract():
    """
    Contract expectation:
    The Checkout service expects the Catalog service to return a product object with:
    - "id" (string)
    - "price" (float)
    - "name" (string)
    """
    import os

    # Simulate response from Catalog
    # A genuine breaking change would change "price" to "amount" or "price_cents", breaking this consumer.

    if os.environ.get("BREAK_CATALOG_CONTRACT") == "true":
        catalog_response = {
            "id": "prod_123",
            "price_cents": 1999,  # Breaking change: changed from price to price_cents
            "name": "Widget",
        }
    else:
        catalog_response = {
            "id": "prod_123",
            "price": 19.99,  # The expected contract
            "name": "Widget",
        }

    # Contract validation by the consumer (Checkout)
    assert "id" in catalog_response
    assert "price" in catalog_response, (
        "Contract broken: 'price' field is missing from catalog response"
    )
    assert isinstance(catalog_response.get("price"), float)
    assert "name" in catalog_response
