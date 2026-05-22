# QuickJax HTTP API 文档

> 将 LaTeX 数学表达式渲染为自包含 SVG 的 RESTful API 服务。
>
> 底层由 MathJax v4 + QuickJS 驱动，零外部依赖。

**协议：** HTTP/1.1  
**字符集：** UTF-8  
**Base URL：** `http://<host>:<port>`

---

## 目录

- [1. 健康检查](#1-健康检查)
- [2. 渲染 LaTeX（JSON 封装）](#2-渲染-latexjson-封装)
- [3. 渲染 LaTeX（GET 方式）](#3-渲染-latexget-方式)
- [4. 渲染 LaTeX（直接返回 SVG）](#4-渲染-latex直接返回-svg)
- [5. CORS 预检](#5-cors-预检)
- [6. 错误处理](#6-错误处理)
- [附录](#附录)

---

## 1. 健康检查

检查服务是否存活。

```
GET /health
```

### 请求示例

```bash
curl http://127.0.0.1:8000/health
```

### 响应

**`200 OK`**

```json
{
  "ok": true,
  "service": "quickjax",
  "version": "0.1.0"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `ok` | `boolean` | 服务状态 |
| `service` | `string` | 服务标识，固定 `"quickjax"` |
| `version` | `string` | 当前 API 版本号 |

---

## 2. 渲染 LaTeX（JSON 封装）

将 LaTeX 表达式渲染为 SVG，返回 JSON 格式（SVG 嵌套在 `svg` 字段中）。**推荐方式**，支持复杂表达式且无需 URL 编码。

```
POST /render
Content-Type: application/json
```

### 请求体

```json
{
  "latex": "E = mc^2",
  "display": true
}
```

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `latex` | `string` | **是** | — | LaTeX 数学表达式。也可使用字段名 `tex` 作为别名 |
| `display` | `boolean` | 否 | `true` | 渲染模式：`true` = 展示模式（块级），`false` = 行内模式 |

> **注意：** `latex` 字段值中**不应包含** `$` 或 `$$` 定界符，仅需提供纯 LaTeX 表达式内容。

### 请求示例

```bash
curl -X POST http://127.0.0.1:8000/render \
  -H 'Content-Type: application/json' \
  -d '{"latex": "E = mc^2", "display": true}'
```

```bash
# 行内模式
curl -X POST http://127.0.0.1:8000/render \
  -H 'Content-Type: application/json' \
  -d '{"latex": "\\alpha + \\beta", "display": false}'
```

```bash
# 使用 tex 字段名
curl -X POST http://127.0.0.1:8000/render \
  -H 'Content-Type: application/json' \
  -d '{"tex": "\\int_0^\\infty e^{-x}\\,dx = 1"}'
```

### 成功响应

**`200 OK`**

```json
{
  "ok": true,
  "svg": "<svg xmlns=\"http://www.w3.org/2000/svg\" ...>...</svg>",
  "display": true,
  "elapsed_ms": 12.345
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `ok` | `boolean` | 固定为 `true` |
| `svg` | `string` | 自包含的 `<svg>...</svg>` 字符串，可直接嵌入 HTML |
| `display` | `boolean` | 实际使用的渲染模式 |
| `elapsed_ms` | `number` | 渲染耗时，单位毫秒，精确到微秒级（3 位小数） |

---

## 3. 渲染 LaTeX（GET 方式）

通过查询参数渲染 LaTeX，返回 JSON 格式。适用于简单表达式或快速调试。

```
GET /render?latex=<url-encoded-latex>&display=true
```

### 查询参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `latex` | `string` | **是*** | — | LaTeX 表达式。也可使用别名 `tex` 或 `q` |
| `display` | `string` | 否 | `true` | 渲染模式，接受值见下方说明 |

> *`latex`、`tex`、`q` 三个参数至少提供其一。

`display` 参数可接受的值：

| 被视为 `true` | 被视为 `false` |
|---------------|----------------|
| `1`, `true`, `yes`, `y`, `on` | `0`, `false`, `no`, `n`, `off`, `inline` |

### 请求示例

```bash
curl "http://127.0.0.1:8000/render?latex=E%20%3D%20mc%5E2&display=true"
```

```bash
# 使用 q 别名，行内模式
curl "http://127.0.0.1:8000/render?q=%5Calpha%20%2B%20%5Cbeta&display=inline"
```

### 响应

与 [POST /render](#2-渲染-latexpost) 相同的响应格式。

### 注意事项

- GET 请求受 URL 长度限制，复杂长表达式请使用 POST 方式。
- LaTeX 中的特殊字符（如 `\`、`{`、`}`、`^` 等）必须进行 URL 编码。

---

## 4. 渲染 LaTeX（直接返回 SVG）

将 LaTeX 表达式渲染为 SVG，**直接返回原始 SVG 内容**（`Content-Type: image/svg+xml`），而非 JSON 封装。适合需要直接获取 SVG 文件或嵌入 `<img>` 标签的场景。

支持 POST 和 GET 两种方式，提供两个路径：

| 路径 | 说明 |
|------|------|
| `/render/svg` | 标准路径 |
| `/svg` | 短别名 |

### 4.1 POST 方式

```
POST /render/svg
Content-Type: application/json
```

也可使用 `POST /svg`。

#### 请求体

```json
{
  "latex": "E = mc^2",
  "display": true
}
```

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `latex` | `string` | **是** | — | LaTeX 数学表达式。也可使用字段名 `tex` 作为别名 |
| `display` | `boolean` | 否 | `true` | 渲染模式：`true` = 展示模式（块级），`false` = 行内模式 |

#### 请求示例

```bash
# 直接保存为 SVG 文件
curl -X POST http://127.0.0.1:8000/render/svg \
  -H 'Content-Type: application/json' \
  -d '{"latex": "E = mc^2"}' > equation.svg

# 行内模式，使用短别名
curl -X POST http://127.0.0.1:8000/svg \
  -H 'Content-Type: application/json' \
  -d '{"latex": "\\alpha + \\beta", "display": false}' > alpha-beta.svg

# 在浏览器中查看（返回的 SVG 直接渲染）
curl -X POST http://127.0.0.1:8000/render/svg \
  -H 'Content-Type: application/json' \
  -d '{"latex": "\\int_0^\\infty e^{-x}\\,dx = 1"}'
```

#### 成功响应

**`200 OK`**

```
Content-Type: image/svg+xml; charset=utf-8

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 50" ...>
  ...
</svg>
```

响应体即为可直接使用的 SVG 标记。保存为 `.svg` 文件后可用浏览器或矢量图编辑器直接打开。

### 4.2 GET 方式

```
GET /render/svg?latex=<url-encoded-latex>&display=true
```

也可使用 `GET /svg?latex=...`。

#### 查询参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `latex` | `string` | **是*** | — | LaTeX 表达式。也可使用别名 `tex` 或 `q` |
| `display` | `string` | 否 | `true` | 渲染模式（同第 3 节中的布尔值解析规则） |

#### 请求示例

```bash
curl "http://127.0.0.1:8000/render/svg?latex=E%20%3D%20mc%5E2" > equation.svg

# 使用短别名
curl "http://127.0.0.1:8000/svg?latex=%5Cfrac%7B-b%20%5Cpm%20%5Csqrt%7Bb%5E2-4ac%7D%7D%7B2a%7D" > quadratic.svg
```

### 4.3 在 HTML 中使用

直接返回 SVG 的端点非常适合在 HTML 中引用：

```html
<!-- 通过 <img> 标签引用 -->
<img src="http://127.0.0.1:8000/svg?latex=E%20%3D%20mc%5E2" alt="E = mc²">

<!-- 通过 <object> 标签引用 -->
<object data="http://127.0.0.1:8000/svg?latex=%5Cint_0%5E%5Cinfty%20e%5E%7B-x%7D%5C%2Cdx" type="image/svg+xml"></object>
```

```html
<!-- 通过 JavaScript 动态加载 -->
<script>
fetch('http://127.0.0.1:8000/render/svg', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ latex: '\\sum_{n=1}^{\\infty} \\frac{1}{n^2}' }),
})
  .then(resp => resp.text())
  .then(svg => {
    document.getElementById('math').innerHTML = svg;
  });
</script>
```

### 4.4 错误处理

当渲染失败时（如 LaTeX 语法错误），SVG 端点会**回退返回 JSON 格式的错误信息**（`Content-Type: application/json`），而非返回无效的 SVG。调用方应检查响应头的 `Content-Type` 来判断请求是否成功。

**`422 Unprocessable Entity`（LaTeX 语法错误）：**

```json
{
  "ok": false,
  "error": "MathJax 错误详情"
}
```

---

## 5. CORS 预检

支持跨域请求的 CORS 预检。

```
OPTIONS /render
```

### 响应

**`204 No Content`**

| 响应头 | 值 |
|--------|-----|
| `Access-Control-Allow-Origin` | `*` |
| `Access-Control-Allow-Methods` | `GET, POST, OPTIONS` |
| `Access-Control-Allow-Headers` | `Content-Type` |
| `Cache-Control` | `no-store` |

> 同样适用于 `/health` 等其他路径。

---

## 6. 错误处理

所有错误响应均为 JSON 格式。

### 错误响应结构

```json
{
  "ok": false,
  "error": "错误描述信息"
}
```

### 错误状态码一览

| 状态码 | 含义 | 典型场景 |
|--------|------|----------|
| `400 Bad Request` | 请求格式错误 | 缺少 `latex` 字段、JSON 解析失败、Content-Type 不是 `application/json`、请求体为空或超限 |
| `404 Not Found` | 路径不存在 | 访问 `/xyz` 等未定义的端点 |
| `422 Unprocessable Entity` | LaTeX 语法错误 | MathJax 无法解析提供的 LaTeX 表达式 |
| `500 Internal Server Error` | 服务器内部异常 | QuickJS 引擎异常等非预期错误（防御性捕获，保持服务不崩溃） |

### 错误示例

**缺少必填字段：**
```json
{
  "ok": false,
  "error": "JSON field 'latex' must be a string"
}
```

**LaTeX 语法错误：**
```json
{
  "ok": false,
  "error": "MathJax failed to render the expression: <错误详情>"
}
```

**请求体过大：**
```json
{
  "ok": false,
  "error": "Request body is too large; limit is 1048576 bytes"
}
```

---

## 附录

### A. 支持的 TeX 扩展

服务预置了以下 23 个 TeX 扩展：

| 类别 | 扩展 |
|------|------|
| 基础 | `ams` · `newcommand` · `boldsymbol` |
| 布局 | `enclose` · `html` · `bbox` · `verb` |
| 化学 | `mhchem` |
| 物理 | `physics` · `braket` · `cancel` |
| 数学工具 | `mathtools` · `amscd` · `action` |
| 颜色 | `color` |
| 扩展箭头 | `extpfeil` |
| 容错 | `noerrors` · `noundefined` |
| Unicode 与文本 | `unicode` · `textmacros` · `textcomp` |
| 其他 | `cases` |

### B. curl 速查

```bash
# 健康检查
curl http://127.0.0.1:8000/health

# ---- JSON 接口 ----

# POST 渲染（展示模式）
curl -X POST http://127.0.0.1:8000/render \
  -H 'Content-Type: application/json' \
  -d '{"latex": "\\int_0^\\infty e^{-x}\\,dx = 1"}'

# POST 渲染（行内模式）
curl -X POST http://127.0.0.1:8000/render \
  -H 'Content-Type: application/json' \
  -d '{"latex": "\\sin^2\\theta + \\cos^2\\theta = 1", "display": false}'

# POST 化学式
curl -X POST http://127.0.0.1:8000/render \
  -H 'Content-Type: application/json' \
  -d '{"latex": "\\ce{CH4 + 2O2 -> CO2 + 2H2O}"}'

# GET 渲染
curl "http://127.0.0.1:8000/render?latex=%5Cfrac%7B-b%20%5Cpm%20%5Csqrt%7Bb%5E2-4ac%7D%7D%7B2a%7D"

# 从 JSON 响应中提取 SVG 保存到文件
curl -s -X POST http://127.0.0.1:8000/render \
  -H 'Content-Type: application/json' \
  -d '{"latex": "E = mc^2"}' | python3 -c "
import sys, json
data = json.load(sys.stdin)
if data.get('ok'):
    with open('equation.svg', 'w') as f:
        f.write(data['svg'])
    print('SVG saved to equation.svg')
else:
    print('Error:', data.get('error'))
"

# ---- 直接 SVG 接口 ----

# POST 直接保存 SVG 文件
curl -X POST http://127.0.0.1:8000/render/svg \
  -H 'Content-Type: application/json' \
  -d '{"latex": "E = mc^2"}' > equation.svg

# POST 使用短别名
curl -X POST http://127.0.0.1:8000/svg \
  -H 'Content-Type: application/json' \
  -d '{"latex": "\\int_0^\\infty e^{-x}\\,dx = 1"}' > integral.svg

# GET 直接保存 SVG 文件
curl "http://127.0.0.1:8000/render/svg?latex=E%20%3D%20mc%5E2" > equation.svg

# GET 短别名
curl "http://127.0.0.1:8000/svg?latex=%5Calpha%20%2B%20%5Cbeta&display=inline" > alpha-beta.svg

# 直接通过浏览器打开（自动渲染为图片）
open "http://127.0.0.1:8000/svg?latex=%5Csum_%7Bn%3D1%7D%5E%7B%5Cinfty%7D%5Cfrac%7B1%7D%7Bn%5E2%7D"
```
```

### C. Python 客户端示例

```python
import json
import urllib.request

def render_latex(latex: str, display: bool = True, host: str = "127.0.0.1", port: int = 8000) -> str:
    url = f"http://{host}:{port}/render"
    payload = json.dumps({"latex": latex, "display": display}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if not data["ok"]:
        raise RuntimeError(data["error"])
    return data["svg"]

# 使用示例
svg = render_latex(r"\int_{-\infty}^{\infty} e^{-x^2}\,dx = \sqrt{\pi}")
print(svg[:200])  # 打印前 200 个字符
```

### D. JavaScript 客户端示例

```javascript
// ---- JSON 接口 ----
async function renderLaTeX(latex, display = true) {
  const resp = await fetch('http://127.0.0.1:8000/render', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ latex, display }),
  });
  const data = await resp.json();
  if (!data.ok) throw new Error(data.error);
  return data.svg;
}

// 使用示例
renderLaTeX('\\sum_{n=1}^{\\infty} \\frac{1}{n^2} = \\frac{\\pi^2}{6}')
  .then(svg => document.getElementById('math').innerHTML = svg)
  .catch(console.error);

// ---- 直接 SVG 接口 ----
async function renderSVGDirect(latex, display = true) {
  const resp = await fetch('http://127.0.0.1:8000/render/svg', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ latex, display }),
  });
  if (!resp.ok) {
    const err = await resp.json();
    throw new Error(err.error);
  }
  return await resp.text();  // 直接返回 SVG 文本
}

// 直接嵌入到 DOM
renderSVGDirect('\\frac{-b \\pm \\sqrt{b^2-4ac}}{2a}')
  .then(svg => document.getElementById('quadratic').innerHTML = svg);

// 也可以用 <img> 标签直接引用 GET 端点
// <img src="http://127.0.0.1:8000/svg?latex=E%20%3D%20mc%5E2" alt="公式">
```

---

> 更多信息请参阅 [README.zh-CN.md](README.zh-CN.md)。
