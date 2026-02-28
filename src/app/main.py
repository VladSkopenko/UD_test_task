import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from src.app.features.auction.endpoints import router as auction_router
from src.app.infrastructure.background_tasks import close_expired_lots_task


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(close_expired_lots_task())
    yield
    task.cancel()
    try:
       await task
    except asyncio.CancelledError:
       pass


app = FastAPI(title="Auction API", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(auction_router, prefix="/api/v1")


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.get("/")
def index():
    return FileResponse("static/index.html")


@app.get("/health")
def health():
    return {"status": "ok"}
