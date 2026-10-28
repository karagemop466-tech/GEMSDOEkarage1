"""A successful report write must never be mistaken for an input readiness pass."""
import json
import sys

import pytest

from scripts import shared_tools


@pytest.fixture
def workspace(tmp_path, monkeypatch):
    monkeypatch.setattr(shared_tools, 'ROOT', tmp_path)
    (tmp_path / 'registry').mkdir()
    return tmp_path


def configure(root, lane, missing=()):
    (root / 'registry/template.json').write_text(json.dumps(
        {'method_lane': lane, 'commit': 'pinned-test-commit'}))
    for name in ('feature_stack.npy', 'training_features.tif',
                 'sample_submission.tif', 'labels.tif', 'existing_faults.tif'):
        if name not in missing:
            folder = 'gems_work' if name.endswith('.npy') else 'gems_data'
            path = root / '.cache' / folder / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()


@pytest.mark.parametrize('lane', [None, '', '  ', [], 1, False])
def test_invalid_lane_blocks_even_with_inputs(workspace, lane):
    configure(workspace, lane)
    assert not shared_tools.preflight()['ready_for_shared_tools']


def test_catalogue_is_required(workspace):
    configure(workspace, 'assigned-lane', ('existing_faults.tif',))
    report = shared_tools.preflight()
    assert report['missing'] == ['.cache/gems_data/existing_faults.tif']
    assert not report['ready_for_shared_tools']


@pytest.mark.parametrize('missing,code', [(('feature_stack.npy',), 1), ((), 0)])
def test_cli_exit_status_is_readiness_not_report_success(workspace, monkeypatch, capsys, missing, code):
    configure(workspace, 'assigned-lane', missing)
    monkeypatch.setattr(sys, 'argv', ['shared_tools.py', 'preflight'])
    assert shared_tools.main() == code
    report = json.loads(capsys.readouterr().out)
    assert report['ok_to_submit'] is False
    assert report['ready_for_shared_tools'] == (code == 0)


@pytest.mark.parametrize('command', ['evaluate', 'write'])
def test_blocked_execution_never_bootstraps(workspace, monkeypatch, command):
    configure(workspace, '   ')
    monkeypatch.setattr(sys, 'argv', ['shared_tools.py', command])
    monkeypatch.setattr(shared_tools, 'bootstrap', lambda: pytest.fail('bootstrapped blocked run'))
    with pytest.raises(SystemExit, match='BLOCKED'):
        shared_tools.main()
