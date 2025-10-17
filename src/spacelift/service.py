import asyncio
import logging
from typing import Optional

from dto.apply import ApplyResult
from spacelift.client import SpaceliftAuth, SpaceliftClient


class SpaceliftService:
    def __init__(self, client: SpaceliftClient):
        self._client = client
        self._logger = logging.getLogger(self.__class__.__name__)

    async def run_apply(self, stack_id: str, commit_sha: str, wait: bool = True, poll_seconds: int = 10) -> ApplyResult:
        self._logger.info("Starting apply: stack_id=%s commit_sha=%s wait=%s", stack_id, commit_sha, wait)
        run = await self._client.trigger_run(stack_id, commit_sha)
        run_id = run["id"]
        self._logger.debug("Triggered run id=%s initial_state=%s", run_id, run.get("state"))

        if not wait:
            return ApplyResult(run_id=run_id, stack_id=stack_id, finished=False, success=False)

        while True:
            status = await self._client.get_run_status(stack_id, run_id)
            self._logger.debug("Polled run status: %s", status)
            if status.get("finished"):
                state = status.get("state")
                success = state in {"FINISHED"}
                self._logger.info("Run finished: id=%s state=%s success=%s", run_id, state, success)
                return ApplyResult(run_id=run_id, stack_id=stack_id, finished=True, success=success)
            await asyncio.sleep(poll_seconds)


