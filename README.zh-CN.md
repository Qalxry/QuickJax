# QuickJax

[English](README.md)

**零依赖的 Python MathJax v4 SVG 渲染器，由 QuickJS 驱动。**

QuickJax 允许你在 Python 进程内将 LaTeX 数学表达式转换为自包含的 SVG 字符串——无需 Node.js、无子进程调用、无网络请求。

## 特性

- **纯进程内渲染** — MathJax v4 通过 [`quickjs`](https://pypi.org/project/quickjs/) Python 库在嵌入式 QuickJS 引擎中运行。
- **自包含 SVG 输出** — 每个渲染的 SVG 携带自己的字体字形（`fontCache: "local"`），无需外部 CSS 或字体。
- **内置 23 个 TeX 扩展**：AMS、physics、mhchem、mathtools、braket、cancel、color 等。
- 支持**展示模式与行内模式**。
- 兼容 **Python 3.8+**。

## 安装

```bash
pip install quickjax
```

> 唯一的运行时依赖是 `quickjs` 包（一个嵌入 QuickJS 引擎的 C 扩展，仅 2MB 左右）。无需安装 Node.js。

## 快速开始

```python
from quickjax import render

# 展示模式（默认）
svg = render(r"E = mc^2")

# 行内模式
svg = render(r"\alpha + \beta", display=False)

# 写入文件
with open("equation.svg", "w") as f:
    f.write(svg)
```

### 使用 Renderer 类

批量渲染时，建议只实例化一次 `MathJaxRenderer` 以分摊 JS 上下文创建开销（约 0.3 秒）：

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

## API 参考

### `render(latex, *, display=True) -> str`

模块级便捷函数。首次调用时懒加载创建共享的 `MathJaxRenderer`。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `latex` | `str` | — | LaTeX 表达式（不含 `$` 定界符） |
| `display` | `bool` | `True` | `True` 为展示模式，`False` 为行内模式 |

**返回值：** 自包含的 `<svg>…</svg>` 字符串。

**异常：** 表达式无法渲染时抛出 `MathJaxRenderError`。

### `class MathJaxRenderer`

| 方法 | 说明 |
|------|------|
| `__init__()` | 将 MathJax JS bundle 加载到 QuickJS 上下文中。 |
| `render(latex, *, display=True) -> str` | 渲染 LaTeX 为 SVG。参数同模块级函数。 |

支持上下文管理器（`with MathJaxRenderer() as r: …`）。

### `class MathJaxRenderError`

`Exception` 的子类。当 MathJax 无法解析或渲染给定的 LaTeX 输入时抛出。

## 支持的 TeX 扩展

`ams` · `newcommand` · `boldsymbol` · `braket` · `cancel` · `color` · `enclose` · `extpfeil` · `html` · `mhchem` · `noerrors` · `noundefined` · `physics` · `mathtools` · `amscd` · `action` · `bbox` · `unicode` · `verb` · `textmacros` · `textcomp` · `cases`

## 开发

### 前置条件

- Python 3.8+
- Node.js（仅构建时需要，用于打包 MathJax）
- `esbuild`（通过 npm 自动安装）

### 构建 JS Bundle

```bash
bash build_bundle.sh
```

此脚本在 `renderer_src/` 中执行 `npm install`，并生成 `quickjax/js/mathjax_bundle.js`（约 4.1 MB 压缩后）。

### 运行测试

```bash
pip install pytest
pytest tests/ -v
```

## 工作原理

1. **构建时** — `esbuild` 将 MathJax v4（`mathjax-full@4.0.0-beta.7`）及 `mathjax-modern-font` 的全部 26 个动态字体文件打包为单一 IIFE JavaScript 文件。
2. **运行时** — `MathJaxRenderer.__init__()` 创建一个 QuickJS 上下文（4 MB 栈 / 128 MB 堆）并评估该 bundle 一次。
3. **渲染** — 每次 `render()` 调用在该上下文中执行 `globalThis.render(latex)`。MathJax 的 `liteAdaptor` 提供虚拟 DOM，SVG 输出被提取后以纯 `<svg>` 字符串返回。

## 许可证

MIT
