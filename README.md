# QuickJax

[中文](README.zh-CN.md)

**Zero-dependency MathJax v4 SVG renderer for Python, powered by QuickJS.**

QuickJax lets you convert LaTeX math expressions to self-contained SVG strings entirely within your Python process — no Node.js, no subprocess calls, no network requests.

## Features

- **Pure in-process rendering** — MathJax v4 runs inside an embedded QuickJS engine via the [`quickjs`](https://pypi.org/project/quickjs/) Python library.
- **Self-contained SVG output** — Every rendered SVG carries its own font glyphs (`fontCache: "local"`); no external CSS or fonts required.
- **23 TeX extensions** included out of the box: AMS, physics, mhchem, mathtools, braket, cancel, color, and more.
- **Display & inline modes** supported.
- **Python 3.8+** compatible.

## Installation

```bash
pip install quickjax
```

> The only runtime dependency is the `quickjs` package (a C extension embedding the QuickJS engine, about 2 MB in size). No Node.js installation is needed.

## Quick Start

```python
from quickjax import render

# Display mode (default)
svg = render(r"E = mc^2")

# Inline mode
svg = render(r"\alpha + \beta", display=False)

# Write to file
with open("equation.svg", "w") as f:
    f.write(svg)
```

### Using the Renderer Class

For batch rendering, instantiate `MathJaxRenderer` once to amortize the JS context creation (~0.3 s):

```python
from quickjax import MathJaxRenderer

renderer = MathJaxRenderer()

expressions = [
    r"\int_0^\infty e^{-x}\,dx = 1",
    r"\nabla \times \mathbf{E} = -\frac{\partial \mathbf{B}}{\partial t}",
    r"\mathbb{R}^n",
]

for i, expr in enumerate(expressions):
    svg = renderer.render(expr)
    with open(f"eq_{i}.svg", "w") as f:
        f.write(svg)
```

## API Reference

### `render(latex, *, display=True) -> str`

Module-level convenience function. Creates a shared `MathJaxRenderer` lazily on first call.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `latex` | `str` | — | LaTeX expression (without `$` delimiters) |
| `display` | `bool` | `True` | `True` for display mode, `False` for inline |

**Returns:** A self-contained `<svg>…</svg>` string.

**Raises:** `MathJaxRenderError` if the expression cannot be rendered.

### `class MathJaxRenderer`

| Method | Description |
|--------|-------------|
| `__init__()` | Load the MathJax JS bundle into a QuickJS context. |
| `render(latex, *, display=True) -> str` | Render LaTeX to SVG. Same parameters as the module-level function. |

Supports use as a context manager (`with MathJaxRenderer() as r: …`).

### `class MathJaxRenderError`

Subclass of `Exception`. Raised when MathJax cannot parse or render the given LaTeX input.

## Supported TeX Extensions

`ams` · `newcommand` · `boldsymbol` · `braket` · `cancel` · `color` · `enclose` · `extpfeil` · `html` · `mhchem` · `noerrors` · `noundefined` · `physics` · `mathtools` · `amscd` · `action` · `bbox` · `unicode` · `verb` · `textmacros` · `textcomp` · `cases`

## Development

### Prerequisites

- Python 3.8+
- Node.js (build-time only, for bundling MathJax)
- `esbuild` (installed automatically via npm)

### Building the JS Bundle

```bash
bash build_bundle.sh
```

This runs `npm install` in `renderer_src/` and produces `quickjax/js/mathjax_bundle.js` (~4.1 MB minified).

### Running Tests

```bash
pip install pytest
pytest tests/ -v
```

## How It Works

1. **Build time** — `esbuild` bundles MathJax v4 (`mathjax-full@4.0.0-beta.7`) plus all 26 dynamic font files from `mathjax-modern-font` into a single IIFE JavaScript file.
2. **Runtime** — `MathJaxRenderer.__init__()` creates a QuickJS context (4 MB stack / 128 MB heap) and evaluates the bundle once.
3. **Render** — Each `render()` call invokes `globalThis.render(latex)` inside that context. MathJax's `liteAdaptor` provides a virtual DOM; the SVG output is extracted and returned as a pure `<svg>` string.

## License

MIT
