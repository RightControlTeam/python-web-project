from fastapi import FastAPI
from uvicorn import run

from shared.config import settings
from urllib.parse import urlparse
from transaction_service.transaction_module.transaction_router import transaction_router

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "transaction"}

app.include_router(transaction_router)


if __name__ == "__main__":
    parsed_url = urlparse(settings.TRANSACTION_SERVICE_URL)
    run(app, host=parsed_url.hostname, port=parsed_url.port)

