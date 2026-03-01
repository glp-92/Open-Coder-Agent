from fastapi import FastAPI

from controller.routes import router as webhook_router

app = FastAPI(title="Open Coder Agent API")

app.include_router(webhook_router, prefix="/api/webhook")


@app.get("/health")
async def health_check():
    return {"status": "ok"}
