"""Snapshot GitHub evidence. GitHub publications are NOT organizer receipts."""
import concurrent.futures
import datetime
import json
from pathlib import Path
import subprocess

SITES = [24, 25, 27, 28, 30, 31, 32, 33, 36]

def snapshot(number):
    repo = f"buffedlizard55-lab/GEMSDOE{number}"
    def api(path, raw=False):
        args = ['gh', 'api', path]
        if raw:
            args += ['-H', 'Accept: application/vnd.github.raw']
        return subprocess.check_output(args, text=True, timeout=90)
    try:
        commit = json.loads(api(f'repos/{repo}/commits/HEAD'))['sha']
        text = api(f'repos/{repo}/contents/README.md?ref={commit}', True)
        path = Path(f'evidence/sources/GEMSDOE{number}.md')
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return dict(site=f'GEMSDOE{number}', commit=commit, source=f'https://github.com/{repo}/blob/{commit}/README.md', status='retrieved', local=str(path))
    except (subprocess.SubprocessError, KeyError, ValueError) as e:
        return dict(site=f'GEMSDOE{number}', status='unavailable', error=str(e))

def main():
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        rows = list(pool.map(snapshot, SITES))
    out = dict(retrieved_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), classification='repository claims, not independently verified organizer results', sites=rows)
    Path('evidence/source_refresh.json').write_text(json.dumps(out, indent=2)+'\n')
    print(json.dumps(out, indent=2))

if __name__ == '__main__':
    main()
