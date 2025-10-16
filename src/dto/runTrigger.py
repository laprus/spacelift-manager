from pydantic import BaseModel

class RunTriggerResult(BaseModel):
    run_id: str
    state: str
