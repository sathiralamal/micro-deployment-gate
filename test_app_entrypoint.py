import importlib


def test_app_exports_entrypoint():
    module = importlib.import_module("app")
    assert hasattr(module, "app"), "app.py must export an app object for deployment"
    assert hasattr(module, "main"), "app.py must expose a main() function for local run"
