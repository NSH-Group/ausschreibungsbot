import structlog, logging

def setup_logging(level: str = 'INFO'):
    logging.basicConfig(level=getattr(logging, level.upper(), logging.INFO), format='%(message)s')
    structlog.configure(processors=[structlog.processors.JSONRenderer()])
    return structlog.get_logger()
