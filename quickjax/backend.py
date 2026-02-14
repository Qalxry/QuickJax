"""QuickJax: Zero-dependency MathJax v4 renderer powered by QuickJS."""

import json
import os
from pathlib import Path

import quickjs


class MathJaxRenderError(Exception):
    """Raised when MathJax fails to render a LaTeX expression."""
    pass


class MathJaxRenderer:
    """MathJax v4 SVG renderer backed by an embedded QuickJS engine.

    The bundled MathJax JavaScript is loaded once on initialization.
    Subsequent ``render`` calls reuse the same JS context for speed.

    Usage::

        renderer = MathJaxRenderer()
        svg = renderer.render(r"E = mc^2")
    """

    _JS_BUNDLE = Path(__file__).parent / "js" / "mathjax_bundle.js"

    def __init__(self) -> None:
        js_code = self._JS_BUNDLE.read_text(encoding="utf-8")

        self._ctx = quickjs.Context()
        # Give QuickJS enough room for the ~1.2 MB MathJax bundle
        self._ctx.set_max_stack_size(4 * 1024 * 1024)   # 4 MB stack
        self._ctx.set_memory_limit(128 * 1024 * 1024)    # 128 MB heap

        try:
            self._ctx.eval(js_code)
        except Exception as exc:
            raise MathJaxRenderError(
                f"Failed to initialize MathJax JS context: {exc}"
            ) from exc

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def render(self, latex: str, *, display: bool = True) -> str:
        """Render a LaTeX string to SVG markup.

        Parameters
        ----------
        latex:
            The LaTeX expression (without surrounding ``$`` delimiters).
        display:
            If *True* (default), render in display mode; otherwise inline.

        Returns
        -------
        str
            A self-contained ``<svg …>…</svg>`` string.

        Raises
        ------
        MathJaxRenderError
            If MathJax cannot parse / render the expression.
        """
        escaped = json.dumps(latex)  # produces a safe JS string literal
        func = "render" if display else "renderInline"
        js_expr = f"globalThis.{func}({escaped})"

        try:
            result = self._ctx.eval(js_expr)
        except Exception as exc:
            raise MathJaxRenderError(
                f"MathJax render failed for input {escaped}: {exc}"
            ) from exc

        if not isinstance(result, str):
            raise MathJaxRenderError(
                f"Expected string from JS render, got {type(result).__name__}"
            )
        return result

    # ------------------------------------------------------------------ #
    # Context-manager support
    # ------------------------------------------------------------------ #

    def __enter__(self) -> "MathJaxRenderer":
        return self

    def __exit__(self, *_: object) -> None:
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"


# ====================================================================== #
# Module-level convenience API (lazy singleton)
# ====================================================================== #

_default_renderer: MathJaxRenderer | None = None


def _get_renderer() -> MathJaxRenderer:
    global _default_renderer
    if _default_renderer is None:
        _default_renderer = MathJaxRenderer()
    return _default_renderer


def render(latex: str, *, display: bool = True) -> str:
    """Render *latex* to a self-contained SVG string.

    This is a convenience wrapper around :class:`MathJaxRenderer`.  The
    underlying JS context is created lazily on the first call and reused
    thereafter.
    """
    return _get_renderer().render(latex, display=display)
