"""OpenBB Platform extension registration for ``openbb_quant``.

The ``QuantExtension`` class is discovered via the
``openbb_extension`` entry-point group declared in ``pyproject.toml``;
its ``router`` attribute is the FastAPI router that OpenBB mounts into
its main application.
"""

from __future__ import annotations

from openbb_quant.router import router


class QuantExtension:
    """OpenBB router extension for the quant-api-gateway proxy."""

    router = router
