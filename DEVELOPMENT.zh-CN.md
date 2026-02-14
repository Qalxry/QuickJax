# QuickJax 开发与维护手册

[English](DEVELOPMENT.md)

本文档面向后续开发者和维护者，详细描述 QuickJax 的架构设计、技术决策、已知问题及排障方法。

---

## 目录

1. [项目概览](#1-项目概览)
2. [目录结构](#2-目录结构)
3. [架构与数据流](#3-架构与数据流)
4. [JavaScript 层详解](#4-javascript-层详解)
5. [Python 层详解](#5-python-层详解)
6. [构建流程](#6-构建流程)
7. [关键技术决策与踩坑记录](#7-关键技术决策与踩坑记录)
8. [测试](#8-测试)
9. [发布与打包](#9-发布与打包)
10. [常见问题排障](#10-常见问题排障)
11. [扩展指南](#11-扩展指南)

---

## 1. 项目概览

QuickJax 是一个纯 Python MathJax v4 渲染器。

**核心思路**：将 MathJax v4 的全部代码（含字体数据）打包成一个 ~4.1 MB 的 JavaScript bundle，然后通过 Python 的 `quickjs` C 扩展在进程内运行。LaTeX → SVG 的全过程在 Python 进程的内存中完成，无需 Node.js 运行时或 subprocess 调用。

**技术栈**：

| 组件 | 技术 | 版本 |
|------|------|------|
| JS 渲染引擎 | MathJax (`mathjax-full`) | 4.0.0-beta.7 |
| 字体数据 | `mathjax-modern-font` | 随 mathjax-full 自动安装 |
| JS 引擎（嵌入） | QuickJS（通过 `quickjs` Python 库） | 1.19.4+ |
| JS 打包器 | esbuild | 0.20+ |
| DOM 模拟 | MathJax `liteAdaptor` | — |

---

## 2. 目录结构

```
QuickJax/
├── quickjax/                   # Python 包（发布到 PyPI 的内容）
│   ├── __init__.py             # 导出 API：render, MathJaxRenderer, MathJaxRenderError
│   ├── backend.py              # 核心实现：QuickJS 上下文管理 + 渲染调用
│   └── js/
│       └── mathjax_bundle.js   # 预构建的 MathJax IIFE bundle (~4.1 MB)
│
├── renderer_src/               # JS 源码（仅构建时使用，不随 pip 分发）
│   ├── index.js                # JS 入口文件：初始化 MathJax + 暴露 render API
│   ├── package.json            # npm 依赖声明
│   └── node_modules/           # npm install 后生成（.gitignore 忽略）
│
├── tests/
│   └── test_render.py          # pytest 测试套件（13 个测试）
│
├── build_bundle.sh             # 一键构建脚本
├── demo.py                     # 155 个 LaTeX 表达式的渲染演示
├── pyproject.toml              # Python 包配置
├── SPECS.md                    # 原始技术需求文档
├── README.md                   # 用户面向的文档
├── DEVELOPMENT.md              # 本文件
└── .gitignore
```

---

## 3. 架构与数据流

```
用户调用
  │
  ▼
quickjax.render(r"\frac{a}{b}")          ← Python 公开 API
  │
  ▼
MathJaxRenderer.render()                 ← backend.py
  │  json.dumps(latex) → JS 字符串字面量
  │  构造表达式: globalThis.render("\\frac{a}{b}")
  │
  ▼
quickjs.Context.eval(js_expr)            ← quickjs C 扩展调用 QuickJS
  │
  ▼
globalThis.render(latex)                 ← mathjax_bundle.js 中的函数
  │
  ▼
MathJax TeX → MathML → SVG pipeline     ← mathjax-full 内部
  │  TeX input parser → 内部 MathML 树
  │  SVG output jax → liteAdaptor 虚拟 DOM → SVG 节点
  │
  ▼
extractSvg(containerNode)               ← 从 <mjx-container> 中提取 <svg>
  │
  ▼
返回 "<svg ...>...</svg>"                → 回到 Python 作为 str 返回
```

**关键洞察**：MathJax 的 `convert()` 方法返回一个 `<mjx-container>` 虚拟 DOM 节点，里面包含实际的 `<svg>` 子节点。我们在 JS 层通过 `extractSvg()` 函数只提取 `<svg>` 部分，确保输出是一个合法的 SVG 文档。

---

## 4. JavaScript 层详解

### 4.1 入口文件 `renderer_src/index.js`

文件分为以下几个逻辑部分：

#### 4.1.1 MathJax 核心导入

```js
import { mathjax } from "mathjax-full/mjs/mathjax.js";
import { TeX } from "mathjax-full/mjs/input/tex.js";
import { SVG } from "mathjax-full/mjs/output/svg.js";
import { liteAdaptor } from "mathjax-full/mjs/adaptors/liteAdaptor.js";
import { RegisterHTMLHandler } from "mathjax-full/mjs/handlers/html.js";
```

**注意**：MathJax v4 beta 使用 `mjs/` 目录（ESM 格式），不是 `js/`。如果未来 MathJax 发布正式版，路径可能变化。

#### 4.1.2 TeX 扩展导入（23 个）

每个扩展通过导入其 `*Configuration.js` 文件来完成自注册。MathJax v4 beta 没有 `AllPackages` 统一导出，所以必须逐个导入。

当前加载的扩展：
`ams`, `newcommand`, `boldsymbol`, `braket`, `cancel`, `color`, `enclose`, `extpfeil`, `html`, `mhchem`, `noerrors`, `noundefined`, `physics`, `mathtools`, `amscd`, `action`, `bbox`, `unicode`, `verb`, `textmacros`, `textcomp`, `cases`

#### 4.1.3 动态字体文件预加载（26 个）

MathJax v4 的字体数据按需动态加载。在浏览器中这是异步的，但 QuickJS 是纯同步引擎，不支持 `Promise`。MathJax 在碰到未加载的字体时会抛出 `retryAfter()` 异常，导致渲染失败。

**解决方案**：在 bundle 时静态导入所有 26 个动态字体文件，然后：

```js
mathjax.asyncLoad = (name) => {};         // 禁用异步加载（no-op）
mathjax.asyncIsSynchronous = true;        // 告知 MathJax 异步操作实际是同步的
svgOutput.font.loadDynamicFilesSync();    // 同步加载所有已导入的字体数据
```

这是 bundle 从 1.2 MB 增长到 4.1 MB 的主要原因——字体路径数据约占 3 MB。

#### 4.1.4 MathJax 文档初始化

```js
const texInput = new TeX({ packages });
const svgOutput = new SVG({
  fontCache: "local",                    // SVG 内嵌 <defs> 字体路径
  linebreaks: { inline: false },         // 禁用行内公式自动换行
});
const htmlDoc = mathjax.document("", {
  InputJax: texInput,
  OutputJax: svgOutput,
});
```

- `fontCache: "local"` 确保每个 SVG 携带自己的 `<defs>` 字体定义，无需外部文件。
- `linebreaks: { inline: false }` 禁用 MathJax v4 默认启用的行内数学自动换行功能。若不禁用，行内公式可能被拆成多个 `<svg>` 元素。

#### 4.1.5 渲染函数

```js
function extractSvg(containerNode) {
  const children = adaptor.childNodes(containerNode);
  for (const child of children) {
    if (adaptor.kind(child) === "svg") {
      return adaptor.outerHTML(child);
    }
  }
  return adaptor.innerHTML(containerNode);
}

globalThis.render = function render(latex) {
  const node = htmlDoc.convert(latex, { display: true, containerWidth: 1e7 });
  return extractSvg(node);
};
```

- `containerWidth: 1e7` 设置一个极大的容器宽度，进一步避免任何潜在的换行。
- `extractSvg()` 遍历 `<mjx-container>` 的子节点找到 `<svg>`，只返回纯 SVG 标记。

### 4.2 npm 依赖

```json
{
  "dependencies": {
    "mathjax-full": "4.0.0-beta.7"
  },
  "devDependencies": {
    "esbuild": "^0.20.0"
  }
}
```

> **重要**：`mathjax-full` 使用精确版本号 `4.0.0-beta.7` 而非范围匹配。MathJax v4 尚未发布稳定版，beta 版本之间可能存在不兼容变更。升级时务必全面测试。

---

## 5. Python 层详解

### 5.1 `backend.py` — MathJaxRenderer 类

#### QuickJS 上下文配置

```python
self._ctx = quickjs.Context()
self._ctx.set_max_stack_size(4 * 1024 * 1024)   # 4 MB 栈
self._ctx.set_memory_limit(128 * 1024 * 1024)    # 128 MB 堆
```

- **4 MB 栈**：MathJax bundle 评估（`eval`）时调用栈较深，默认栈大小不够。
- **128 MB 堆**：MathJax 初始化后常驻约 30-50 MB，留有余量。

#### LaTeX 转义

```python
escaped = json.dumps(latex)  # "E = mc^2" → '"E = mc^2"'
```

使用 `json.dumps()` 生成合法的 JS 字符串字面量，自动处理反斜杠、引号等特殊字符的转义。

#### 异常处理

JS 层的 `throw new Error(...)` 会被 QuickJS 捕获为 Python 异常，再包装为 `MathJaxRenderError`。

### 5.2 `__init__.py` — 公开 API

导出三个名字：`MathJaxRenderer`、`MathJaxRenderError`、`render`。

模块级 `render()` 函数使用懒加载单例模式——首次调用时创建 `MathJaxRenderer` 实例（耗时约 0.3 秒），后续调用复用。

---

## 6. 构建流程

### 6.1 `build_bundle.sh`

```bash
cd renderer_src
npm install --silent                    # 安装 mathjax-full + esbuild
npx esbuild index.js \
  --bundle \                            # 将所有 import 打包
  --minify \                            # 压缩代码
  --platform=browser \                  # 不引入 Node.js 内置模块
  --format=iife \                       # 自执行函数格式（非 ESM）
  --outfile=../quickjax/js/mathjax_bundle.js
```

**关键参数解释**：

| 参数 | 原因 |
|------|------|
| `--platform=browser` | QuickJS 没有 `fs`、`path` 等 Node 模块，用 browser platform 避免 esbuild 注入 polyfill |
| `--format=iife` | QuickJS 不支持 ESM 的 `import`/`export`，必须打包为 IIFE |
| `--minify` | 从 ~12 MB 压缩到 ~4.1 MB |

### 6.2 何时需要重新构建

- 修改了 `renderer_src/index.js`
- 升级了 `mathjax-full` 版本
- 添加/移除 TeX 扩展或字体文件

重新构建后，生成的 `quickjax/js/mathjax_bundle.js` 会被 Git 追踪，确保 `pip install` 时无需 Node.js。

---

## 7. 关键技术决策与踩坑记录

### 7.1 MathJax v4 版本选择

**问题**：npm 上 `mathjax-full@^4.0.0` 不存在。截至开发时，最新版是 `4.0.0-beta.7`。

**决策**：使用精确版本 `4.0.0-beta.7`。

**后果**：MathJax v4 正式版发布后需要测试兼容性，可能需要调整导入路径。

### 7.2 ESM 目录：`mjs/` vs `js/`

**问题**：MathJax v4 beta 的 ESM 模块在 `mjs/` 目录下，而非文档中常见的 `js/`。

**解决**：所有导入路径使用 `mathjax-full/mjs/...`。

### 7.3 无 AllPackages 统一导出

**问题**：MathJax v3 的 `AllPackages` 在 v4 beta 中不存在。

**解决**：手动导入 23 个扩展的 Configuration 文件。每个文件导入后会自动注册到 MathJax 的扩展系统中。

### 7.4 动态字体加载与 QuickJS 同步限制

**问题**：MathJax v4 按需加载字体（`\mathbb`、`\mathfrak` 等触发）。加载机制使用 `retryAfter(asyncFunction)` — 本质上是一个异步重试模式。QuickJS 不支持异步操作。

**表现**：渲染 `\mathbb{R}` 时抛出 "MathJax retry" 或类似错误。

**解决**：
1. 在 bundle 中静态导入全部 26 个动态字体文件（它们会在模块加载时自注册到字体注册表）。
2. 设置 `mathjax.asyncLoad` 为空函数、`mathjax.asyncIsSynchronous = true`。
3. 调用 `svgOutput.font.loadDynamicFilesSync()` 将所有字体数据同步加载到内存。

**代价**：bundle 从 1.2 MB → 4.1 MB（字体路径数据约 3 MB）。

### 7.5 `<mjx-container>` 包装与行内换行

**问题**：MathJax 的 `convert()` 返回 `<mjx-container>` 虚拟节点，而不是纯 `<svg>`。此外 v4 默认开启行内数学自动换行（`linebreaks.inline: true`），导致一个行内公式被拆分成多个 `<svg>` 元素。

**解决**：
1. `SVG` 构造参数添加 `linebreaks: { inline: false }` 禁用行内换行。
2. JS 中 `extractSvg()` 函数从容器节点中提取第一个 `<svg>` 子元素。
3. `containerWidth: 1e7` 作为额外保险，设置极大容器宽度。

### 7.6 文件名大小写敏感

**问题**：`TextmacrosConfiguration.js` — 实际文件名是 `TextMacrosConfiguration.js`（大写 M）。在 Linux 上导入路径大小写敏感，导致构建失败。

**解决**：修正为正确的大小写。

---

## 8. 测试

### 8.1 单元测试

```bash
pytest tests/ -v
```

13 个测试覆盖：

| 测试类 | 测试内容 |
|--------|----------|
| `TestBasicRender` | 基本公式、行内模式、分数、积分、矩阵 |
| `TestSVGSelfContained` | 无外部 href 引用、SVG 标签存在 |
| `TestContextReuse` | 多次渲染复用上下文，结果正确且互不相同 |
| `TestEscaping` | 反斜杠、花括号、引号等特殊字符 |
| `TestConvenienceFunction` | 模块级 `render()` 函数 + 行内模式 |

### 8.2 Demo 测试

```bash
python demo.py
```

`demo.py` 包含 25 个类别共 155 个 LaTeX 表达式的渲染测试，覆盖：算术、希腊字母、微积分、线性代数、集合论、逻辑、统计、mhchem 化学方程式、physics 宏、字体命令 (`\mathbb`, `\mathfrak`, `\mathcal`)、大型公式等。

---

## 9. 发布与打包

### 9.1 构建分发包

```bash
# 确保 bundle 已构建
bash build_bundle.sh

# 构建 sdist + wheel
pip install build
python -m build
```

`pyproject.toml` 中的配置确保 `quickjax/js/mathjax_bundle.js` 被包含在 wheel 中：

```toml
[tool.setuptools.package-data]
quickjax = ["js/*.js"]
```

### 9.2 发布到 PyPI

```bash
pip install twine
twine upload dist/*
```

### 9.3 版本管理

版本号定义在两个位置，更新时需同步：
- `pyproject.toml` → `version = "0.1.0"`
- `quickjax/__init__.py` → `__version__ = "0.1.0"`

---

## 10. 常见问题排障

### "MathJax retry" 错误

**原因**：某个字体文件未被预加载。

**排查**：
1. 检查错误消息中提到的字体名称。
2. 在 `node_modules/mathjax-modern-font/mjs/svg/dynamic/` 下查找对应文件。
3. 在 `index.js` 中添加对应的 `import` 语句。
4. 重新运行 `bash build_bundle.sh`。

### QuickJS 栈溢出

**原因**：4 MB 栈空间不足。

**解决**：在 `backend.py` 中增大 `set_max_stack_size` 的值。

### QuickJS 内存不足

**原因**：128 MB 堆空间不足（极其罕见）。

**解决**：在 `backend.py` 中增大 `set_memory_limit` 的值。

### 新 TeX 命令不被识别

**原因**：对应的 TeX 扩展未被加载。

**解决**：
1. 查找该命令属于哪个 MathJax TeX 扩展。
2. 在 `index.js` 中添加 `import "mathjax-full/mjs/input/tex/<ext>/<Ext>Configuration.js"` 导入。
3. 在 `packages` 数组中添加扩展名。
4. 重新构建。

### SVG 输出为空或格式异常

**排查步骤**：
1. 检查 JS 层是否正常：`python -c "from quickjax import MathJaxRenderer; r = MathJaxRenderer(); print(r.render(r'x^2'))"`
2. 确认输出以 `<svg` 开头、以 `</svg>` 结尾。
3. 如果输出为空的 `<svg></svg>`，可能是 `fontCache` 设置问题。

---

## 11. 扩展指南

### 添加新的 TeX 扩展

1. 确认扩展在 `mathjax-full` 中可用：检查 `node_modules/mathjax-full/mjs/input/tex/` 下是否存在对应目录。
2. 在 `index.js` 中添加 `import` 语句。
3. 在 `packages` 数组中添加扩展标识符。
4. 重新构建并测试。

### 升级 MathJax 版本

1. 修改 `renderer_src/package.json` 中的 `mathjax-full` 版本号。
2. 删除 `renderer_src/node_modules/` 和 `renderer_src/package-lock.json`。
3. 运行 `bash build_bundle.sh`。
4. 运行 `pytest tests/ -v` 和 `python demo.py` 验证。
5. **特别注意**：
   - MathJax 正式 v4 可能将 `mjs/` 改为 `js/`，检查导入路径。
   - 字体包名可能从 `mathjax-modern-font` 变更，检查 `package.json` 中的实际依赖关系。
   - `AllPackages` 可能在正式版中恢复，届时可以简化扩展导入。

### 支持 MathML 输入（未来可选）

MathJax 同时支持 MathML 输入。如有需要：

1. 在 `index.js` 中导入 `MathML` input jax。
2. 创建新的 `mathjax.document` 或替换 `texInput`。
3. 暴露新的 `globalThis.renderMathML(mml)` 函数。
4. 在 Python 层添加对应的 API。

### 调整 QuickJS 资源限制

如果渲染极复杂的公式时遇到资源限制：

```python
# backend.py 中修改
self._ctx.set_max_stack_size(8 * 1024 * 1024)   # 8 MB 栈
self._ctx.set_memory_limit(256 * 1024 * 1024)    # 256 MB 堆
```

---

## 附录：文件校验

| 文件 | 用途 | 大小（参考） |
|------|------|------------|
| `quickjax/js/mathjax_bundle.js` | 预构建 JS bundle | ~4.1 MB |
| `renderer_src/index.js` | JS 源码入口 | ~4 KB |
| `quickjax/backend.py` | Python 核心实现 | ~3 KB |
| `quickjax/__init__.py` | 包导出 | ~0.2 KB |
| `tests/test_render.py` | 测试套件 | ~3 KB |
| `demo.py` | 渲染演示 | ~6 KB |
