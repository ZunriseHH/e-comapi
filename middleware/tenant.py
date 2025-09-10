from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.exc import ProgrammingError
from db.session import SessionLocal
from models.tenant import Tenant

class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/health":
            return await call_next(request)

        host = request.headers.get("host", "")
        tenant_hint = request.headers.get("x-tenant")

        with SessionLocal() as db:
            tenant = None
            try:
                if tenant_hint:
                    tenant = db.query(Tenant).filter(Tenant.slug == tenant_hint).first()
                if tenant is None and host:
                    tenant = db.query(Tenant).filter(Tenant.domain == host.split(":")[0]).first()
            except ProgrammingError:
                tenant = None

            request.state.tenant_id = tenant.id if tenant else None

        return await call_next(request)
