from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Numeric, Boolean, ForeignKey
from db.base import Base

class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), index=True)
    title: Mapped[str] = mapped_column(String(160))
    slug: Mapped[str] = mapped_column(String(160), index=True)
    price: Mapped[float] = mapped_column(Numeric(12,2))
    stock: Mapped[int] = mapped_column(Integer, default=0)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
