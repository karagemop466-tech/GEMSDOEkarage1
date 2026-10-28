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
            path.write_bytes(b'placeholder; not a validated scientific input')


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


@pytest.mark.parametrize('name', [
    'feature_stack.npy', 'existing_faults.tif', 'training_features.tif',
    'sample_submission.tif', 'labels.tif',
])
def test_empty_input_blocks_readiness(workspace, name):
    configure(workspace, 'assigned-lane')
    folder = 'gems_work' if name.endswith('.npy') else 'gems_data'
    path = workspace / '.cache' / folder / name
    path.write_bytes(b'')
    report = shared_tools.preflight()
    assert report['empty'] == [str(path.relative_to(workspace))]
    assert report['missing'] == []
    assert report['unreadable'] == []
    assert not report['ready_for_shared_tools']


@pytest.mark.parametrize('command', ['preflight', 'evaluate', 'write'])
def test_empty_cache_never_runs_shared_tools(workspace, monkeypatch, capsys, command):
    configure(workspace, 'assigned-lane')
    (workspace / '.cache/gems_work/feature_stack.npy').write_bytes(b'')
    monkeypatch.setattr(sys, 'argv', ['shared_tools.py', command])
    monkeypatch.setattr(shared_tools, 'bootstrap', lambda: pytest.fail('bootstrapped empty cache'))
    if command == 'preflight':
        assert shared_tools.main() == 1
        assert json.loads(capsys.readouterr().out)['empty']
    else:
        with pytest.raises(SystemExit, match='empty or unreadable'):
            shared_tools.main()


def test_unreadable_input_fails_closed(workspace, monkeypatch):
    configure(workspace, 'assigned-lane')
    original = shared_tools.Path.open
    def denied(path, *args, **kwargs):
        if path.name == 'feature_stack.npy':
            raise PermissionError('synthetic unreadable cache')
        return original(path, *args, **kwargs)
    monkeypatch.setattr(shared_tools.Path, 'open', denied)
    report = shared_tools.preflight()
    assert report['unreadable'] == ['.cache/gems_work/feature_stack.npy']
    assert not report['ready_for_shared_tools']


@pytest.mark.parametrize('kind', ['directory', 'broken-symlink'])
def test_nonfile_input_is_missing(workspace, kind):
    configure(workspace, 'assigned-lane')
    path = workspace / '.cache/gems_work/feature_stack.npy'
    path.unlink()
    if kind == 'directory':
        path.mkdir()
    else:
        path.symlink_to(workspace / 'not-downloaded')
    report = shared_tools.preflight()
    assert report['missing'] == ['.cache/gems_work/feature_stack.npy']
    assert not report['ready_for_shared_tools']


def test_nonempty_bytes_are_not_format_or_submission_approval(workspace):
    configure(workspace, 'assigned-lane')
    report = shared_tools.preflight()
    assert report['ready_for_shared_tools']
    assert report['ok_to_submit'] is False
    assert 'not format, provenance' in report['scope']
