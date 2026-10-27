"""Pin public GitHub evidence; never interpret owner claims as organizer receipts."""
import base64
import concurrent.futures
import hashlib
import json
from pathlib import Path
import re
import subprocess
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
SITES = [24, 25, 27, 28, 30, 31, 32, 33, 36]


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
    raw = content(repo, ref, 'README.md')
    dest = ROOT / 'evidence' / 'sources' / f'GEMSDOE{n}-README.md'
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(raw)
    return {'site': f'GEMSDOE{n}', 'repo': repo, 'ref': ref,
            'readme_sha256': hashlib.sha256(raw).hexdigest(),
            'source_url': f'https://github.com/{repo}/blob/{ref}/README.md'}


def main():
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        rows = list(pool.map(collect, SITES))
    # Historical artifact identities are extracted from a pinned source, not guessed.
    text = (ROOT / 'evidence/sources/GEMSDOE36-README.md').read_text()
    for row in rows:
        line = next(x for x in text.splitlines() if x.startswith('| '+row['site']+' |'))
        match = re.search(r'\[([^]]+\.tif)\]\((https://github.com/[^)]+)\)', line)
        if not match:
            raise ValueError(f'Missing historical identity: {row["site"]}')
        name, url = match.groups()
        parts = url.removeprefix('https://github.com/').split('/')
        repo, ref, path = '/'.join(parts[:2]), parts[3], '/'.join(parts[4:])
        raw = content(repo, ref, path)
        dest = ROOT / '.research/rasters' / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(raw)
        row.update(artifact=name, artifact_url=url, artifact_ref=ref,
                   artifact_sha256=hashlib.sha256(raw).hexdigest(),
                   estimate=None, organizer_confirmed=None, submit=False)
    result = {'checked_at': datetime.now(timezone.utc).isoformat(),
              'scope': 'Nine historical artifacts, not all submissions or all current repository rasters',
              'sites': rows}
    (ROOT/'docs/data/sources.json').write_text(json.dumps(result, indent=2)+'\n')


if __name__ == '__main__':
    main()
