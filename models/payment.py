from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, DateTime, func
from sqlalchemy.orm import relationship
from db.base import Base

class PaymentIntent(Base):
    __tablename__ = "payment_intents"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), index=True, nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), unique=True, nullable=False)
    provider = Column(String(20), default="wompi", nullable=False)
    status = Column(String(20), default="pending", index=True)  # pending, paid, failed
    reference = Column(String(100), unique=True, index=True, nullable=False)
    amount_in_cents = Column(Integer, nullable=False)  # Wompi usa centavos
    currency = Column(String(3), default="COP", nullable=False)
    checkout_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    order = relationship("Order")
