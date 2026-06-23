from app.core.database import engine
from app.models.base import Base

# import all models so they are registered on the metadata
from app.models import supplier, product, order, shipment, inventory  # noqa: F401
from sqlalchemy.orm import Session
from app.services.data_generator import seed


def main():
    print("Creating tables (if not exist) and seeding data...")
    Base.metadata.create_all(bind=engine)
    with Session(bind=engine) as db:
        seed(db)
    print("Seed complete")


if __name__ == "__main__":
    main()
