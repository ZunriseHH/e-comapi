# seed.py
from db.session import SessionLocal, engine
from db.base import Base
from models.tenant import Tenant
from models.product import Product

def main():
    # Crea tablas si no existen
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        # Tenant demo
        t = db.query(Tenant).filter(Tenant.slug == "tienda1").first()
        if not t:
            t = Tenant(
                slug="tienda1",
                name="Tienda Uno",
                domain="localhost",  # usar host local para pruebas
                theme={"primary_color": "#0ea5e9"},
                currency="COP",
            )
            db.add(t); db.commit(); db.refresh(t)

        # Productos demo
        if db.query(Product).filter(Product.tenant_id == t.id).count() == 0:
            db.add_all([
                Product(tenant_id=t.id, title="Camiseta Básica", slug="camiseta-basica", price=39000, stock=25),
                Product(tenant_id=t.id, title="Gorra Negra", slug="gorra-negra", price=45000, stock=10),
            ])
            db.commit()

    print("SEED OK")

if __name__ == "__main__":
    main()
