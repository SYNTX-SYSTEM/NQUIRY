import importlib.machinery, os, sys
if os.environ.get("PYTEST_XDIST_WORKER"):  # poison ONLY inside xdist workers
    class _MasterFinder:
        @classmethod
        def find_spec(cls, name, path=None, target=None):
            if name == "domain":
                return importlib.machinery.PathFinder.find_spec(name, ["/home/codi/Entwicklung/nquiry/packages"])
            return None
    sys.meta_path.insert(0, _MasterFinder)
