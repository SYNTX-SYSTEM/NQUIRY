import importlib.util, sys
def pytest_collection_modifyitems(session, config, items):  # AFTER configure-time checks
    spec = importlib.util.spec_from_file_location("governance.master_copy", "/home/codi/Entwicklung/nquiry/packages/governance/__init__.py")
    mod = importlib.util.module_from_spec(spec); sys.modules["governance.master_copy"] = mod
