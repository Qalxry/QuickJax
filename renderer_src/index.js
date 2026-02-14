import { mathjax } from "mathjax-full/mjs/mathjax.js";
import { TeX } from "mathjax-full/mjs/input/tex.js";
import { SVG } from "mathjax-full/mjs/output/svg.js";
import { liteAdaptor } from "mathjax-full/mjs/adaptors/liteAdaptor.js";
import { RegisterHTMLHandler } from "mathjax-full/mjs/handlers/html.js";

// Import common TeX extension packages so they register themselves
import "mathjax-full/mjs/input/tex/ams/AmsConfiguration.js";
import "mathjax-full/mjs/input/tex/newcommand/NewcommandConfiguration.js";
import "mathjax-full/mjs/input/tex/boldsymbol/BoldsymbolConfiguration.js";
import "mathjax-full/mjs/input/tex/braket/BraketConfiguration.js";
import "mathjax-full/mjs/input/tex/cancel/CancelConfiguration.js";
import "mathjax-full/mjs/input/tex/color/ColorConfiguration.js";
import "mathjax-full/mjs/input/tex/enclose/EncloseConfiguration.js";
import "mathjax-full/mjs/input/tex/extpfeil/ExtpfeilConfiguration.js";
import "mathjax-full/mjs/input/tex/html/HtmlConfiguration.js";
import "mathjax-full/mjs/input/tex/mhchem/MhchemConfiguration.js";
import "mathjax-full/mjs/input/tex/noerrors/NoErrorsConfiguration.js";
import "mathjax-full/mjs/input/tex/noundefined/NoUndefinedConfiguration.js";
import "mathjax-full/mjs/input/tex/physics/PhysicsConfiguration.js";
import "mathjax-full/mjs/input/tex/mathtools/MathtoolsConfiguration.js";
import "mathjax-full/mjs/input/tex/amscd/AmsCdConfiguration.js";
import "mathjax-full/mjs/input/tex/action/ActionConfiguration.js";
import "mathjax-full/mjs/input/tex/bbox/BboxConfiguration.js";
import "mathjax-full/mjs/input/tex/unicode/UnicodeConfiguration.js";
import "mathjax-full/mjs/input/tex/verb/VerbConfiguration.js";
import "mathjax-full/mjs/input/tex/textmacros/TextMacrosConfiguration.js";
import "mathjax-full/mjs/input/tex/textcomp/TextcompConfiguration.js";
import "mathjax-full/mjs/input/tex/cases/CasesConfiguration.js";

// Pre-load ALL dynamic font files to avoid async retryAfter errors in QuickJS
import "mathjax-modern-font/mjs/svg/dynamic/accents.js";
import "mathjax-modern-font/mjs/svg/dynamic/accents-b-i.js";
import "mathjax-modern-font/mjs/svg/dynamic/arrows.js";
import "mathjax-modern-font/mjs/svg/dynamic/calligraphic.js";
import "mathjax-modern-font/mjs/svg/dynamic/double-struck.js";
import "mathjax-modern-font/mjs/svg/dynamic/fraktur.js";
import "mathjax-modern-font/mjs/svg/dynamic/latin.js";
import "mathjax-modern-font/mjs/svg/dynamic/latin-b.js";
import "mathjax-modern-font/mjs/svg/dynamic/latin-bi.js";
import "mathjax-modern-font/mjs/svg/dynamic/latin-i.js";
import "mathjax-modern-font/mjs/svg/dynamic/math.js";
import "mathjax-modern-font/mjs/svg/dynamic/monospace.js";
import "mathjax-modern-font/mjs/svg/dynamic/monospace-ex.js";
import "mathjax-modern-font/mjs/svg/dynamic/monospace-l.js";
import "mathjax-modern-font/mjs/svg/dynamic/PUA.js";
import "mathjax-modern-font/mjs/svg/dynamic/sans-serif.js";
import "mathjax-modern-font/mjs/svg/dynamic/sans-serif-b.js";
import "mathjax-modern-font/mjs/svg/dynamic/sans-serif-bi.js";
import "mathjax-modern-font/mjs/svg/dynamic/sans-serif-ex.js";
import "mathjax-modern-font/mjs/svg/dynamic/sans-serif-i.js";
import "mathjax-modern-font/mjs/svg/dynamic/sans-serif-r.js";
import "mathjax-modern-font/mjs/svg/dynamic/script.js";
import "mathjax-modern-font/mjs/svg/dynamic/shapes.js";
import "mathjax-modern-font/mjs/svg/dynamic/symbols.js";
import "mathjax-modern-font/mjs/svg/dynamic/symbols-b-i.js";
import "mathjax-modern-font/mjs/svg/dynamic/variants.js";

// Set up synchronous font loading — all dynamic files are already bundled
// so asyncLoad is a no-op; we just need setup() to run on the font instance
mathjax.asyncLoad = (name) => {};
mathjax.asyncIsSynchronous = true;

// Initialize the lite adaptor (virtual DOM for non-browser environments)
const adaptor = liteAdaptor();

// Register the HTML handler with the adaptor
RegisterHTMLHandler(adaptor);

// Define the list of packages to load
const packages = [
  "base", "ams", "newcommand", "boldsymbol", "braket", "cancel",
  "color", "enclose", "extpfeil", "html", "mhchem", "noerrors",
  "noundefined", "physics", "mathtools", "amscd", "action", "bbox",
  "unicode", "verb", "textmacros", "textcomp", "cases",
];

// Create the MathJax document with TeX input and SVG output
const texInput = new TeX({ packages });
const svgOutput = new SVG({
  fontCache: "local",
  linebreaks: { inline: false },
});
const htmlDoc = mathjax.document("", {
  InputJax: texInput,
  OutputJax: svgOutput,
});

// Force synchronous loading of all dynamic font data into the font instance
// This prevents "MathJax retry" errors for \mathbb, \mathfrak, \mathcal, etc.
svgOutput.font.loadDynamicFilesSync();

/**
 * Extract the first <svg> child from a MathJax container node and return its
 * outerHTML serialized as valid XML (properly escaping &, <, > in attributes).
 * This strips the <mjx-container> wrapper and avoids multi-SVG line-breaking artifacts.
 */
function extractSvg(containerNode) {
  const children = adaptor.childNodes(containerNode);
  for (const child of children) {
    if (adaptor.kind(child) === "svg") {
      return adaptor.serializeXML(child);
    }
  }
  // Fallback: return the full container inner HTML
  return adaptor.innerHTML(containerNode);
}

/**
 * Render a LaTeX string to an SVG string.
 * @param {string} latex - The LaTeX expression to render.
 * @returns {string} The rendered SVG markup (a single self-contained <svg> element).
 */
globalThis.render = function render(latex) {
  try {
    const node = htmlDoc.convert(latex, { display: true, containerWidth: 1e7 });
    return extractSvg(node);
  } catch (e) {
    throw new Error("MathJax render error: " + (e.message || String(e)));
  }
};

/**
 * Render an inline LaTeX string to an SVG string.
 * @param {string} latex - The LaTeX expression to render.
 * @returns {string} The rendered SVG markup (a single self-contained <svg> element).
 */
globalThis.renderInline = function renderInline(latex) {
  try {
    const node = htmlDoc.convert(latex, { display: false, containerWidth: 1e7 });
    return extractSvg(node);
  } catch (e) {
    throw new Error("MathJax render error: " + (e.message || String(e)));
  }
};
