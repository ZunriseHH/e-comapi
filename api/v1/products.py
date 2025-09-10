from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from db.session import get_session
from models.product import Product

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/")
def list_products(request: Request, db: Session = Depends(get_session)):
    if not request.state.tenant_id:
        raise HTTPException(400, "Tenant no resuelto (usa dominio o header X-Tenant).")
    rows = (
        db.query(Product)
          .filter(Product.tenant_id == request.state.tenant_id, Product.active == True)
          .order_by(Product.id.desc())
          .all()
    )
    return [{"id": r.id, "title": r.title, "price": float(r.price), "stock": r.stock} for r in rows]
