import hashlib
import hmac
from urllib.parse import urlencode

import httpx

from fdl_mcp.auth import AkSkSignatureAuth


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

