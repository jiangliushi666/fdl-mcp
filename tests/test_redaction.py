from fdl_mcp.redaction import redact_value


def test_redaction_masks_sensitive_keys() -> None:
    payload = {
        "client_id": "abc",
        "secret": "s",
        "nested": {"fine_auth_token": "t", "x": 1},
        "list": [{"authorization": "Bearer z"}],
    }
    redacted = redact_value(payload)
    assert redacted["secret"] == "***REDACTED***"
    assert redacted["nested"]["fine_auth_token"] == "***REDACTED***"
    assert redacted["list"][0]["authorization"] == "***REDACTED***"
    assert redacted["nested"]["x"] == 1

