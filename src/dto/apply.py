from pydantic import BaseModel, field_validator


class ApplyRequest(BaseModel):
    stack_id: str
    commit_sha: str
    
    @field_validator('commit_sha')
    @classmethod
    def remove_sha256_prefix(cls, v: str) -> str:
        if v.startswith("sha256:"):
            return v[len("sha256:") :]
        return v

class ApplyResult(BaseModel):
    run_id: str
    stack_id: str
    finished: bool
    success: bool