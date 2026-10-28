"""Retired GPC-Z uniqueness entrypoint.

The old implementation exempted calibration lattices, skipped missing files,
used sampled ranks and could claim uniqueness without a complete registry.
Those behaviors conflict with the literal protocol. Use the fail-closed
``gemskarage1.registry_audit`` adapter and shared ``gems57.uniqueness`` tools
instead, with a complete pinned index and a pre-placement surface check.
"""


def check(*_args, **_kwargs):
    raise RuntimeError('STOP: legacy GPC-Z uniqueness checker is retired; use the shared all-registry gate')
