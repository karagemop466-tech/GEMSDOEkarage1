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
    repo, commit = 'example/test-template', 'a' * 40
    (root / 'registry/template.json').write_text(json.dumps({
        'method_lane': lane, 'repository': repo, 'commit': commit,
        'canonical_template_assignment': {
            'method_lane': lane, 'repository': repo, 'commit': commit,
            'evidence': 'synthetic test assignment; not real authorization',
        },
    }))
    for name in ('feature_stack.npy', 'training_features.tif',
                 'sample_submission.tif', 'labels.tif', 'existing_faults.tif'):
        if name not in missing:
            folder = 'gems_work' if name.endswith('.npy') else 'gems_data'
            path = root / '.cache' / folder / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b'placeholder; not authenticated data')


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


@pytest.mark.parametrize('name', ['feature_stack.npy', 'training_features.tif',
                                  'sample_submission.tif', 'labels.tif', 'existing_faults.tif'])
def test_empty_input_blocks_execution(workspace, monkeypatch, name):
    configure(workspace, 'assigned-lane')
    folder = 'gems_work' if name.endswith('.npy') else 'gems_data'
    path = workspace / '.cache' / folder / name
    path.write_bytes(b'')
    report = shared_tools.preflight()
    assert report['empty'] == [str(path.relative_to(workspace))]
    assert not report['ready_for_shared_tools']
    monkeypatch.setattr(sys, 'argv', ['shared_tools.py', 'evaluate'])
    monkeypatch.setattr(shared_tools, 'bootstrap', lambda: pytest.fail('bootstrapped empty input'))
    with pytest.raises(SystemExit, match='empty'):
        shared_tools.main()

@pytest.mark.parametrize('change', [
    {'canonical_template_assignment': None},
    {'canonical_template_assignment': {}},
    {'canonical_template_assignment': {'method_lane': 'another-lane', 'repository': 'example/test-template',
                                       'commit': 'a' * 40, 'evidence': 'test'}},
    {'canonical_template_assignment': {'method_lane': 'assigned-lane', 'repository': 'other/template',
                                       'commit': 'a' * 40, 'evidence': 'test'}},
    {'canonical_template_assignment': {'method_lane': 'assigned-lane', 'repository': 'example/test-template',
                                       'commit': 'b' * 40, 'evidence': 'test'}},
    {'canonical_template_assignment': {'method_lane': 'assigned-lane', 'repository': 'example/test-template',
                                       'commit': 'a' * 40, 'evidence': '  '}},
    {'commit': 'main'},
    {'repository': '../template'},
])
def test_unresolved_or_inconsistent_template_assignment_blocks(workspace, change):
    configure(workspace, 'assigned-lane')
    path = workspace / 'registry/template.json'
    pin = json.loads(path.read_text())
    pin.update(change)
    path.write_text(json.dumps(pin))
    report = shared_tools.preflight()
    assert report['canonical_assignment_recorded'] is False
    assert report['ready_for_shared_tools'] is False
    assert report['ok_to_submit'] is False


@pytest.mark.parametrize('command', ['evaluate', 'write'])
def test_no_execution_with_unassigned_template_even_when_all_files_present(workspace, monkeypatch, command):
    configure(workspace, 'assigned-lane')
    path = workspace / 'registry/template.json'
    pin = json.loads(path.read_text())
    pin['canonical_template_assignment'] = None
    path.write_text(json.dumps(pin))
    monkeypatch.setattr(sys, 'argv', ['shared_tools.py', command])
    monkeypatch.setattr(shared_tools, 'bootstrap', lambda: pytest.fail('bootstrapped blocked run'))
    with pytest.raises(SystemExit, match='BLOCKED'):
        shared_tools.main()


@pytest.mark.parametrize('command,target', [('evaluate', 'evaluate_holdout.py'), ('write', 'submission_writer.py')])
def test_recorded_assignment_dispatches_but_does_not_authorize(workspace, monkeypatch, command, target):
    configure(workspace, 'assigned-lane')
    monkeypatch.setattr(shared_tools, 'TEMPLATE', workspace / '.work/template')
    monkeypatch.setattr(shared_tools, 'bootstrap', lambda: None)
    calls = []
    monkeypatch.setattr(shared_tools.subprocess, 'run', lambda *a, **kw: calls.append((a, kw)))
    monkeypatch.setattr(sys, 'argv', ['shared_tools.py', command, '--example', 'value'])
    assert shared_tools.main() is None
    args, kwargs = calls[0]
    assert args[0] == [sys.executable, str(workspace / '.work/template/scripts' / target), '--example', 'value']
    assert kwargs['check'] is True
    assert kwargs['env']['GEMS_DATA_DIR'] == str(workspace / '.cache/gems_data')
    assert kwargs['env']['GEMS_WORK_DIR'] == str(workspace / '.cache/gems_work')
    assert shared_tools.preflight()['ok_to_submit'] is False


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
