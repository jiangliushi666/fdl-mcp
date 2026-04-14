import base64
import json

import httpx
import pytest
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

from fdl_mcp.auth import AppCodeAuth
from fdl_mcp.client import FDLClient
from fdl_mcp.endpoint_resolver import EndpointResolver
from fdl_mcp.errors import FDLError


@pytest.mark.asyncio
async def test_request_fdl_dev_plaintext_headers() -> None:
    captured: dict[str, str] = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        captured["fdl-encrypt"] = request.headers["fdl-encrypt"]
        captured["x-requested-with"] = request.headers["x-requested-with"]
        captured["accept"] = request.headers["accept"]
        return httpx.Response(200, json={"ok": True})

    client = FDLClient(
        resolver=EndpointResolver(base_url="https://fdl.example.com"),
        auth_provider=AppCodeAuth("abc"),
        retry_max=0,
        transport=httpx.MockTransport(handler),
    )

    data, status, endpoint = await client.request_fdl_dev(
        "GET",
        "/webroot/decision/fdl/dev/param/global/query",
    )

    assert data == {"ok": True}
    assert status == 200
    assert endpoint == "/webroot/decision/fdl/dev/param/global/query"
    assert captured == {
        "fdl-encrypt": "plaintext",
        "x-requested-with": "XMLHttpRequest",
        "accept": "application/json, text/plain, */*",
    }


@pytest.mark.asyncio
async def test_request_fdl_dev_encrypted_string_body_without_local_encryption() -> None:
    captured: dict[str, str] = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        captured["fdl-encrypt"] = request.headers["fdl-encrypt"]
        captured["content-type"] = request.headers["content-type"]
        captured["body"] = request.content.decode("utf-8")
        return httpx.Response(200, json={"ok": True})

    client = FDLClient(
        resolver=EndpointResolver(base_url="https://fdl.example.com"),
        auth_provider=AppCodeAuth("abc"),
        retry_max=0,
        transport=httpx.MockTransport(handler),
    )

    await client.request_fdl_dev(
        "POST",
        "/webroot/decision/fdl/dev/work/publish",
        body="encrypted-payload",
        encrypted=True,
    )

    assert captured == {
        "fdl-encrypt": "encrypted",
        "content-type": "application/json",
        "body": "encrypted-payload",
    }


@pytest.mark.asyncio
async def test_request_fdl_dev_encrypts_json_payload_in_aes_mode() -> None:
    captured: dict[str, str] = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        captured["fdl-encrypt"] = request.headers["fdl-encrypt"]
        captured["content-type"] = request.headers["content-type"]
        captured["body"] = request.content.decode("utf-8")
        return httpx.Response(200, json={"ok": True})

    client = FDLClient(
        resolver=EndpointResolver(base_url="https://fdl.example.com"),
        auth_provider=AppCodeAuth("abc"),
        retry_max=0,
        encrypt_mode="aes",
        encrypt_key="1ED6F5BA8CFD75F8",
        transport=httpx.MockTransport(handler),
    )

    await client.request_fdl_dev(
        "POST",
        "/webroot/decision/fdl/dev/work/save",
        body={"name": "demo"},
        encrypted=True,
    )

    assert captured == {
        "fdl-encrypt": "encrypted",
        "content-type": "application/json",
        "body": "PJIwE/gRfS6vGyZuWmg+NA==",
    }


@pytest.mark.asyncio
async def test_request_fdl_dev_decrypts_encrypted_response_in_aes_mode() -> None:
    plaintext = json.dumps({"ok": True}, separators=(",", ":"))
    cipher = AES.new(b"1ED6F5BA8CFD75F8", AES.MODE_ECB)
    encrypted = base64.b64encode(cipher.encrypt(pad(plaintext.encode("utf-8"), AES.block_size))).decode("utf-8")

    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text=encrypted, headers={"alreadyencrypted": "true"})

    client = FDLClient(
        resolver=EndpointResolver(base_url="https://fdl.example.com"),
        auth_provider=AppCodeAuth("abc"),
        retry_max=0,
        encrypt_mode="aes",
        encrypt_key="1ED6F5BA8CFD75F8",
        transport=httpx.MockTransport(handler),
    )

    data, status, endpoint = await client.request_fdl_dev(
        "POST",
        "/webroot/decision/fdl/dev/work/publish/check",
        body={"name": "demo"},
        encrypted=True,
    )

    assert data == {"ok": True}
    assert status == 200
    assert endpoint == "/webroot/decision/fdl/dev/work/publish/check"


@pytest.mark.asyncio
async def test_request_fdl_dev_decrypts_non_json_encrypted_response_to_raw() -> None:
    plaintext = "ok-not-json"
    cipher = AES.new(b"1ED6F5BA8CFD75F8", AES.MODE_ECB)
    encrypted = base64.b64encode(cipher.encrypt(pad(plaintext.encode("utf-8"), AES.block_size))).decode("utf-8")

    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text=encrypted, headers={"alreadyencrypted": "true"})

    client = FDLClient(
        resolver=EndpointResolver(base_url="https://fdl.example.com"),
        auth_provider=AppCodeAuth("abc"),
        retry_max=0,
        encrypt_mode="aes",
        encrypt_key="1ED6F5BA8CFD75F8",
        transport=httpx.MockTransport(handler),
    )

    data, status, endpoint = await client.request_fdl_dev(
        "POST",
        "/webroot/decision/fdl/dev/work/save",
        body={"name": "demo"},
        encrypted=True,
    )

    assert data == {"raw": "ok-not-json"}
    assert status == 200
    assert endpoint == "/webroot/decision/fdl/dev/work/save"


@pytest.mark.asyncio
async def test_request_fdl_dev_returns_clear_error_on_invalid_aes_config() -> None:
    client = FDLClient(
        resolver=EndpointResolver(base_url="https://fdl.example.com"),
        auth_provider=AppCodeAuth("abc"),
        retry_max=0,
        encrypt_mode="aes",
        encrypt_key="short",
        transport=httpx.MockTransport(lambda request: httpx.Response(200, json={"ok": True})),
    )

    with pytest.raises(FDLError) as err:
        await client.request_fdl_dev(
            "POST",
            "/webroot/decision/fdl/dev/work/save",
            body={"name": "demo"},
            encrypted=True,
        )

    assert err.value.code == "FDL_ENCRYPT_INVALID_CONFIG"


@pytest.mark.asyncio
async def test_request_json_maps_404() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, text="missing")

    client = FDLClient(
        resolver=EndpointResolver(base_url="https://fdl.example.com"),
        auth_provider=AppCodeAuth("abc"),
        retry_max=0,
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(FDLError) as err:
        await client.request_json("GET", "/missing")

    assert err.value.code == "FDL_HTTP_404"
