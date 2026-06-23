from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.supplier import Supplier
from typing import List
from app.schemas.supplier import SupplierSchema

router = APIRouter()


@router.get("/", response_model=List[SupplierSchema])
def list_suppliers(limit: int = Query(20, ge=1, le=200), offset: int = 0, db: Session = Depends(get_db)):
    suppliers = db.query(Supplier).order_by(Supplier.id).limit(limit).offset(offset).all()
    return suppliers
