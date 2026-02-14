"""QuickJax — zero-dependency MathJax v4 SVG renderer for Python."""

__version__ = "0.1.0"

from .backend import MathJaxRenderError, MathJaxRenderer, render

__all__ = ["MathJaxRenderError", "MathJaxRenderer", "render", "__version__"]
