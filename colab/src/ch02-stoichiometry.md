<!-- md -->
# Chapter 2 Atoms, molecules and stoichiometry

Cambridge International AS & A Level Chemistry 9701（2025 / 2026 / 2027）· **Physical chemistry**

- 内容边界与 learning outcome 逐字取自 syllabus；*A*ᵣ 取自 syllabus 的 Periodic Table，常数取自 data booklet；判分句式取自 2024–2026 Paper 2 的 mark scheme，引用写卷号。
- 🔬 / 📝 开头的 cell 是交互图（已经预先渲染好，打开就能用）。如果显示空白：**Runtime → Run all**（连本地运行时即可，几秒跑完）。
- 本章几乎全是计算。每一个交互件都会把每一步的算式写出来，照着它的格式写，就是 mark scheme 要的 working。

本章用到的常数（data booklet）：

| 常数 | 值 |
|---|---|
| Avogadro constant, *L* | 6.02 × 10²³ mol⁻¹ |
| molar volume of gas, *V*ₘ | 24.0 dm³ mol⁻¹ under room conditions；22.4 dm³ mol⁻¹ at s.t.p.（101 kPa，273 K） |
| molar gas constant, *R* | 8.31 J K⁻¹ mol⁻¹（*pV* = *nRT* 属于 chapter 4，但本章的气体计算题常常要用） |

<!-- md -->
## 2.1 Relative masses of atoms and molecules

### A. Unified atomic mass unit

一个 atom 的质量太小（10⁻²⁷ – 10⁻²⁵ kg），直接用 kg 很不方便。于是选一个 standard：**carbon-12 atom**。

**unified atomic mass unit**（符号 u）= one twelfth of the mass of a carbon-12 atom ≈ 1.66 × 10⁻²⁷ kg。

所有 relative mass 都是「这个粒子的质量是 1 u 的多少倍」，是两个质量之比，所以**没有单位**。

{{lo 2.1.1}}

### B. 四个 relative mass

| term | 比的是什么 | 用在哪 |
|---|---|---|
| relative isotopic mass | the mass of **one atom of a particular isotope** ÷ 1 u | 单个 isotope，例如 ³⁵Cl = 35.0（近似整数） |
| relative atomic mass, *A*ᵣ | the **weighted average mass** of the atoms of an element ÷ 1 u | element（天然 isotope 混合物），例如 Cl = 35.5 |
| relative molecular mass, *M*ᵣ | the weighted average mass of **one molecule** ÷ 1 u | simple molecular substance，例如 CH₄ = 16.0 |
| relative formula mass | the weighted average mass of **one formula unit** ÷ 1 u | ionic compound（没有 molecule），例如 Mg(OH)₂ = 58.3 |

relative isotopic mass 的判分（9701/21 Oct/Nov 2024 Q1(c)(i)，2 分）：

- M1 **mass of an (atom of an) isotope**
- M2 compared to the unified atomic mass unit **OR** on a scale on which a carbon-12 atom has a mass of exactly 12 units **OR** divided by 1/12 mass of a carbon-12 atom

讲义提醒：M2 写成 "compared to the unified atomic mass" 少了 *unit* 会被拒。*A*ᵣ 的定义比它多一个关键词 **weighted average**——因为大部分 element 是 isotopes 的混合物，所以 Periodic Table 上的 *A*ᵣ 不是整数（Cl = 35.5）。

*M*ᵣ / relative formula mass 就是把 formula 里所有 atom 的 *A*ᵣ 加起来：

- CH₄：12.0 + 4 × 1.0 = 16.0
- Mg(OH)₂：24.3 + 2 × (16.0 + 1.0) = 58.3
- CuSO₄·5H₂O：63.5 + 32.1 + 4 × 16.0 + 5 × 18.0 = 249.6（water of crystallisation 也要算进去）

{{lo 2.1.2}}

### C. 从 mass spectrum 算 *A*ᵣ

mass spectrometer 把 atom 变成 +1 ion，按 *m*/*e* 分开；每个 peak 对应一个 isotope，peak 的高度是它的 relative abundance。

*A*ᵣ = Σ(relative isotopic mass × relative abundance) ÷ Σ(relative abundance)

- abundance 不一定是百分数（boron：¹⁰B 23、¹¹B 100），所以分母要写 **Σ abundance**，不能直接 ÷ 100。
- boron：(10 × 23 + 11 × 100) ÷ (23 + 100) = 10.8
- chlorine：(35 × 75 + 37 × 25) ÷ 100 = 35.5

<!-- html: mass spectrum → Aᵣ -->
{{cell ar-spectrum}}

<!-- md -->
## 2.2 The mole and the Avogadro constant

**mole**：the amount of substance that contains **6.02 × 10²³** specified particles（atoms、molecules、ions 或 electrons）。这个数就是 **Avogadro constant, *L***（6.02 × 10²³ mol⁻¹）。

1 mol 任何物质的质量，以 g 计，在数值上等于它的 *A*ᵣ / *M*ᵣ——这就是 **molar mass, *M***，单位 g mol⁻¹。

| 关系 | 公式 |
|---|---|
| mass ↔ amount | *n* = *m* / *M* |
| amount ↔ particles | *N* = *n* × *L* |
| gas volume ↔ amount（room conditions） | *n* = *V* / 24.0（*V* 用 dm³） |
| solution ↔ amount | *n* = *c* × *V*（*V* 用 dm³；1 dm³ = 1000 cm³） |

**一定要说清楚是什么 particle**：「1 mol of oxygen」有歧义——1 mol O atoms 是 16.0 g，1 mol O₂ molecules 是 32.0 g、含 2 × 6.02 × 10²³ 个 O atoms。

例：0.18 g ethanedioic acid, HO₂CCO₂H（*M*ᵣ = 90.0）里有多少个 carbon atom？

1. *n*(acid) = 0.18 / 90.0 = 0.0020 mol
2. 每个 molecule 有 2 个 C：*n*(C) = 2 × 0.0020 = 0.0040 mol
3. *N*(C) = 0.0040 × 6.02 × 10²³ = **2.4 × 10²¹**（2 s.f.，跟 0.18 一样）

{{lo 2.2.1}}

<!-- html: mole 换算图 -->
{{cell mole-map}}

<!-- md -->
## 2.3 Formulas

### A. Ionic compounds 的 formula

规则只有一条：**positive charges 的总数 = negative charges 的总数**（整体 neutral）。

ion 的 charge 可以从 Periodic Table 上的位置预测：

| 位置 | 怎样达到 noble gas configuration | ion charge | 例 |
|---|---|---|---|
| Group 1 | 失 1 个 electron | +1 | Na⁺、K⁺ |
| Group 2 | 失 2 个 | +2 | Mg²⁺、Ca²⁺ |
| Group 13 | 失 3 个 | +3 | Al³⁺ |
| Group 15 | 得 3 个 | −3 | N³⁻（nitride） |
| Group 16 | 得 2 个 | −2 | O²⁻（oxide）、S²⁻（sulfide） |
| Group 17 | 得 1 个 | −1 | Cl⁻（chloride）、Br⁻、I⁻ |
| transition element | charge 不固定 | 用 Roman numeral 写 oxidation number | iron(II) → Fe²⁺，iron(III) → Fe³⁺ |

Group 1 / 2 / 13 的 compound 不写 Roman numeral：magnesium oxide，不是 magnesium(II) oxide。

**必须背的 ion**（syllabus 点名）：

| ion | name | ion | name |
|---|---|---|---|
| NO₃⁻ | nitrate | NH₄⁺ | ammonium |
| CO₃²⁻ | carbonate | Zn²⁺ | zinc |
| SO₄²⁻ | sulfate | Ag⁺ | silver |
| OH⁻ | hydroxide | HCO₃⁻ | hydrogencarbonate |
| PO₄³⁻ | phosphate | | |

写 formula 时，compound ion 要乘 2 以上就加括号：Zn²⁺ + 2 NO₃⁻ → Zn(NO₃)₂；(NH₄)₂SO₄；Ca₃(PO₄)₂。

{{lo 2.3.1}}

<!-- html: ionic formula 拼装器 -->
{{cell ion-formula}}

<!-- md -->
### B. Equations：配平、state symbols、ionic equations

**配平**：atom 不会凭空产生或消失，左右两边每种 atom 的数目必须相等。

1. 写出 reactants 和 products 的正确 formula——**之后只改前面的系数，绝不改 formula**；
2. 数两边每种 atom；
3. 一次配一种 atom，最后配出现在多个物质里的那一种（通常是 O 或 H）。

例：Fe₂O₃ + CO → Fe + CO₂ → 先配 Fe：Fe₂O₃ + CO → **2**Fe + CO₂ → 设 CO 和 CO₂ 的系数都是 *x*（C 守恒），O 两边分别是 3 + *x* 和 2*x* → *x* = 3：
Fe₂O₃ + 3CO → 2Fe + 3CO₂。

真题里「Construct an equation」常给产物的描述，要自己写 formula：

- bismuth 把 water 还原成 Bi₂O₃，同时放出一种 squeaky pop 的气体（H₂）：2Bi + 3H₂O → Bi₂O₃ + 3H₂（9701/22 Feb/Mar 2024 Q1(b)(i)）
- Mg₃N₂ 和 excess water 只生成 ammonia 和 magnesium hydroxide：Mg₃N₂ + 6H₂O → 3Mg(OH)₂ + 2NH₃（9701/21 May/June 2024 Q2(c)(ii)）

**state symbols**：(s) solid、(l) liquid、(g) gas、(aq) aqueous（溶在水里）。注意 water 本身是 (l)，不是 (aq)；precipitate 是 (s)。

**ionic equation**：只写真正参与反应的 ions / atoms / molecules；溶液里前后没有变化的 ion 叫 **spectator ions**，要删掉。做法：把所有 (aq) 的 ionic compound 拆成 ions → 两边相同的划掉 → 检查 atoms 和 **charges** 都平衡。

| full equation | ionic equation | spectator ions |
|---|---|---|
| Zn(s) + CuSO₄(aq) → ZnSO₄(aq) + Cu(s) | Zn(s) + Cu²⁺(aq) → Zn²⁺(aq) + Cu(s) | SO₄²⁻ |
| H₂SO₄(aq) + 2NaOH(aq) → Na₂SO₄(aq) + 2H₂O(l) | H⁺(aq) + OH⁻(aq) → H₂O(l) | Na⁺、SO₄²⁻ |
| Br₂(aq) + 2KI(aq) → 2KBr(aq) + I₂(aq) | Br₂(aq) + 2I⁻(aq) → 2Br⁻(aq) + I₂(aq) | K⁺ |
| CuSO₄(aq) + 2NaOH(aq) → Cu(OH)₂(s) + Na₂SO₄(aq) | Cu²⁺(aq) + 2OH⁻(aq) → Cu(OH)₂(s) | Na⁺、SO₄²⁻ |
| Pb(NO₃)₂(aq) + 2KI(aq) → PbI₂(s) + 2KNO₃(aq) | Pb²⁺(aq) + 2I⁻(aq) → PbI₂(s) | K⁺、NO₃⁻ |

{{lo 2.3.2}}

<!-- html: 配平 + ionic equation -->
{{cell balance}}

<!-- md -->
### C. Empirical formula 和 molecular formula

- **empirical formula**：the simplest whole-number ratio of the atoms of each element present in a compound。
- **molecular formula**：the actual number of atoms of each element present in one molecule。
- molecular formula 一定是 empirical formula 的整数倍：C₆H₁₂O₆ → CH₂O，C₂H₄Br₂ → CH₂Br。ionic compound 没有 molecule，它的 formula 就是 empirical formula。

{{lo 2.3.3}}

**anhydrous / hydrated / water of crystallisation**

- **water of crystallisation**：以固定的 mol 数结合在 crystal structure 里的 water，formula 里用「·」隔开，系数是整数：CuSO₄·5H₂O。
- **hydrated**：含 water of crystallisation 的 compound（blue CuSO₄·5H₂O）。
- **anhydrous**：不含 water of crystallisation（white CuSO₄）。
- 加热：CuSO₄·5H₂O → CuSO₄ + 5H₂O；加水则反过来。同一个 salt 可以有不同 hydrate：CoCl₂·6H₂O、CoCl₂·2H₂O。

{{lo 2.3.4}}

**怎么算**（三列表格法）：

1. 每个 element 的 mass（或 %）——没给的那个用减法：O = 总 mass − 其余；
2. ÷ *A*ᵣ → amount (mol)；
3. ÷ 最小的那个 → ratio；接近 .5 就 ×2，接近 .33 / .67 就 ×3，**不要把 1.5 四舍五入成 2**；
4. molecular formula：*n* = *M*ᵣ ÷ (empirical formula mass)，再把 empirical formula 乘 *n*。

例：100.0 g 的 X（只含 S 和 Cl）含 47.49 g S，*M*ᵣ = 135.2（9701/21 May/June 2026 Q1(e)）：

| | S | Cl |
|---|---|---|
| mass / g | 47.49 | 100.0 − 47.49 = 52.51 |
| ÷ *A*ᵣ | 47.49 / 32.1 = 1.48 | 52.51 / 35.5 = 1.48 |
| ratio | 1 | 1 |

empirical formula SCl，mass = 67.6；135.2 / 67.6 = 2 → **S₂Cl₂**。

hydrated salt 求 *x* 时，把 H₂O 当成一个「element」（*M*ᵣ = 18.0）放进表格。

{{lo 2.3.5}}

<!-- html: empirical → molecular formula 分步解 -->
{{cell empirical}}

<!-- md -->
## 2.4 Reacting masses and volumes (of solutions and gases)

### A. Reacting masses、limiting reagent、percentage yield

balanced equation 的系数就是 **mole ratio**（stoichiometry）。所有题都是同一个套路：

> 已知量 → **mol** → 用系数换成目标物的 **mol** → 目标量

例：79.8 g Fe₂O₃ 与 9.36 g C 加热：2Fe₂O₃ + 3C → 4Fe + 3CO₂，求 CO₂ 的 mass。

1. *n*(Fe₂O₃) = 79.8 / 159.6 = 0.500 mol；*n*(C) = 9.36 / 12.0 = 0.780 mol
2. 0.500 mol Fe₂O₃ 需要 0.500 × 3/2 = 0.750 mol C < 0.780 → **C in excess**（剩 0.030 mol），**Fe₂O₃ is the limiting reagent**
3. 产物永远按 limiting reagent 算：*n*(CO₂) = 0.500 × 3/2 = 0.750 mol → 0.750 × 44.0 = **33.0 g**

**percentage yield** = actual yield ÷ theoretical (predicted) yield × 100%。theoretical yield 是 limiting reagent 全部转化、没有 side reaction 时算出来的量。yield 低于 100% 的原因：side reactions、reaction 没有进行完全（reversible）、操作中损失产物。

例：18.0 g Al 与 excess Cl₂：2Al + 3Cl₂ → 2AlCl₃，实得 71.0 g AlCl₃。theoretical = 18.0 / 27.0 × 133.5 = 89.0 g → yield = 71.0 / 89.0 × 100 = **79.8%**。

**significant figures**：答案的 s.f. 跟题目数据里最少的那个一致；**中间步骤不要先四舍五入**，最后一步才 round。0.004 是 1 s.f.，0.0040 是 2 s.f.。mark scheme 对 s.f. 是认真的：9701/22 May/June 2026 Q4(b)(iii) 的 1.875 × 10⁻³ mol，接受 1.88 × 10⁻³ / 1.9 × 10⁻³，但**拒绝** 1.880 × 10⁻³、1.90 × 10⁻³、2.0 × 10⁻³（凭空多出来的 0 = 不合理的精度），也拒绝截断成 1.87 × 10⁻³。

<!-- html: limiting reagent + percentage yield -->
{{cell limiting}}

<!-- md -->
### B. Volumes of gases

同温同压下，相同体积的任何 gas 含相同数目的 molecules，所以 **gas 的体积比 = mole 比**。room conditions 下 1 mol gas 占 **24.0 dm³**（= 24 000 cm³）。

- 0.40 mol N₂ 的体积：0.40 × 24.0 = 9.6 dm³
- 120 cm³ CH₄ 的 mass：0.120 / 24.0 = 0.00500 mol → × 16.0 = 0.0800 g
- 14 g C₂H₄ 完全燃烧：C₂H₄ + 3O₂ → 2CO₂ + 2H₂O，0.50 mol C₂H₄ → 1.0 mol CO₂ → 24 dm³

**hydrocarbon 燃烧**：C*ₓ*H*ᵧ* + (*x* + *y*/4) O₂ → *x* CO₂ + (*y*/2) H₂O

例：50 cm³ hydrocarbon 恰好与 250 cm³ O₂ 反应，生成 150 cm³ CO₂（room temperature，H₂O 是 liquid、体积忽略）。体积比 1 : 5 : 3 → *x* = 3；O 守恒：5 × 2 = 3 × 2 + *y*/2 → *y* = 8 → **C₃H₈**。

不是 room conditions 时（例如 400 °C、101 kPa），就要用 *pV* = *nRT*：*p* 用 Pa、*V* 用 m³、*T* 用 K（chapter 4）。

<!-- html: gas volumes：hydrocarbon 燃烧 -->
{{cell combustion}}

<!-- md -->
### C. Volumes and concentrations of solutions

**concentration** *c* = *n* / *V*，单位 mol dm⁻³；*V* 必须先从 cm³ 换成 dm³（÷ 1000）。

- 250 cm³ 溶液含 2.0 g NaOH：*n* = 2.0 / 40.0 = 0.050 mol，*c* = 0.050 / 0.250 = 0.20 mol dm⁻³
- 55 cm³ 0.20 mol dm⁻³ CuSO₄ 里 CuSO₄ 的 mass：0.20 × 55/1000 = 0.011 mol → × 159.6 = 1.8 g（2 s.f.）

**titration** 三步：

1. 已知 *c* 和 *V* 的那个 → mol；
2. 用 equation 的 mole ratio 换成另一个的 mol；
3. ÷ 它的 *V*（dm³）→ *c*。

例：25.0 cm³ NaOH(aq) 恰好被 15.10 cm³ 0.200 mol dm⁻³ H₂SO₄ 中和：2NaOH + H₂SO₄ → Na₂SO₄ + 2H₂O。

*n*(H₂SO₄) = 0.200 × 15.10/1000 = 0.00302 mol → *n*(NaOH) = 2 × 0.00302 = 0.00604 mol → *c* = 0.00604 / 0.0250 = **0.242 mol dm⁻³**

**dilution factor**：真题最爱「先把样品配成 *V*₁、取 *V*₂ 去滴定」。滴定只测了取出来那一份，算回原样品要 × *V*₁ / *V*₂（9701/21 May/June 2025 Q4 的 × 200/5、9701/22 May/June 2025 Q5 的 × 100.0/25.0 = × 4）。

<!-- html: titration 计算（含稀释） -->
{{cell titration}}

<!-- md -->
### D. Deduce stoichiometric relationships

反过来用：实验测出两种物质反应的 mol 数 → 化成最简整数比 → 就是 equation 里的系数。

例：0.0012 mol W（C₅H₁₂O₄）恰好被 0.0020 mol acidified K₂Cr₂O₇ 完全氧化（9701/22 May/June 2026 Q4(c)(i)）。

0.0012 : 0.0020 = 3 : 5 → 3C₅H₁₂O₄ + **5**Cr₂O₇²⁻ + 40H⁺ → 3C₅H₆O₆ + 10Cr³⁺ + 29H₂O

（M1 就是写对 5Cr₂O₇²⁻；之后 Cr、O、H 依次配平，最后用 charge 检查：左边 −10 + 40 = +30，右边 10 × (+3) = +30。）

{{lo 2.4.1}}

<!-- md -->
## Practice

2024–2026 Paper 2 里所有考 chapter 2 的小问，按考试时间排列（含正本在其他章、但这一小问考本章的）。题干里与本章无关的部分只保留到看得懂为止。表格里的空格可以直接填（填对变绿），再展开 **答案** 对照 mark scheme。

<!-- practice: 9701/22 Feb/Mar 2024 -->
### 9701/22 Feb/Mar 2024

Bismuth is an element in Group 15 of the Periodic Table.

#### Q1(b)(i) [1]
Bismuth reduces water to form bismuth oxide, Bi₂O₃. A colourless gas that ignites with a squeaky pop also forms. Construct an equation for the reduction of water by bismuth.

::: answer
2Bi + 3H₂O → Bi₂O₃ + 3H₂
:::

#### Q1(e) [3]
NaBiO₃ can be used to determine the concentration of Mn²⁺(aq):

equation 2　2Mn²⁺ + 5BiO₃⁻ + 14H⁺ → 2MnO₄⁻ + 5Bi³⁺ + 7H₂O

A student dilutes 100.0 cm³ of saturated Mn²⁺(aq) to 1.00 dm³. 25.00 cm³ of the diluted solution is titrated with 0.100 mol dm⁻³ NaBiO₃(aq); 21.50 cm³ is needed. Calculate the concentration, in mol dm⁻³, of Mn²⁺(aq) in the saturated solution. Show your working.

::: answer
- *n*(NaBiO₃) = 21.50 / 1000 × 0.100 = 2.15 × 10⁻³ mol
- *n*(Mn²⁺) in 1.00 dm³ of diluted solution = 2.15 × 10⁻³ × 2/5 × 40 = 0.0344 mol（2 : 5 来自 equation 2，× 40 = 1000 / 25.00）
- 这 0.0344 mol 全部来自 100.0 cm³ saturated solution：*c* = 0.0344 × 1000 / 100 = **0.344 mol dm⁻³**

判分：三步各 1 分。
:::

<!-- practice: 9701/21 May/June 2024 -->
### 9701/21 May/June 2024

#### Q2(c)(ii) [1]
Magnesium nitride reacts with an excess of water to produce ammonia and magnesium hydroxide only. Construct an equation to describe this reaction.

::: answer
Mg₃N₂ + 6H₂O → 3Mg(OH)₂ + 2NH₃
:::

#### Q2(d)(i) [1]
Figure 2.2 shows part of the lattice structure of a crystal of boron nitride. Use Figure 2.2 to deduce the empirical formula of boron nitride.

{{img passyear/extracted/ch02-stoichiometry/img/9701_s24_21_fig2-2.png 420}}

::: answer
BN（B 和 N 交替排列，1 : 1）
:::

<!-- practice: 9701/21 Oct/Nov 2024 -->
### 9701/21 Oct/Nov 2024

Table 1.2 shows the relative abundances of isotopes in a sample of an alloy containing rhodium and iridium only.

| isotope | relative isotopic mass | relative abundance in alloy |
|---|---|---|
| ¹⁰³Rh | 102.91 | 50.00 |
| ¹⁹¹Ir | 190.96 | 15.18 |
| ¹⁹³Ir | 192.96 | 34.82 |

#### Q1(c)(i) [2]
Define relative isotopic mass.

::: answer
- M1 mass of an (atom of an) isotope
- M2 compared to the mass of the unified atomic mass unit **OR** on a scale on which a carbon-12 atom has a mass of exactly 12 units **OR** divided by 1/12 mass of a carbon-12 atom
:::

#### Q1(c)(ii) [2]
Use Table 1.2 to calculate the relative atomic mass, *A*ᵣ, of iridium in the alloy. Give your answer to two decimal places.

*A*ᵣ(Ir) = [[192.35]]

::: answer
(190.96 × 15.18 + 192.96 × 34.82) ÷ (15.18 + 34.82) = **192.35**

注意分母是 Ir 两个 isotope 的 abundance 之和 50.00，不是 100——Rh 不是 iridium。（本小问在分类表里归 chapter 22，因为数据来自 mass spectrum。）
:::

#### Q1(d)(i) [2]
Hydrated rhodium(III) chloride, RhCl₃·xH₂O, contains 20.5% by mass of water of crystallisation. Deduce the integer value of *x* in RhCl₃·xH₂O. Show your working.

*x* = [[3]]

::: answer
- M1 RhCl₃ : H₂O = 79.5 / 209.4 : 20.5 / 18.0 = 0.380 : 1.14 = 1 : 3
  （或 18*x* ÷ (102.9 + 3 × 35.5 + 18*x*) = 0.205）
- M2 *x* = **3**
:::

<!-- practice: 9701/21 May/June 2025 -->
### 9701/21 May/June 2025

{{img passyear/extracted/ch02-stoichiometry/img/9701_s25_21_fig4-1.png 520}}

#### Q4(a) [1]
The structure of vitamin C is shown in Figure 4.1. Deduce the empirical formula of vitamin C.

::: answer
C₃H₄O₃（molecular formula C₆H₈O₆，÷ 2）
:::

#### Q4(b)(i) [1]
A vitamin C tablet is dissolved in water to produce 200.0 cm³ of vitamin C solution. 5.00 cm³ of this solution is added to a flask with approximately 150 cm³ of water and an indicator. Exactly 28.40 cm³ of 5.00 × 10⁻⁴ mol dm⁻³ I₂(aq) reacts with the sample of vitamin C solution in the flask. [*M*ᵣ: vitamin C, 176]

{{img passyear/extracted/ch02-stoichiometry/img/9701_s25_21_fig4-2.png 520}}

Calculate the amount, in mol, of I₂(aq) added to the flask in this titration.

::: answer
28.40 / 1000 × 5.00 × 10⁻⁴ = **1.42 × 10⁻⁵ mol**
:::

#### Q4(b)(ii) [2]
Use your answer to (b)(i) to calculate the mass, in g, of vitamin C in the tablet. Show your working.

::: answer
vitamin C : I₂ = 1 : 1（Figure 4.2）。

- M1 mass in the 5 cm³ sample = 1.42 × 10⁻⁵ × 176 = 2.4992 × 10⁻³ g（写出来可以是 2.50 × 10⁻³，但计算器里保留全部位数）
- M2 mass in the tablet = 2.4992 × 10⁻³ × 200 / 5 = 0.099968 → **0.100 g**（3 s.f.）

两个常见错：用已经 round 过的 2.49 × 10⁻³ 继续乘，得到 0.0996（中间步骤提前四舍五入）；把 0.099968 截断成 0.0999（应该四舍五入）。

也可以先 × 200/5 再 × 176，两种顺序都给分。那 150 cm³ 水是干扰项：它不改变 flask 里 vitamin C 的 mol 数。
:::

<!-- practice: 9701/22 May/June 2025 -->
### 9701/22 May/June 2025

{{img passyear/extracted/ch02-stoichiometry/img/9701_s25_22_fig5-1.png 520}}

#### Q5(a) [1]
Deduce the empirical formula of vitamin C.

::: answer
C₃H₄O₃
:::

#### Q5(b)(i) [1]
All the vitamin C in 150.0 g of lemon is extracted and dissolved in water to make 100.0 cm³ of solution **L**. A 25.0 cm³ sample of **L** is titrated with 5.00 × 10⁻³ mol dm⁻³ I₂(aq); exactly 36.65 cm³ of I₂(aq) reacts. [*M*ᵣ: vitamin C, 176]

{{img passyear/extracted/ch02-stoichiometry/img/9701_s25_22_fig5-2.png 520}}

Calculate the amount, in mol, of I₂(aq) added in the titration.

::: answer
5.00 × 10⁻³ × 36.65 / 1000 = **1.83 × 10⁻⁴ mol**（1.8325 × 10⁻⁴）
:::

#### Q5(b)(ii) [2]
Use your answer to (b)(i) to calculate the percentage by mass of vitamin C present in 150.0 g of lemon.

percentage = [[0.086|0.087]] %

::: answer
- M1 mass of vitamin C in 150 g lemon = 1.8325 × 10⁻⁴ × 176 × 4 = 0.129 g（× 4 = 100.0 / 25.0）
- M2 0.129 / 150 × 100 = **0.086%**（0.087 也接受）
:::

<!-- practice: 9701/22 Feb/Mar 2026 -->
### 9701/22 Feb/Mar 2026

#### Q2(b) [4]
In the laboratory, NO is made in the reaction of copper metal with dilute nitric acid:

8HNO₃(aq) + 3Cu(s) → 3Cu(NO₃)₂(aq) + 4H₂O(l) + 2NO(g)

A student reacts 0.00393 mol Cu with excess dilute HNO₃(aq) at 5 °C and 101 kPa. Calculate the maximum volume, in cm³, of NO(g) that is produced under these conditions.

volume = [[59.9|60]] cm³

::: answer
- M1 *n*(NO) = 0.00393 × 2/3 = 0.00262 mol
- M2 *p* = 101 000 Pa，*R* = 8.31，*T* = 278 K，*n* = 0.00262
- M3 use of *pV* = *nRT*（*V* = *nRT* / *p*）
- M4 *V* = 5.99 × 10⁻⁵ m³ × 10⁶ = **59.9 cm³**

5 °C 不是 room conditions，不能用 24.0 dm³ mol⁻¹。
:::

<!-- practice: 9701/21 May/June 2026 -->
### 9701/21 May/June 2026

#### Q1(e) [3]
Compound X contains sulfur and chlorine only. 100.0 g of X contains 47.49 g of sulfur. The relative molecular mass, *M*ᵣ, of X is 135.2. Determine the molecular formula of X. Show your working.

::: answer
- M1 mass Cl = 100.0 − 47.49 = 52.51 g
- M2 47.49 / 32.1 : 52.51 / 35.5 = 1.48 : 1.48 → empirical formula SCl
- M3 *M*ᵣ(SCl) = 67.6，135.2 / 67.6 = 2 → **S₂Cl₂**

判分：M2 允许 ecf；只写 S₂Cl₂ 不给过程，M3 也给。
:::

#### Q2(c)(ii) [4]
equation 1　2CaCO₃ + 2SO₂ + O₂ → 2CaSO₄ + 2CO₂

Use the ideal gas equation to calculate the volume of O₂(g) that reacts with 0.500 mol of SO₂ at 400 °C and 101 kPa in equation 1. Include units in your answer.

::: answer
- M1 *pV* = *nRT*
- M2 *n*(O₂) = 0.500 ÷ 2 = 0.250 mol
- M3 *T* = 400 + 273 = 673 K
- M4 *V* = 0.250 × 8.31 × 673 ÷ 101 000 = **0.0138 m³**（= 13.8 dm³ = 13 800 cm³）

判分：单位跟数值配套即可（0.014 m³ / 14 dm³ / 14 000 cm³ 都给满分）；M4 允许 ecf。
:::

<!-- practice: 9701/22 May/June 2026 -->
### 9701/22 May/June 2026

{{img passyear/extracted/ch02-stoichiometry/img/9701_s26_22_fig4-2.png 520}}

The molecular formula of X is C₅H₁₂O₄. Complete oxidation of 0.255 g of X occurs when it reacts with exactly 10.0 cm³ of 0.500 mol dm⁻³ acidified K₂Cr₂O₇(aq).

#### Q4(b)(ii) [1]
Calculate the amount, in mol, of K₂Cr₂O₇(aq) used in the reaction.

amount = [[0.005|0.0050|5e-3]] mol

::: answer
10.0 / 1000 × 0.500 = **0.005 mol**（5 × 10⁻³）
:::

#### Q4(b)(iii) [1]
Calculate the amount, in mol, of X present in the 0.255 g sample.

::: answer
*M*ᵣ(C₅H₁₂O₄) = 5 × 12.0 + 12 × 1.0 + 4 × 16.0 = 136 → 0.255 / 136 = **1.875 × 10⁻³ mol**

判分：接受 1.88 × 10⁻³ / 1.9 × 10⁻³（2 × 10⁻³ 需有过程）；**拒绝** 1.880 × 10⁻³、1.90 × 10⁻³、2.0 × 10⁻³、1.87 × 10⁻³。
:::

#### Q4(c)(i) [2]
Compound X and W are a pair of structural isomers. 0.0012 mol of W is completely oxidised when it is heated under reflux with exactly 0.0020 mol of acidified K₂Cr₂O₇(aq) to produce compound Z, C₅H₆O₆. Complete the equation for this reaction.

…C₅H₁₂O₄ + …Cr₂O₇²⁻ + …H⁺ → …C₅H₆O₆ + …Cr³⁺ + …H₂O

::: answer
3C₅H₁₂O₄ + 5Cr₂O₇²⁻ + 40H⁺ → 3C₅H₆O₆ + 10Cr³⁺ + 29H₂O

- M1 系数 5Cr₂O₇²⁻（0.0012 : 0.0020 = 3 : 5）
- M2 全式配平正确
:::

<!-- md -->
{{lo-checklist}}
