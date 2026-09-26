import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from report_loader import ReportSpec, load_report_spec

# A sample spec file that uses the !!python/object tag.
SAMPLE_YAML = """\
!!python/object:report_loader.ReportSpec
title: Monthly Sales
columns:
- region
- revenue
filters:
  status: closed
"""


def test_load_report_spec(tmp_path):
    spec_file = tmp_path / "monthly_sales.yaml"
    spec_file.write_text(SAMPLE_YAML)

    spec = load_report_spec(str(spec_file))

    assert isinstance(spec, ReportSpec), f"Expected ReportSpec, got {type(spec)}"
    assert spec.title == "Monthly Sales"
    assert spec.columns == ["region", "revenue"]
    assert spec.filters == {"status": "closed"}
