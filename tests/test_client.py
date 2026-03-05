import json

import httpx
import pytest

from fdl_mcp.auth import AppCodeAuth
from fdl_mcp.client import FDLClient
from fdl_mcp.endpoint_resolver import EndpointResolver
from fdl_mcp.errors import FDLError


@pytest.mark.asyncio
async def test_client_retries_and_succeeds() -> None:
    calls = {"count": 0}

    async def handler(request: httpx.Request) -> httpx.Response:
        calls["count"] += 1
        if calls["count"] == 1:
            return httpx.Response(500, text="temp")
        return httpx.Response(200, json={"ok": True})

    client = FDLClient(
        resolver=EndpointResolver(base_url="https://fdl.example.com"),
        auth_provider=AppCodeAuth("abc"),
        retry_max=1,
        transport=httpx.MockTransport(handler),
    )
    data, status, endpoint = await client.request_json("GET", "/decision/sp/client/api/fdl/record/info")
    assert data == {"ok": True}
    assert status == 200
    assert endpoint == "/decision/sp/client/api/fdl/record/info"
    assert calls["count"] == 2


@pytest.mark.asyncio
async def test_client_maps_auth_error() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, text=json.dumps({"msg": "unauthorized"}))

    client = FDLClient(
        resolver=EndpointResolver(base_url="https://fdl.example.com"),
        auth_provider=AppCodeAuth("abc"),
        retry_max=0,
        transport=httpx.MockTransport(handler),
    )
    with pytest.raises(FDLError) as err:
        await client.request_json("GET", "/decision/sp/client/api/fdl/record/info")
    assert err.value.code == "FDL_AUTH_HTTP_401"

