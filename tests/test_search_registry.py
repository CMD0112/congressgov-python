"""Search registry uses congressgov module paths (not legacy middleware)."""

from congressgov.services.core.search import _SEARCH_REGISTRY, _load_search_handler


def test_search_registry_module_paths_use_congressgov() -> None:
    for resource_type, config in _SEARCH_REGISTRY.items():
        module_path = config["module"]
        assert module_path.startswith("congressgov."), (
            f"{resource_type} registry still points at legacy path: {module_path!r}"
        )
        assert "middleware" not in module_path


def test_load_search_handler_bill() -> None:
    handler = _load_search_handler("bill")
    assert handler.__name__ == "billsearch"
