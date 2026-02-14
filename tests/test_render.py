"""Tests for quickjax renderer."""

import pytest

from quickjax import MathJaxRenderError, MathJaxRenderer, render


# ------------------------------------------------------------------ #
# Fixture: shared renderer instance (expensive to create)
# ------------------------------------------------------------------ #

@pytest.fixture(scope="module")
def renderer():
    return MathJaxRenderer()


# ------------------------------------------------------------------ #
# Basic rendering
# ------------------------------------------------------------------ #

class TestBasicRender:
    def test_simple_equation(self, renderer):
        svg = renderer.render(r"E = mc^2")
        assert "<mjx-container" in svg
        assert "<svg" in svg
        assert "</svg>" in svg

    def test_inline_mode(self, renderer):
        svg = renderer.render(r"x^2", display=False)
        assert "<svg" in svg

    def test_fraction(self, renderer):
        svg = renderer.render(r"\frac{a}{b}")
        assert "<svg" in svg

    def test_integral(self, renderer):
        svg = renderer.render(r"\int_0^\infty e^{-x} \, dx")
        assert "<svg" in svg

    def test_matrix(self, renderer):
        svg = renderer.render(r"\begin{pmatrix} a & b \\ c & d \end{pmatrix}")
        assert "<svg" in svg


# ------------------------------------------------------------------ #
# SVG self-containedness
# ------------------------------------------------------------------ #

class TestSVGSelfContained:
    def test_no_external_href(self, renderer):
        svg = renderer.render(r"\sum_{i=1}^{n} x_i")
        # Should not reference external resources (xmlns declarations are fine)
        import re
        # Strip xmlns declarations before checking for external URLs
        stripped = re.sub(r'xmlns(?::xlink)?="[^"]*"', '', svg)
        assert "http://" not in stripped
        assert "https://" not in stripped

    def test_contains_svg_tag(self, renderer):
        svg = renderer.render(r"a^2 + b^2 = c^2")
        assert "<svg" in svg


# ------------------------------------------------------------------ #
# Multiple renders (context reuse)
# ------------------------------------------------------------------ #

class TestContextReuse:
    def test_multiple_renders(self, renderer):
        expressions = [
            r"x^2",
            r"\alpha + \beta",
            r"\sqrt{2}",
            r"\lim_{x \to 0} \frac{\sin x}{x} = 1",
        ]
        results = [renderer.render(expr) for expr in expressions]
        assert all("<svg" in r for r in results)
        # Each result should be distinct
        assert len(set(results)) == len(results)


# ------------------------------------------------------------------ #
# Special characters / escaping
# ------------------------------------------------------------------ #

class TestEscaping:
    def test_backslash_heavy(self, renderer):
        svg = renderer.render(r"\alpha \beta \gamma \delta")
        assert "<svg" in svg

    def test_curly_braces(self, renderer):
        svg = renderer.render(r"x^{10}")
        assert "<svg" in svg

    def test_quotes_in_latex(self, renderer):
        svg = renderer.render(r'\text{He said "hello"}')
        assert "<svg" in svg


# ------------------------------------------------------------------ #
# Module-level convenience function
# ------------------------------------------------------------------ #

class TestConvenienceFunction:
    def test_render_function(self):
        svg = render(r"x + y = z")
        assert "<svg" in svg

    def test_render_inline(self):
        svg = render(r"x + y", display=False)
        assert "<svg" in svg
