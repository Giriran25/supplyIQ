from faker import Faker
import random
from typing import List
from sqlalchemy.orm import Session
from app.models.supplier import Supplier
from app.models.product import Product
from app.models.order import Order
from app.models.shipment import Shipment
from app.models.inventory import InventorySnapshot, Warehouse
import numpy as np


fake = Faker()


def generate_suppliers(n: int = 100) -> List[dict]:
    regions = ["EMEA", "APAC", "AMER", "MEA", "LATAM"]
    suppliers = []
    for i in range(n):
        suppliers.append(
            {
                "name": fake.company() + f" {i}",
                "region": random.choice(regions),
                "tier": random.choices([1, 2, 3], weights=[0.2, 0.5, 0.3])[0],
                "lead_time_mean": float(np.random.lognormal(mean=1.5, sigma=0.4)),
                "lead_time_std": float(max(0.5, np.random.rand() * 3.0)),
                "on_time_rate": float(round(0.7 + np.random.rand() * 0.25, 3)),
            }
        )
    return suppliers


def seed(db: Session):
    # products
    products = []
    for i in range(1, 51):
        p = Product(sku=f"SKU-{i:04d}", name=f"Product {i}", category="general", unit_cost=1.0 + i * 0.1, critical=(i <= 10))
        db.add(p)
        products.append(p)
    db.flush()

    # suppliers
    suppliers = []
    for s in generate_suppliers(100):
        sup = Supplier(**s)
        db.add(sup)
        suppliers.append(sup)
    db.flush()

    # warehouses
    warehouses = []
    regions = ["EMEA", "APAC", "AMER", "MEA", "LATAM"]
    for i, r in enumerate(regions, start=1):
        w = Warehouse(name=f"WH-{i}", region=r)
        db.add(w)
        warehouses.append(w)
    db.flush()

    # orders and shipments
    shipments = []
    for i in range(1000):
        prod = random.choice(products)
        order = Order(product_id=prod.id, quantity=random.randint(1, 20))
        db.add(order)
        db.flush()

        # one or more shipments per order
        for _ in range(random.choices([1, 1, 2], weights=[0.6, 0.2, 0.2])[0]):
            sup = random.choice(suppliers)
            lead = float(np.random.lognormal(mean=1.5, sigma=0.5))
            delayed = random.random() > sup.on_time_rate
            sh = Shipment(order_id=order.id, supplier_id=sup.id, lead_time_days=lead, delayed=delayed)
            db.add(sh)
            shipments.append(sh)

    db.flush()

    # inventory snapshots
    for prod in products[:50]:
        for wh in warehouses:
            inv = InventorySnapshot(product_id=prod.id, warehouse_id=wh.id, quantity=random.randint(0, 500))
            db.add(inv)

    db.commit()
