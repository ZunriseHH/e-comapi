from fastapi import FastAPI
from middleware.tenant import TenantMiddleware
from api.v1.products import router as products_router

app = FastAPI(title="Ecom API (multi-tenant)")
app.add_middleware(TenantMiddleware)

@app.get("/health")
def health():
    return {"ok": True}

app.include_router(products_router)
