import importlib.machinery, sys
class _MasterFinder:  # simulates a master-bound editable finder placed FIRST
    @classmethod
    def find_spec(cls, name, path=None, target=None):
        if name == "domain":
            return importlib.machinery.PathFinder.find_spec(name, ["/home/codi/Entwicklung/nquiry/packages"])
        return None
sys.meta_path.insert(0, _MasterFinder)
