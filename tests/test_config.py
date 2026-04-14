import pytest

from fdl_mcp.config import FDLSettings


def test_from_chrome_session_payload_builds_runtime_settings() -> None:
    settings = FDLSettings.from_chrome_session_payload(
        {
            "origin": "http://192.168.138.35:8068",
            "href": "http://192.168.138.35:8068/webroot/decision#preparation",
            "frontSeed": "1ED6F5BA8CFD75F8",
            "cookie": "JSESSIONID=abc; fine_auth_token=demo-token; tenant=1",
        }
    )

    assert settings.base_url == "http://192.168.138.35:8068"
    assert settings.auth_mode == "fine_auth_token"
    assert settings.fine_auth_token == "demo-token"
    assert settings.fine_auth_cookie == "JSESSIONID=abc; fine_auth_token=demo-token; tenant=1"
    assert settings.encrypt_mode == "aes"
    assert settings.encrypt_key == "1ED6F5BA8CFD75F8"
    assert settings.chrome_session_mode is True
    assert settings.chrome_session_page_url == "http://192.168.138.35:8068/webroot/decision#preparation"


def test_from_chrome_session_payload_missing_origin_fails_validation() -> None:
    settings = FDLSettings.from_chrome_session_payload(
        {
            "href": "http://192.168.138.35:8068/webroot/decision#preparation",
            "frontSeed": "1ED6F5BA8CFD75F8",
            "cookie": "JSESSIONID=abc; fine_auth_token=demo-token; tenant=1",
        }
    )

    with pytest.raises(ValueError) as err:
        settings.validate()

    assert str(err.value) == "FDL_BASE_URL is required"


def test_from_chrome_session_payload_missing_front_seed_fails_validation() -> None:
    settings = FDLSettings.from_chrome_session_payload(
        {
            "origin": "http://192.168.138.35:8068",
            "href": "http://192.168.138.35:8068/webroot/decision#preparation",
            "cookie": "JSESSIONID=abc; fine_auth_token=demo-token; tenant=1",
        }
    )

    with pytest.raises(ValueError) as err:
        settings.validate()

    assert str(err.value) == "FDL_ENCRYPT_KEY is required for aes mode"


def test_from_chrome_session_payload_missing_cookie_token_fails_validation() -> None:
    settings = FDLSettings.from_chrome_session_payload(
        {
            "origin": "http://192.168.138.35:8068",
            "href": "http://192.168.138.35:8068/webroot/decision#preparation",
            "frontSeed": "1ED6F5BA8CFD75F8",
            "cookie": "JSESSIONID=abc; tenant=1",
        }
    )

    with pytest.raises(ValueError) as err:
        settings.validate()

    assert str(err.value) == "FDL_FINE_AUTH_TOKEN is required for fine_auth_token mode"


def test_validate_accepts_none_auth_mode() -> None:
    settings = FDLSettings(
        base_url="https://fdl.example.com",
        auth_mode="none",
        client_id=None,
        secret=None,
        appcode=None,
        fine_auth_token=None,
        fine_auth_cookie=None,
        timeout_ms=10000,
        retry_max=2,
        service_path_mode="auto",
        encrypt_mode="none",
        encrypt_key=None,
        chrome_session_mode=False,
        chrome_session_page_url=None,
        allowed_work_ids=set(),
        allowed_work_names=set(),
        allowed_tools=set(),
        rate_limit_per_min=120,
        idempotency_ttl_sec=600,
    )

    settings.validate()


def test_validate_requires_encrypt_key_for_aes_mode() -> None:
    settings = FDLSettings(
        base_url="https://fdl.example.com",
        auth_mode="none",
        client_id=None,
        secret=None,
        appcode=None,
        fine_auth_token=None,
        fine_auth_cookie=None,
        timeout_ms=10000,
        retry_max=2,
        service_path_mode="auto",
        encrypt_mode="aes",
        encrypt_key=None,
        chrome_session_mode=False,
        chrome_session_page_url=None,
        allowed_work_ids=set(),
        allowed_work_names=set(),
        allowed_tools=set(),
        rate_limit_per_min=120,
        idempotency_ttl_sec=600,
    )

    try:
        settings.validate()
        assert False, "expected validate() to fail"
    except ValueError as err:
        assert str(err) == "FDL_ENCRYPT_KEY is required for aes mode"
