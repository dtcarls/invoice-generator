import os
import pytest
import tempfile

# Set DATA_DIR BEFORE any app imports happen so the engine is initialised
# correctly when modules are first loaded.  We use a single session-level
# temp directory for file storage (PDFs, logos, etc.) but give each test
# function its own fresh SQLite file so there is no data leakage between tests.
_session_tmpdir = tempfile.mkdtemp()
os.environ["DATA_DIR"] = _session_tmpdir
for _sub in ("logos", "pdfs", "receipts"):
    os.makedirs(os.path.join(_session_tmpdir, _sub), exist_ok=True)


@pytest.fixture(scope="session", autouse=True)
def data_dir():
    """Return the temp DATA_DIR used for the entire test session."""
    yield _session_tmpdir


@pytest.fixture
def db(data_dir):
    """
    Provide a fresh, isolated DB session for each test.

    A new SQLite file is created for every test so that rows committed by one
    test never affect another.
    """
    import uuid
    from app.db import init_db, SessionLocal, Base, _make_engine
    from sqlalchemy.orm import sessionmaker

    # Point to a brand-new DB file for this test
    db_path = os.path.join(data_dir, f"test_{uuid.uuid4().hex}.db")
    os.environ["DATA_DIR"] = data_dir  # keep DATA_DIR consistent

    # Build a throw-away engine + session factory
    from sqlalchemy import create_engine
    test_engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
    )

    # Import models to ensure they are registered on Base
    import app.models  # noqa: F401

    Base.metadata.create_all(test_engine)
    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestSession()
    yield session
    session.close()
    test_engine.dispose()
    try:
        os.remove(db_path)
    except OSError:
        pass
