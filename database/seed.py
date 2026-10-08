from services.api.database import SessionLocal
from services.api.models.product import Product
from services.api.models.user import User


def seed():
    db = SessionLocal()

    # Check if we already seeded
    if db.query(User).first():
        print("Database already seeded.")
        return

    print("Seeding database...")
    user1 = User(name="Alice", email="alice@example.com")
    user2 = User(name="Bob", email="bob@example.com")

    product1 = Product(name="Widget", price=19.99)
    product2 = Product(name="Gadget", price=29.99)

    db.add_all([user1, user2, product1, product2])
    db.commit()
    print("Seed complete.")
    db.close()


if __name__ == "__main__":
    seed()
