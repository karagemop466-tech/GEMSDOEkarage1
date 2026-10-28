"""A parallel research TIFF remains blocked under the literal lattice rule."""
import json
from pathlib import Path
import sys

import pytest

from scripts import audit_existing_candidates as audit

ROOT = Path(__file__).resolve().parents[1]


def test_saved_byte_replay_is_scoped_and_disqualifying():
    report = json.loads((ROOT / 'evidence/bbstep_independent_audit_5c261093.json').read_text())
    assert report['registry_complete'] is False and report['upload_authorized'] is False
    assert report['preplacement_surfaces_checked'] is False
    assert len(report['candidates']) == 2
    for candidate in report['candidates']:
        assert candidate['positive_pixels_in_footprint'] == 17766
        witness = candidate['comparisons'][0]
        assert witness['reference'] == 'lattice'
        assert witness['candidate_dots_within_3px'] == 17504
        assert witness['candidate_dots'] == 17766
        assert witness['overlap_exceeds_70_percent'] is True
        assert candidate['verdict'] == 'duplicate' and candidate['ok_to_submit'] is False
        assert candidate['format_checks']['no_nonfinite_inside'] is True
        assert candidate['format_checks']['inside_values_in_0_1'] is True
        assert candidate['format_checks']['crs_shape_transform_match_mirror'] is True
    zeros, nan = report['candidates']
    assert zeros['format_checks']['outside_all_null_or_nan'] is False
    assert nan['format_checks']['outside_all_null_or_nan'] is True


def test_custom_cli_needs_output_and_cannot_overwrite_input(tmp_path, monkeypatch, capsys):
    candidate = tmp_path / 'candidate.tif'
    candidate.write_bytes(b'preserve me')
    monkeypatch.setattr(audit, 'audit', lambda *args: pytest.fail('unexpected full raster audit'))
    monkeypatch.setattr(sys, 'argv', ['audit_existing_candidates.py', '--candidate', str(candidate)])
    with pytest.raises(SystemExit) as exc:
        audit.main()
    assert exc.value.code == 2
    assert candidate.read_bytes() == b'preserve me'
    monkeypatch.setattr(sys, 'argv', ['audit_existing_candidates.py', '--candidate', str(candidate), '--out', str(candidate)])
    assert audit.main() == 2
    assert 'must not overwrite' in capsys.readouterr().err
    assert candidate.read_bytes() == b'preserve me'
