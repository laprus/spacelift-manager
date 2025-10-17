import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

import httpx


SPACELIFT_GRAPHQL_URL = "https://hyland.app.spacelift.io/graphql"


@dataclass
class SpaceliftAuth:
    api_key_id: str
    api_key_secret: str


class SpaceliftClient:
    def __init__(self, auth: SpaceliftAuth, graphql_url: str = SPACELIFT_GRAPHQL_URL):
        self._auth = auth
        self._graphql_url = graphql_url
        self._jwt: Optional[str] = None
        self._logger = logging.getLogger(self.__class__.__name__)

    async def _graph_query(self, query: str, variables: Dict[str, Any], jwt: Optional[str] = None) -> Dict[str, Any]:
        self._logger.debug("GraphQL request to %s with vars keys: %s", self._graphql_url, list(variables.keys()))
        headers = {"Content-Type": "application/json"}
        if jwt:
            headers["Authorization"] = f"Bearer {jwt}"
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(self._graphql_url, json={"query": query, "variables": variables}, headers=headers)
            resp.raise_for_status()
            payload = resp.json()
            if "errors" in payload and payload["errors"]:
                self._logger.error("Spacelift GraphQL error: %s", payload["errors"])
                raise RuntimeError(f"Spacelift GraphQL error: {payload['errors']}")
            return payload["data"]

    async def authenticate(self) -> str:
        mutation = (
            "mutation GetSpaceliftToken($id: ID!, $secret: String!) {"
            "  apiKeyUser(id: $id, secret: $secret) { jwt }"
            "}"
        )
        self._logger.info("Authenticating to Spacelift using API key id (secret not logged)")
        data = await self._graph_query(mutation, {"id": self._auth.api_key_id, "secret": self._auth.api_key_secret})
        jwt = data["apiKeyUser"]["jwt"]
        if not jwt:
            raise RuntimeError("Failed to obtain Spacelift JWT")
        self._jwt = jwt
        self._logger.debug("Spacelift authentication successful; JWT stored in memory")
        return jwt

    async def trigger_run(self, stack_id: str, commit_sha: str) -> Dict[str, Any]:
        if not self._jwt:
            await self.authenticate()
        mutation = (
            "mutation RunTrigger($stack: ID!, $commitSha: String!) {"
            "  runTrigger(stack: $stack, commitSha: $commitSha, runType: TRACKED) {"
            "    id"
            "    state"
            "  }"
            "}"
        )
        self._logger.info("Triggering Spacelift run: stack_id=%s commit_sha=%s", stack_id, commit_sha)
        data = await self._graph_query(mutation, {"stack": stack_id, "commitSha": commit_sha}, jwt=self._jwt)
        self._logger.debug("Triggered run response: %s", data)
        return data["runTrigger"]

    async def get_run_status(self, stack_id: str, run_id: str) -> Dict[str, Any]:
        if not self._jwt:
            await self.authenticate()
        query = (
            "query GetRunById($stackId: ID!, $runId: ID!) {"
            "  stack(id: $stackId) {"
            "    run(id: $runId) {"
            "      id"
            "      state"
            "      type"
            "      finished"
            "      createdAt"
            "    }"
            "  }"
            "}"
        )
        self._logger.debug("Polling run status: stack_id=%s run_id=%s", stack_id, run_id)
        data = await self._graph_query(query, {"stackId": stack_id, "runId": run_id}, jwt=self._jwt)
        self._logger.debug("Run status response: %s", data)
        return data["stack"]["run"]


