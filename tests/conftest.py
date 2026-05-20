import os
import pytest
import tempfile


@pytest.fixture(scope="session", autouse=True)
def data_dir():
    with tempfile.TemporaryDirectory() as d:
        os.environ["DATA_DIR"] = d
        for sub in ("logos", "pdfs", "receipts"):
            os.makedirs(os.path.join(d, sub), exist_ok=True)
        yield d


@pytest.fixture
def db(data_dir):
    from app.db import SessionLocal, init_db
    init_db()
    session = SessionLocal()
    yield session
    session.close()
