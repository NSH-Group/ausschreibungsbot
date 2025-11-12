from fastapi import FastAPI
from .logging import setup_logging
from .db import engine
from .models import Base
log = setup_logging()
app = FastAPI(title='tender-monitoring')
@app.on_event('startup')
def startup():
    Base.metadata.create_all(bind=engine)
    log.info('startup')
@app.get('/health')
def health():
    return {'status':'ok'}
