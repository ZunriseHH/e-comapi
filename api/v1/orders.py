# api/v1/orders.py
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import select
from db.session import get_session
from models.product import Product
from models.customer import Customer
from models.order import Order, OrderItem
from schemas.orders import OrderCreateIn, OrderOut
from typing import List
from schemas.orders import OrderOut
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from schemas.orders import OrderDetailOut

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/", response_model=OrderOut)
def create_order(payload: OrderCreateIn, request: Request, db: Session = Depends(get_session)):
    tenant_id = request.state.tenant_id
    if not tenant_id:
        raise HTTPException(400, "Tenant no resuelto (dominio o X-Tenant).")

    # 1) Upsert básico de Customer por email
    cust = db.execute(
        select(Customer).where(Customer.tenant_id==tenant_id, Customer.email==payload.customer.email)
    ).scalar_one_or_none()
    if not cust:
        cust = Customer(tenant_id=tenant_id, email=payload.customer.email, name=payload.customer.name)
        db.add(cust); db.flush()  # flush para obtener ID

    # 2) Cargar productos, validar stock y calcular total
    total = 0
    items_data = []
    for item in payload.items:
        p = db.get(Product, item.product_id)
        if not p or p.tenant_id != tenant_id or not p.active:
            raise HTTPException(400, f"Producto {item.product_id} no disponible.")
        if p.stock < item.qty:
            raise HTTPException(400, f"Stock insuficiente para {p.title} (disp: {p.stock}).")
        line_total = float(p.price) * item.qty
        total += line_total
        items_data.append((p, item.qty, line_total))

    # 3) Crear Order + Items
    order = Order(tenant_id=tenant_id, customer_id=cust.id, total=total, status="created")
    db.add(order); db.flush()

    for p, qty, line_total in items_data:
        db.add(OrderItem(order_id=order.id, product_id=p.id, title=p.title,
                         qty=qty, unit_price=p.price, line_total=line_total))
        # opcional: descontar stock en created
        p.stock -= qty

    db.commit()
    db.refresh(order)
    return order

@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int, request: Request, db: Session = Depends(get_session)):
    tenant_id = request.state.tenant_id
    if not tenant_id:
        raise HTTPException(400, "Tenant no resuelto.")
    order = db.get(Order, order_id)
    if not order or order.tenant_id != tenant_id:
        raise HTTPException(404, "Pedido no encontrado.")
    return order

# api/v1/orders.py (agrega abajo)


@router.get("/", response_model=List[OrderOut])
def list_orders(request: Request, db: Session = Depends(get_session)):
    tenant_id = request.state.tenant_id
    if not tenant_id:
        raise HTTPException(400, "Tenant no resuelto.")
    rows = db.execute(
        select(Order).where(Order.tenant_id == tenant_id).order_by(Order.id.desc())
    ).scalars().all()
    return rows

@router.get("/{order_id}", response_model=OrderDetailOut)
def get_order(order_id: int, request: Request, db: Session = Depends(get_session)):
    tenant_id = request.state.tenant_id
    if not tenant_id:
        raise HTTPException(400, "Tenant no resuelto.")
    order = db.query(Order).options(selectinload(Order.items)).get(order_id)
    if not order or order.tenant_id != tenant_id:
        raise HTTPException(404, "Pedido no encontrado.")
    return order
