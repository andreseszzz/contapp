from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import auth, clients, products, invoices, reports

app = FastAPI(
    title=settings.app_name,
    description="Mini ERP contable colombiano con integración a Factus",
    version="0.1.0",
    debug=settings.debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(clients.router, prefix="/api/clients", tags=["clients"])
app.include_router(products.router, prefix="/api/products", tags=["products"])
app.include_router(invoices.router, prefix="/api/invoices", tags=["invoices"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])


@app.get("/api/health")
def health_check():
    return {"status": "ok", "app": settings.app_name}
