#!/usr/bin/env python3
"""QuickJax Demo — 大量 LaTeX 渲染示例，涵盖各种数学场景。"""

import os
import time
from quickjax import MathJaxRenderer, render


def demo_render(renderer: MathJaxRenderer, label: str, latex: str, display: bool = True, save: bool = True) -> None:
    """渲染并打印简要结果。"""
    t0 = time.perf_counter()
    svg = renderer.render(latex, display=display)
    elapsed = (time.perf_counter() - t0) * 1000
    ok = "<svg" in svg
    status = "✓" if ok else "✗"
    print(f"  {status} [{elapsed:6.1f}ms] {label}")
    if save:
        os.makedirs("outputs", exist_ok=True)
        filename = f"outputs/demo_{label.replace(' ', '_').replace('/', '_')}.svg"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(svg)
    if not ok:
        print(f"    OUTPUT: {svg[:120]}...")


def main():
    print("=" * 70)
    print("QuickJax Demo — MathJax v4 SVG Renderer")
    print("=" * 70)

    t0 = time.perf_counter()
    renderer = MathJaxRenderer()
    init_time = (time.perf_counter() - t0) * 1000
    print(f"\n初始化耗时: {init_time:.0f}ms\n")

    # ------------------------------------------------------------------ #
    # 1. 基础运算
    # ------------------------------------------------------------------ #
    print("── 基础运算 ──")
    basics = {
        "加减乘除": r"a + b - c \times d \div e",
        "等式": r"E = mc^2",
        "不等式": r"a \neq b, \quad x \leq y, \quad m \geq n",
        "幂与下标": r"x^{2n+1}, \quad a_{i,j}",
        "嵌套上下标": r"x_{i_1}^{j^{k}}",
        "正负号": r"\pm \alpha \mp \beta",
        "点乘与叉乘": r"\mathbf{a} \cdot \mathbf{b} = |\mathbf{a}||\mathbf{b}|\cos\theta",
    }
    for label, latex in basics.items():
        demo_render(renderer, label, latex)

    # ------------------------------------------------------------------ #
    # 2. 分数与根号
    # ------------------------------------------------------------------ #
    print("\n── 分数与根号 ──")
    fractions = {
        "简单分数": r"\frac{a}{b}",
        "嵌套分数": r"\frac{1}{1+\frac{1}{1+\frac{1}{x}}}",
        "展示分数(dfrac)": r"\dfrac{\partial f}{\partial x}",
        "行内分数(tfrac)": r"\tfrac{1}{2}",
        "平方根": r"\sqrt{x^2 + y^2}",
        "n次根": r"\sqrt[3]{27} = 3",
        "嵌套根号": r"\sqrt{1 + \sqrt{1 + \sqrt{1 + x}}}",
        "分数+根号组合": r"x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}",
    }
    for label, latex in fractions.items():
        demo_render(renderer, label, latex)

    # ------------------------------------------------------------------ #
    # 3. 希腊字母
    # ------------------------------------------------------------------ #
    print("\n── 希腊字母 ──")
    greeks = {
        "小写希腊": r"\alpha \beta \gamma \delta \epsilon \zeta \eta \theta",
        "更多小写": r"\iota \kappa \lambda \mu \nu \xi \pi \rho",
        "最后小写": r"\sigma \tau \upsilon \phi \chi \psi \omega",
        "大写希腊": r"\Gamma \Delta \Theta \Lambda \Xi \Pi \Sigma \Phi \Psi \Omega",
        "变体": r"\varepsilon \vartheta \varpi \varrho \varsigma \varphi",
    }
    for label, latex in greeks.items():
        demo_render(renderer, label, latex)

    # ------------------------------------------------------------------ #
    # 4. 求和、积分、极限
    # ------------------------------------------------------------------ #
    print("\n── 求和、积分、极限 ──")
    calculus = {
        "求和": r"\sum_{i=1}^{n} i = \frac{n(n+1)}{2}",
        "乘积": r"\prod_{k=1}^{n} k = n!",
        "定积分": r"\int_0^1 x^2 \, dx = \frac{1}{3}",
        "不定积分": r"\int e^x \, dx = e^x + C",
        "多重积分": r"\iint_D f(x,y) \, dA",
        "三重积分": r"\iiint_V \rho \, dV",
        "曲线积分": r"\oint_C \mathbf{F} \cdot d\mathbf{r}",
        "极限": r"\lim_{x \to 0} \frac{\sin x}{x} = 1",
        "无穷极限": r"\lim_{n \to \infty} \left(1 + \frac{1}{n}\right)^n = e",
        "上确界": r"\sup_{x \in S} f(x)",
        "下确界": r"\inf_{x \in S} f(x)",
    }
    for label, latex in calculus.items():
        demo_render(renderer, label, latex)

    # ------------------------------------------------------------------ #
    # 5. 矩阵
    # ------------------------------------------------------------------ #
    print("\n── 矩阵 ──")
    matrices = {
        "圆括号矩阵": r"\begin{pmatrix} a & b \\ c & d \end{pmatrix}",
        "方括号矩阵": r"\begin{bmatrix} 1 & 0 & 0 \\ 0 & 1 & 0 \\ 0 & 0 & 1 \end{bmatrix}",
        "花括号矩阵": r"\begin{Bmatrix} x \\ y \end{Bmatrix}",
        "行列式": r"\begin{vmatrix} a & b \\ c & d \end{vmatrix} = ad - bc",
        "范数矩阵": r"\begin{Vmatrix} \mathbf{v} \end{Vmatrix}",
        "无括号矩阵": r"\begin{matrix} 1 & 2 \\ 3 & 4 \end{matrix}",
        "增广矩阵": r"\left(\begin{array}{cc|c} 1 & 2 & 3 \\ 4 & 5 & 6 \end{array}\right)",
        "小矩阵(行内)": r"A = \bigl(\begin{smallmatrix} a & b \\ c & d \end{smallmatrix}\bigr)",
    }
    for label, latex in matrices.items():
        demo_render(renderer, label, latex)

    # ------------------------------------------------------------------ #
    # 6. 对齐与多行公式
    # ------------------------------------------------------------------ #
    print("\n── 对齐与多行公式 ──")
    multiline = {
        "aligned": r"""\begin{aligned}
            f(x) &= x^2 + 2x + 1 \\
                 &= (x+1)^2
        \end{aligned}""",
        "cases分段函数": r"""|x| = \begin{cases}
            x  & \text{if } x \geq 0 \\
            -x & \text{if } x < 0
        \end{cases}""",
        "gather居中多行": r"""\begin{gathered}
            a + b = c \\
            d + e = f
        \end{gathered}""",
    }
    for label, latex in multiline.items():
        demo_render(renderer, label, latex)

    # ------------------------------------------------------------------ #
    # 7. 定界符
    # ------------------------------------------------------------------ #
    print("\n── 定界符 ──")
    delimiters = {
        "自适应括号": r"\left( \frac{a}{b} \right)",
        "自适应方括号": r"\left[ \sum_{i=1}^n x_i \right]",
        "自适应花括号": r"\left\{ x \in \mathbb{R} \mid x > 0 \right\}",
        "自适应尖括号": r"\left\langle \psi \mid \phi \right\rangle",
        "单边定界符": r"\left. \frac{dy}{dx} \right|_{x=0}",
        "取整函数": r"\lfloor x \rfloor, \quad \lceil x \rceil",
    }
    for label, latex in delimiters.items():
        demo_render(renderer, label, latex)

    # ------------------------------------------------------------------ #
    # 8. 文本与字体
    # ------------------------------------------------------------------ #
    print("\n── 文本与字体 ──")
    fonts = {
        "粗体": r"\mathbf{A} \mathbf{x} = \mathbf{b}",
        "斜体(默认)": r"f(x) = ax + b",
        "罗马体": r"\mathrm{pH} = -\log[\mathrm{H}^+]",
        "花体/手写": r"\mathcal{L} \{ f(t) \} = F(s)",
        "黑板粗体": r"\mathbb{R}, \mathbb{C}, \mathbb{Z}, \mathbb{Q}, \mathbb{N}",
        "哥特体": r"\mathfrak{g}, \mathfrak{su}(2)",
        "等宽体": r"\mathtt{code}",
        "文本混排": r"f(x) = 0 \quad \text{for all } x \in S",
        "中文文本": r"\text{面积} = \pi r^2",
    }
    for label, latex in fonts.items():
        demo_render(renderer, label, latex)

    # ------------------------------------------------------------------ #
    # 9. 重音与装饰
    # ------------------------------------------------------------------ #
    print("\n── 重音与装饰 ──")
    accents = {
        "上划线": r"\overline{AB}",
        "下划线": r"\underline{x + y}",
        "帽子": r"\hat{a}, \widehat{ABC}",
        "波浪线": r"\tilde{x}, \widetilde{XYZ}",
        "向量箭头": r"\vec{v}, \overrightarrow{AB}",
        "点(导数)": r"\dot{x}, \ddot{x}, \dddot{x}",
        "上下括号": r"\overbrace{a+b+\cdots+z}^{26}, \quad \underbrace{1+1+\cdots+1}_{n}",
    }
    for label, latex in accents.items():
        demo_render(renderer, label, latex)

    # ------------------------------------------------------------------ #
    # 10. 数论与集合
    # ------------------------------------------------------------------ #
    print("\n── 数论与集合 ──")
    sets = {
        "集合运算": r"A \cup B, \quad A \cap B, \quad A \setminus B",
        "子集": r"A \subset B, \quad A \subseteq B, \quad A \supset B",
        "属于": r"x \in A, \quad y \notin B",
        "空集": r"\emptyset, \quad \varnothing",
        "集合构造": r"S = \{ x \in \mathbb{Z} \mid x^2 < 10 \}",
        "直和": r"V = V_1 \oplus V_2",
        "笛卡尔积": r"A \times B",
    }
    for label, latex in sets.items():
        demo_render(renderer, label, latex)

    # ------------------------------------------------------------------ #
    # 11. 逻辑符号
    # ------------------------------------------------------------------ #
    print("\n── 逻辑符号 ──")
    logic = {
        "逻辑与或": r"P \land Q, \quad P \lor Q, \quad \lnot P",
        "蕴含": r"P \implies Q, \quad P \iff Q",
        "全称存在": r"\forall x \in \mathbb{R}, \quad \exists y > 0",
        "因此": r"A, \quad B \quad \therefore C",
    }
    for label, latex in logic.items():
        demo_render(renderer, label, latex)

    # ------------------------------------------------------------------ #
    # 12. 箭头
    # ------------------------------------------------------------------ #
    print("\n── 箭头 ──")
    arrows = {
        "基本箭头": r"\leftarrow \rightarrow \leftrightarrow",
        "长箭头": r"\longleftarrow \longrightarrow \longleftrightarrow",
        "双线箭头": r"\Leftarrow \Rightarrow \Leftrightarrow",
        "映射箭头": r"f \colon X \to Y, \quad x \mapsto f(x)",
        "钩箭头": r"A \hookrightarrow B",
        "上下箭头": r"\uparrow \downarrow \updownarrow",
    }
    for label, latex in arrows.items():
        demo_render(renderer, label, latex)

    # ------------------------------------------------------------------ #
    # 13. 物理相关
    # ------------------------------------------------------------------ #
    print("\n── 物理 ──")
    physics_exprs = {
        "薛定谔方程": r"i\hbar \frac{\partial}{\partial t} \Psi = \hat{H} \Psi",
        "麦克斯韦方程(散度)": r"\nabla \cdot \mathbf{E} = \frac{\rho}{\varepsilon_0}",
        "麦克斯韦方程(旋度)": r"\nabla \times \mathbf{B} = \mu_0 \mathbf{J} + \mu_0 \varepsilon_0 \frac{\partial \mathbf{E}}{\partial t}",
        "狄拉克方程": r"(i \gamma^\mu \partial_\mu - m) \psi = 0",
        "爱因斯坦场方程": r"R_{\mu\nu} - \tfrac{1}{2} R g_{\mu\nu} + \Lambda g_{\mu\nu} = \frac{8\pi G}{c^4} T_{\mu\nu}",
        "洛伦兹力": r"\mathbf{F} = q(\mathbf{E} + \mathbf{v} \times \mathbf{B})",
        "热力学第一定律": r"dU = \delta Q - \delta W",
        "玻尔兹曼熵": r"S = k_B \ln \Omega",
    }
    for label, latex in physics_exprs.items():
        demo_render(renderer, label, latex)

    # ------------------------------------------------------------------ #
    # 14. 概率与统计
    # ------------------------------------------------------------------ #
    print("\n── 概率与统计 ──")
    prob = {
        "期望": r"\mathbb{E}[X] = \sum_{i} x_i p_i",
        "方差": r"\mathrm{Var}(X) = \mathbb{E}[X^2] - (\mathbb{E}[X])^2",
        "正态分布": r"f(x) = \frac{1}{\sigma\sqrt{2\pi}} e^{-\frac{(x-\mu)^2}{2\sigma^2}}",
        "贝叶斯定理": r"P(A|B) = \frac{P(B|A) P(A)}{P(B)}",
        "二项分布": r"P(X=k) = \binom{n}{k} p^k (1-p)^{n-k}",
        "卡方分布": r"\chi^2 = \sum_{i=1}^{k} \frac{(O_i - E_i)^2}{E_i}",
        "协方差": r"\mathrm{Cov}(X,Y) = \mathbb{E}[(X - \mu_X)(Y - \mu_Y)]",
    }
    for label, latex in prob.items():
        demo_render(renderer, label, latex)

    # ------------------------------------------------------------------ #
    # 15. 线性代数
    # ------------------------------------------------------------------ #
    print("\n── 线性代数 ──")
    linalg = {
        "特征方程": r"\det(A - \lambda I) = 0",
        "迹": r"\mathrm{tr}(A) = \sum_{i=1}^n a_{ii}",
        "转置": r"(AB)^T = B^T A^T",
        "逆矩阵": r"A^{-1} A = A A^{-1} = I",
        "克罗内克积": r"A \otimes B",
        "内积": r"\langle u, v \rangle = \sum_i u_i \overline{v_i}",
        "范数": r"\| \mathbf{x} \|_p = \left( \sum_i |x_i|^p \right)^{1/p}",
        "SVD分解": r"A = U \Sigma V^*",
    }
    for label, latex in linalg.items():
        demo_render(renderer, label, latex)

    # ------------------------------------------------------------------ #
    # 16. 微积分进阶
    # ------------------------------------------------------------------ #
    print("\n── 微积分进阶 ──")
    advanced_calc = {
        "泰勒级数": r"e^x = \sum_{n=0}^{\infty} \frac{x^n}{n!}",
        "傅里叶变换": r"\hat{f}(\xi) = \int_{-\infty}^{\infty} f(x) e^{-2\pi i x \xi} \, dx",
        "拉普拉斯变换": r"\mathcal{L}\{f(t)\} = \int_0^\infty f(t) e^{-st} \, dt",
        "偏微分方程": r"\frac{\partial^2 u}{\partial t^2} = c^2 \nabla^2 u",
        "格林公式": r"\oint_C (P\,dx + Q\,dy) = \iint_D \left(\frac{\partial Q}{\partial x} - \frac{\partial P}{\partial y}\right) dA",
        "散度定理": r"\iiint_V (\nabla \cdot \mathbf{F}) \, dV = \oiint_S \mathbf{F} \cdot d\mathbf{S}",
        "莱布尼茨公式": r"\frac{d}{dx}\int_{a(x)}^{b(x)} f(x,t)\,dt = f(x,b) b'(x) - f(x,a) a'(x) + \int_a^b \frac{\partial f}{\partial x} dt",
        "欧拉公式": r"e^{i\theta} = \cos\theta + i\sin\theta",
    }
    for label, latex in advanced_calc.items():
        demo_render(renderer, label, latex)

    # ------------------------------------------------------------------ #
    # 17. 化学 (mhchem)
    # ------------------------------------------------------------------ #
    print("\n── 化学 (mhchem) ──")
    chemistry = {
        "化学方程式": r"\ce{2H2 + O2 -> 2H2O}",
        "可逆反应": r"\ce{N2 + 3H2 <=> 2NH3}",
        "离子方程式": r"\ce{Ag+ + Cl- -> AgCl v}",
        "氧化还原": r"\ce{Fe^{2+} -> Fe^{3+} + e-}",
        "有机分子": r"\ce{CH3CH2OH}",
    }
    for label, latex in chemistry.items():
        demo_render(renderer, label, latex)

    # ------------------------------------------------------------------ #
    # 18. 组合数学
    # ------------------------------------------------------------------ #
    print("\n── 组合数学 ──")
    combinatorics = {
        "组合数": r"\binom{n}{k} = \frac{n!}{k!(n-k)!}",
        "多项式系数": r"\binom{n}{k_1, k_2, \ldots, k_m}",
        "斯特林数": r"\left\{ {n \atop k} \right\}",
        "卡特兰数": r"C_n = \frac{1}{n+1}\binom{2n}{n}",
        "范德蒙恒等式": r"\sum_{k=0}^{r} \binom{m}{k}\binom{n}{r-k} = \binom{m+n}{r}",
        "容斥原理": r"|A_1 \cup \cdots \cup A_n| = \sum_{i} |A_i| - \sum_{i<j} |A_i \cap A_j| + \cdots",
    }
    for label, latex in combinatorics.items():
        demo_render(renderer, label, latex)

    # ------------------------------------------------------------------ #
    # 19. 数论
    # ------------------------------------------------------------------ #
    print("\n── 数论 ──")
    number_theory = {
        "整除": r"a \mid b",
        "同余": r"a \equiv b \pmod{m}",
        "欧拉函数": r"\phi(n) = n \prod_{p \mid n} \left(1 - \frac{1}{p}\right)",
        "黎曼zeta函数": r"\zeta(s) = \sum_{n=1}^{\infty} \frac{1}{n^s} = \prod_{p \text{ prime}} \frac{1}{1-p^{-s}}",
        "勒让德符号": r"\left(\frac{a}{p}\right)",
        "连分数": r"x = a_0 + \cfrac{1}{a_1 + \cfrac{1}{a_2 + \cfrac{1}{a_3 + \cdots}}}",
    }
    for label, latex in number_theory.items():
        demo_render(renderer, label, latex)

    # ------------------------------------------------------------------ #
    # 20. 拓扑与抽象代数
    # ------------------------------------------------------------------ #
    print("\n── 拓扑与抽象代数 ──")
    abstract = {
        "同态映射": r"f: G \to H, \quad f(ab) = f(a)f(b)",
        "正合列": r"0 \to A \xrightarrow{f} B \xrightarrow{g} C \to 0",
        "张量积": r"V \otimes W",
        "商群": r"G / N",
        "同构": r"G \cong \mathbb{Z}/n\mathbb{Z}",
        "基本群": r"\pi_1(S^1) \cong \mathbb{Z}",
    }
    for label, latex in abstract.items():
        demo_render(renderer, label, latex)

    # ------------------------------------------------------------------ #
    # 21. 颜色
    # ------------------------------------------------------------------ #
    print("\n── 颜色 ──")
    colors = {
        "红色": r"{\color{red} x^2} + {\color{blue} y^2} = {\color{green} z^2}",
        "彩色方程": r"\colorbox{yellow}{$E = mc^2$}",
        "彩色分数": r"\frac{{\color{red}a}}{{\color{blue}b}}",
    }
    for label, latex in colors.items():
        demo_render(renderer, label, latex)

    # ------------------------------------------------------------------ #
    # 22. 取消线 (cancel)
    # ------------------------------------------------------------------ #
    print("\n── 取消线 ──")
    cancels = {
        "取消": r"\cancel{x} + \bcancel{y} + \xcancel{z}",
        "约分": r"\frac{\cancel{a} \cdot b}{\cancel{a} \cdot c} = \frac{b}{c}",
    }
    for label, latex in cancels.items():
        demo_render(renderer, label, latex)

    # ------------------------------------------------------------------ #
    # 23. 大型综合公式
    # ------------------------------------------------------------------ #
    print("\n── 大型综合公式 ──")
    complex_exprs = {
        "麦克斯韦方程组": r"""\begin{aligned}
            \nabla \cdot \mathbf{E} &= \frac{\rho}{\varepsilon_0} \\
            \nabla \cdot \mathbf{B} &= 0 \\
            \nabla \times \mathbf{E} &= -\frac{\partial \mathbf{B}}{\partial t} \\
            \nabla \times \mathbf{B} &= \mu_0 \mathbf{J} + \mu_0 \varepsilon_0 \frac{\partial \mathbf{E}}{\partial t}
        \end{aligned}""",
        "变分法": r"\delta \int_{t_1}^{t_2} L(q, \dot{q}, t) \, dt = 0 \implies \frac{d}{dt}\frac{\partial L}{\partial \dot{q}} - \frac{\partial L}{\partial q} = 0",
        "路径积分": r"K(x_b, t_b; x_a, t_a) = \int \mathcal{D}[x(t)] \, e^{\frac{i}{\hbar} S[x(t)]}",
        "广义Stokes定理": r"\int_{\partial \Omega} \omega = \int_\Omega d\omega",
    }
    for label, latex in complex_exprs.items():
        demo_render(renderer, label, latex)

    # ------------------------------------------------------------------ #
    # 24. 行内模式测试
    # ------------------------------------------------------------------ #
    print("\n── 行内模式 ──")
    inline_tests = {
        "行内加法": r"a + b",
        "行内分数": r"\frac{1}{2}",
        "行内求和": r"\sum x_i",
        "行内积分": r"\int f",
    }
    for label, latex in inline_tests.items():
        demo_render(renderer, label, latex, display=False)

    # ------------------------------------------------------------------ #
    # 25. 边界/特殊情况
    # ------------------------------------------------------------------ #
    print("\n── 边界情况 ──")
    edge_cases = {
        "空字符串": r"",
        "单字符": r"x",
        "纯数字": r"12345",
        "单空格": r"\ ",
        "连续空格": r"a \quad b \qquad c",
        "极深嵌套": r"\sqrt{\sqrt{\sqrt{\sqrt{\sqrt{x}}}}}",
        "超长下标": r"x_{a_{b_{c_{d_{e}}}}}",
    }
    for label, latex in edge_cases.items():
        demo_render(renderer, label, latex)

    # ------------------------------------------------------------------ #
    # 汇总
    # ------------------------------------------------------------------ #
    total = sum(len(d) for d in [
        basics, fractions, greeks, calculus, matrices, multiline,
        delimiters, fonts, accents, sets, logic, arrows, physics_exprs,
        prob, linalg, advanced_calc, chemistry, combinatorics,
        number_theory, abstract, colors, cancels, complex_exprs,
        inline_tests, edge_cases,
    ])
    print(f"\n{'=' * 70}")
    print(f"共测试 {total} 个 LaTeX 表达式")
    print(f"初始化耗时: {init_time:.0f}ms")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
