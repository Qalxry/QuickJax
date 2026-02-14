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
const svgOutput = new SVG({ fontCache: "local" });
const htmlDoc = mathjax.document("", {
  InputJax: texInput,
  OutputJax: svgOutput,
});

/**
 * Render a LaTeX string to an SVG string.
 * @param {string} latex - The LaTeX expression to render.
 * @returns {string} The rendered SVG markup.
 */
globalThis.render = function render(latex) {
  try {
    const node = htmlDoc.convert(latex, { display: true });
    const svg = adaptor.outerHTML(node);
    return svg;
  } catch (e) {
    throw new Error("MathJax render error: " + (e.message || String(e)));
  }
};

/**
 * Render an inline LaTeX string to an SVG string.
 * @param {string} latex - The LaTeX expression to render.
 * @returns {string} The rendered SVG markup.
 */
globalThis.renderInline = function renderInline(latex) {
  try {
    const node = htmlDoc.convert(latex, { display: false });
    const svg = adaptor.outerHTML(node);
    return svg;
  } catch (e) {
    throw new Error("MathJax render error: " + (e.message || String(e)));
  }
};
