import os
import pathlib
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.db import init_db
from app.templates_config import templates  # noqa: F401 - re-exported for backward compat

DATA_DIR = os.environ.get("DATA_DIR", "/data")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    for subdir in ("logos", "pdfs", "receipts"):
        pathlib.Path(DATA_DIR, subdir).mkdir(parents=True, exist_ok=True)
    yield
    # Shutdown (nothing to do)


app = FastAPI(title="Invoice Generator", lifespan=lifespan)

# Static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Import and include routers
from app.routes import dashboard, invoices, clients, services, settings  # noqa: E402

app.include_router(dashboard.router)
app.include_router(invoices.router)
app.include_router(clients.router)
app.include_router(services.router)
app.include_router(settings.router)
