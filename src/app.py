import random
from fastapi import FastAPI

from dto.apply import ApplyRequest
from spacelift.spacelift_service import SpaceliftService

app = FastAPI(title="Spacelift Service", version="0.1.0")
service = SpaceliftService()

@app.get("/healthy")
def healthy():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.post("/apply")
async def apply(dto: ApplyRequest):
    result = await service.run_apply(dto.stack_id, dto.commit_sha)
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)