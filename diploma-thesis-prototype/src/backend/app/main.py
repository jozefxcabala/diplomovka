from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api import detection, anomaly, result, video

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Povolenie frontend domény
    allow_credentials=True,
    allow_methods=["*"],  # Povolenie všetkých HTTP metód (GET, POST, PUT, DELETE)
    allow_headers=["*"],  # Povolenie všetkých hlavičiek
)

app_version = "Prototype 1.0.0"

@app.get("/ping")
async def return_version():
    return {"message": app_version}

app.include_router(detection.router, prefix="/api")
app.include_router(anomaly.router, prefix="/api")
app.include_router(result.router, prefix="/api")
app.include_router(video.router, prefix="/api")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
