from app.db import engine
from app.models import Base

def test_create_tables():
    Base.metadata.create_all(bind=engine)
    assert True
