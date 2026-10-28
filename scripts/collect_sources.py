"""Pin public GitHub evidence; never interpret owner claims as organizer receipts."""
import base64
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
SITES = [24, 25, 27, 28, 30, 31, 32, 33, 36]


def _write_atomic(dest: Path, raw: bytes) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix='.' + dest.name + '.', suffix='.tmp', dir=dest.parent)
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, 'wb') as out:
            out.write(raw)
        os.chmod(tmp, 0o644)
        tmp.replace(dest)
    finally:
        tmp.unlink(missing_ok=True)


def parse_pinned_github_blob(name: str, url: str, rasters_root: Path) -> tuple[str, str, str, Path]:
    if (not isinstance(name, str) or not re.fullmatch(r'[A-Za-z0-9._-]+\.tif', name)
            or name in ('.', '..') or '..' in name):
        raise ValueError(f'Unsafe historical artifact filename: {name}')
    if not isinstance(url, str) or not url.startswith('https://github.com/'):
        raise ValueError(f'Unexpected historical artifact URL: {url}')
    parts = url.removeprefix('https://github.com/').split('/')
    if len(parts) < 5 or parts[2] != 'blob':
        raise ValueError(f'Artifact URL is not a GitHub blob link: {url}')
    repo, ref, path = '/'.join(parts[:2]), parts[3], '/'.join(parts[4:])
    if (not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repo)
            or any(seg in ('.', '..') for seg in repo.split('/'))):
        raise ValueError(f'Invalid repository in artifact URL: {repo}')
    if not re.fullmatch(r'[0-9a-f]{40}', ref):
        raise ValueError(f'Artifact URL must be pinned to a 40-hex commit SHA: {ref}')
    if '\\' in path or path.startswith('/') or any(seg in ('', '.', '..') for seg in path.split('/')):
        raise ValueError(f'Unsafe blob path in artifact URL: {path}')
    rasters_root.mkdir(parents=True, exist_ok=True)
    root_resolved = rasters_root.resolve()
    dest = (root_resolved / name).resolve()
    if not dest.is_relative_to(root_resolved):
        raise ValueError(f'Artifact destination escapes raster directory: {name}')
    return repo, ref, path, dest


def api(path):
    return json.loads(subprocess.check_output(['gh', 'api', path], text=True))


def content(repo, ref, path):
    d = api(f'repos/{repo}/contents/{path}?ref={ref}')
    if not d.get('content'):
        d = api(f'repos/{repo}/git/blobs/{d["sha"]}')
        if not d.get('content'):
            raise ValueError(f'No blob content: {repo}/{path}')
    return base64.b64decode(d['content'])


def collect(n):
    repo = f'buffedlizard55-lab/GEMSDOE{n}'
    ref = api(f'repos/{repo}/commits/HEAD')['sha']
    if not re.fullmatch(r'[0-9a-f]{40}', str(ref)):
        raise ValueError(f'Unpinned commit ref for {repo}: {ref}')
    raw = content(repo, ref, 'README.md')
    dest = ROOT / 'evidence' / 'sources' / f'GEMSDOE{n}-README.md'
    _write_atomic(dest, raw)
    return {'site': f'GEMSDOE{n}', 'repo': repo, 'ref': ref,
            'readme_sha256': hashlib.sha256(raw).hexdigest(),
            'source_url': f'https://github.com/{repo}/blob/{ref}/README.md'}


def main():
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        rows = list(pool.map(collect, SITES))
    # Historical artifact identities are extracted from a pinned source, not guessed.
    text = (ROOT / 'evidence/sources/GEMSDOE36-README.md').read_text()
    rasters_root = ROOT / '.research/rasters'
    for row in rows:
        line = next(x for x in text.splitlines() if x.startswith('| '+row['site']+' |'))
        match = re.search(r'\[([^]]+\.tif)\]\((https://github.com/[^)]+)\)', line)
        if not match:
            raise ValueError(f'Missing historical identity: {row["site"]}')
        name, url = match.groups()
        repo, ref, path, dest = parse_pinned_github_blob(name, url, rasters_root)
        raw = content(repo, ref, path)
        _write_atomic(dest, raw)
        row.update(artifact=name, artifact_url=url, artifact_ref=ref,
                   artifact_sha256=hashlib.sha256(raw).hexdigest(),
                   estimate=None, organizer_confirmed=None, submit=False)
    result = {'checked_at': datetime.now(timezone.utc).isoformat(),
              'scope': 'Nine historical artifacts, not all submissions or all current repository rasters',
              'sites': rows}
    _write_atomic(ROOT/'docs/data/sources.json', (json.dumps(result, indent=2, allow_nan=False)+'\n').encode('utf-8'))


if __name__ == '__main__':
    main()
