from pydantic import BaseModel

class ApplyRequest(BaseModel):
    stack_id: str
    commit_sha: str

class ApplyResult(BaseModel):
    run_id: str
    stack_id: str
    finished: bool
    success: bool