import hashlib
import hmac
from urllib.parse import urlencode

import httpx

from fdl_mcp.auth import AkSkSignatureAuth, FineAuthTokenAuth
from fdl_mcp.config import FDLSettings


def test_aksk_signature_headers_are_stable() -> None:
    auth = AkSkSignatureAuth(client_id="cid", secret="sec", now_fn=lambda: 1_700_000_000)
    request = httpx.Request(
        "POST",
        "https://fdl.example.com/decision/sp/client/api/fdl/workId/execute?" + urlencode({"b": "2", "a": "1"}),
        json={"x": 1},
    )
    auth.apply(request)

    assert request.headers["X-FDL-Client-Id"] == "cid"
    assert request.headers["X-FDL-Timestamp"] == "1700000000"
    canonical = "\n".join(
        [
            "POST",
            "/decision/sp/client/api/fdl/workId/execute",
            "a=1&b=2",
            "1700000000",
            hashlib.sha256(request.content).hexdigest(),
        ]
    )
    expected = hmac.new(b"sec", canonical.encode("utf-8"), hashlib.sha256).hexdigest()
    assert request.headers["X-FDL-Signature"] == expected


def test_fine_auth_token_sets_bearer_and_cookie() -> None:
    auth = FineAuthTokenAuth(token="demo-token")
    request = httpx.Request("GET", "https://fdl.example.com/webroot/decision/fdl/dev/work/save")

    auth.apply(request)

    assert request.headers["Authorization"] == "Bearer demo-token"
    assert request.headers["Cookie"] == "fine_auth_token=demo-token"


def test_fine_auth_token_prefers_full_cookie_header() -> None:
    auth = FineAuthTokenAuth(
        token="demo-token",
        cookie_header="JSESSIONID=abc; fine_auth_token=demo-token; tenant=1",
    )
    request = httpx.Request("GET", "https://fdl.example.com/webroot/decision/fdl/dev/work/save")

    auth.apply(request)

    assert request.headers["Authorization"] == "Bearer demo-token"
    assert request.headers["Cookie"] == "JSESSIONID=abc; fine_auth_token=demo-token; tenant=1"


def test_settings_extract_token_from_cookie() -> None:
    settings = FDLSettings(
        base_url="https://fdl.example.com",
        auth_mode="fine_auth_token",
        client_id=None,
        secret=None,
        appcode=None,
        fine_auth_token="demo-token",
        fine_auth_cookie="JSESSIONID=abc; fine_auth_token=demo-token",
        timeout_ms=10000,
        retry_max=2,
        service_path_mode="auto",
        encrypt_mode="aes",
        encrypt_key="1ED6F5BA8CFD75F8",
        chrome_session_mode=True,
        chrome_session_page_url="https://fdl.example.com/webroot/decision#preparation",
        allowed_work_ids=set(),
        allowed_work_names=set(),
        allowed_tools=set(),
        rate_limit_per_min=120,
        idempotency_ttl_sec=600,
    )

    settings.validate()

