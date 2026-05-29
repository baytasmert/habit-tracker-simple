"""Playwright fixtures — module-scope browser ile hızlı testler."""


def pytest_collection_modifyitems(config, items):
    """E2E testler için marker."""
    for item in items:
        item.add_marker("e2e")
