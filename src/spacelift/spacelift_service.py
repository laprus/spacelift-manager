import logging
import uuid
from dto.apply import ApplyResult

logger = logging.getLogger(__name__)

class SpaceliftService:
    
    async def run_apply(
        self,
        stack_id: str,
        commit_sha: str
    ) -> ApplyResult:

        logger.info(f"Simulating apply run for stack {stack_id} at commit {commit_sha}")    
        
        return ApplyResult(
            run_id=str(uuid.uuid4()),
            stack_id=stack_id,
            finished=True,
            success=True
        )