from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, JSON
from db.base import Base

class Tenant(Base):
    __tablename__ = "tenants"
    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    domain: Mapped[str] = mapped_column(String(255), unique=True)
    theme: Mapped[dict] = mapped_column(JSON, default=dict)  # {logo_url, primary_color,...}
    currency: Mapped[str] = mapped_column(String(8), default="COP")
