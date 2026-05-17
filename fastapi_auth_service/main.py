from fastapi import FastAPI
from uvicorn import run

from user_module.user_router import user_router
from shared.config import settings
from urllib.parse import urlparse

app = FastAPI()

app.include_router(user_router)

if __name__ == "__main__":
    parsed_url = urlparse(settings.FASTAPI_AUTH_URL)
    run(app, host=parsed_url.hostname, port=parsed_url.port)

