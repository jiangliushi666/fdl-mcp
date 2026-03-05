from fdl_mcp.endpoint_resolver import EndpointResolver


def test_data_service_candidates_auto() -> None:
    resolver = EndpointResolver(base_url="https://fdl.example.com", service_path_mode="auto")
    assert resolver.data_service_candidates("app1", "/foo/bar") == [
        "/service/app1/foo/bar",
        "/service/publish/app1/foo/bar",
    ]


def test_data_service_candidates_legacy() -> None:
    resolver = EndpointResolver(base_url="https://fdl.example.com", service_path_mode="legacy")
    assert resolver.data_service_candidates("app1", "foo/bar") == ["/service/publish/app1/foo/bar"]

