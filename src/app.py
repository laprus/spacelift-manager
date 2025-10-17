import random
import logging
from fastapi import FastAPI

from dto.apply import ApplyRequest
from spacelift.client import SpaceliftAuth, SpaceliftClient
from spacelift.service import SpaceliftService
import os


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI(title="Spacelift Service", version="0.1.0")
api_key_id = os.getenv("SPACELIFT_API_KEY_ID", "")
api_key_secret = os.getenv("SPACELIFT_API_KEY_SECRET", "")
service = SpaceliftService(SpaceliftClient(SpaceliftAuth(api_key_id=api_key_id, api_key_secret=api_key_secret)))

logger = logging.getLogger(__name__)

@app.get("/healthy")
def healthy():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.post("/apply")
async def apply(dto: ApplyRequest):
    logging.info("Received apply request: %s", dto)
    result = await service.run_apply(dto.stack_id, dto.commit_sha)
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)