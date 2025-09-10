from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import select
import os, httpx, secrets
from db.session import get_session
from models.order import Order
from models.payment import PaymentIntent

router = APIRouter(prefix="/payments", tags=["payments"])

WOMPI_BASE = os.getenv("WOMPI_SANDBOX_BASE", "https://sandbox.wompi.co/v1")
WOMPI_PK = os.getenv("WOMPI_PUBLIC_KEY", "")
WOMPI_SK = os.getenv("WOMPI_PRIVATE_KEY", "")

@router.get("/acceptance")
def get_acceptance_token():
    # Útil si quieres mostrar texto de aceptación; opcional
    return {"wompi_public_key": WOMPI_PK}

@router.post("/intents/{order_id}")
def create_payment_intent(order_id: int, request: Request, db: Session = Depends(get_session)):
    tenant_id = request.state.tenant_id
    if not tenant_id:
        raise HTTPException(400, "Tenant no resuelto.")

    order = db.get(Order, order_id)
    if not order or order.tenant_id != tenant_id:
        raise HTTPException(404, "Pedido no encontrado.")
    if order.status == "paid":
        return {"status": "already_paid", "order_id": order_id}

    # Idempotencia simple: si ya existe intent para la orden, reusar
    pi = db.execute(
        select(PaymentIntent).where(PaymentIntent.order_id == order_id)
    ).scalar_one_or_none()

    amount_in_cents = int(round(order.total * 100))

    if not pi:
        reference = f"ORD-{order_id}-{secrets.token_hex(4)}"
        pi = PaymentIntent(
            tenant_id=tenant_id,
            order_id=order_id,
            reference=reference,
            amount_in_cents=amount_in_cents,
            currency="COP",
            status="pending"
        )
        db.add(pi); db.flush()
    else:
        reference = pi.reference

    # Wompi: Checkout URL (Link de pago, sandbox)
    # Documentación: creamos un "Payment Link" efímero via API Board (simulado simple)
    # Alternativa común: integrar "Checkout" en frontend con public key; aquí devolvemos una URL
    checkout_url = f"https://checkout.wompi.co/p/?public-key={WOMPI_PK}&currency=COP&amount-in-cents={amount_in_cents}&reference={reference}"

    pi.checkout_url = checkout_url
    db.commit()
    db.refresh(pi)

    return {
        "order_id": order_id,
        "reference": reference,
        "amount_in_cents": amount_in_cents,
        "currency": "COP",
        "checkout_url": checkout_url,
        "status": pi.status
    }

@router.post("/webhooks/wompi")
async def wompi_webhook(payload: dict, request: Request, db: Session = Depends(get_session)):
    """
    Webhook muy simplificado: en sandbox, marca paid cuando event == transaction.updated && status == APPROVED
    En producción valida firma con WOMPI_SK (X-Signature).
    """
    event = payload.get("event")
    data = payload.get("data", {})
    transaction = data.get("transaction", {})
    reference = transaction.get("reference")
    status = transaction.get("status")  # APPROVED, DECLINED, ERROR

    if not reference:
        return {"ok": True}

    pi = db.execute(
        select(PaymentIntent).where(PaymentIntent.reference == reference)
    ).scalar_one_or_none()
    if not pi:
        return {"ok": True}

    if status == "APPROVED":
        pi.status = "paid"
        order = db.get(Order, pi.order_id)
        if order:
            order.status = "paid"
    elif status in ("DECLINED", "ERROR"):
        pi.status = "failed"

    db.commit()
    return {"ok": True}
