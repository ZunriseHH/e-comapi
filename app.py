from fastapi import FastAPI
from middleware.tenant import TenantMiddleware
from api.v1.products import router as products_router
from api.v1.orders import router as orders_router
from api.v1.payments import router as payments_router




app = FastAPI(title="Ecom API (multi-tenant)")
app.add_middleware(TenantMiddleware)

@app.get("/health")
def health():
    return {"ok": True}

app.include_router(products_router)
app.include_router(orders_router)
app.include_router(payments_router)
