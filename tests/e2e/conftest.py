"""Playwright fixtures — module-scope browser ile hızlı testler."""


def pytest_configure(config):
    """'e2e' marker'ını kaydet → PytestUnknownMarkWarning'i önler."""
    config.addinivalue_line("markers", "e2e: uçtan uca (Playwright) testler")


def pytest_collection_modifyitems(config, items):
    """E2E testler için marker."""
    for item in items:
        item.add_marker("e2e")
