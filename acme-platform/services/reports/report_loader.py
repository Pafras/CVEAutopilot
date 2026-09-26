"""report_loader — loads YAML report specifications.

Report spec files use the custom Python object tag
``!!python/object:report_loader.ReportSpec`` so that authors can encode
the spec as a native Python object directly in YAML.
"""
import yaml


class ReportSpec:
    """Represents a parsed report specification."""

    def __init__(self):
        self.title = None
        self.columns = []
        self.filters = {}

    def __repr__(self):
        return f"ReportSpec(title={self.title!r}, columns={self.columns!r})"


def load_report_spec(path):
    """Load a YAML report spec file and return a ReportSpec instance."""
    with open(path) as f:
        return yaml.load(f, Loader=yaml.FullLoader)
