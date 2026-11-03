def pytest_configure(config):
    config.addinivalue_line("markers", "kg: needs the live multiomics KG (skip with -m 'not kg')")
