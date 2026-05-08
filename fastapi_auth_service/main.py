from fastapi import FastAPI
from uvicorn import run

from user_module.user_router import user_router

app = FastAPI()

app.include_router(user_router)

if __name__ == "__main__":
    run(app, host="localhost", port=8000)

