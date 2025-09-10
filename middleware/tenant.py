from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
from db.session import SessionLocal
from models.tenant import Tenant

class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        host = request.headers.get("host", "")
        tenant_hint = request.headers.get("x-tenant")  # para dev/local
        with SessionLocal() as db:
            tenant = None
            if tenant_hint:
                tenant = db.query(Tenant).filter(Tenant.slug == tenant_hint).first()
            if tenant is None and host:
                tenant = db.query(Tenant).filter(Tenant.domain == host.split(":")[0]).first()
            request.state.tenant_id = tenant.id if tenant else None
        return await call_next(request)
