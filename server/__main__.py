from fastapi import FastAPI
from contextlib import asynccontextmanager
from server.db.settings import init_db
from server.config import SERVER_PORT, SERVER_ADDRESS
from server.routers.routers import router
import uvicorn


@asynccontextmanager
async def lifespan(app: FastAPI):
    # On startup:
    await init_db()
    yield
    # On shutdown:
    ...


app = FastAPI(lifespan=lifespan)

app.include_router(router)


@app.get("/ping")
async def root():
    return {"message": "ok"}
