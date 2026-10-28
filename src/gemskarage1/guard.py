"""Release stop for inherited experiment drivers with invalidated evidence."""

def stop_inherited_driver() -> None:
    """Never rerun or promote a lane after its literal duplicate stop.

    A future assigned lane requires a new entrypoint with pre-placement
    complete-registry comparison, the shared buffered holdout and fresh
    single-feature canaries. An environment switch would hide this stop and is
    intentionally not provided.
    """
    raise RuntimeError(
        'STOP: inherited candidates exceeded the literal registry overlap limit; '
        'their drivers cannot be rerun or promoted. The current prompt contains '
        'no assigned method paragraph. See evidence/prior_candidate_audit.json '
        'and knowledge/three-pass-review-2026-10-28.md.'
    )
