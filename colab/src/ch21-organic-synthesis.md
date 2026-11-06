<!-- md #top -->
# Chapter 21 Organic synthesis

Cambridge International AS & A Level Chemistry 9701（2025 / 2026 / 2027）· **Organic chemistry**

{{org-nav}}

- 内容边界与 learning outcome 逐字取自 syllabus；判分句式取自 2024–2026 Paper 2 的 mark scheme，引用写卷号（冲突时以 9701/22 May/June 2026 为准）。
- 🔬 / 🧊 / 📝 开头的 cell 是交互图（打开就能用；空白时 **Runtime → Run all**）。蓝色链接跳到别章：新标签页打开后，**左边目录里高亮的那一项就是目标**。

chapter 21 没有新 reaction：它把 13–20 章的全部 reaction 当作工具箱，考三件事——**认出 functional group 并预测反应（21.1.1）、设计多步路线（21.1.2）、分析给定路线（21.1.3）**。下面的 🔬 反应网络就是整个 organic 部分的地图：点任意一条反应，会跳到它详写的那一章。

<!-- html: organic 反应网络（13–20 章全部 reaction） #roadmap -->
{{cell roadmap}}

<!-- md #s21-1 -->
## 21.1 Organic synthesis

<!-- md #identify -->
### A. 认出 functional group，预测性质和反应

{{lo 21.1.1}}

**(a) 用 syllabus 里的 test 认 functional group**：

| test | 阳性现象 | 说明有 | 详见 |
|---|---|---|---|
| Br₂(aq) | orange → colourless | C=C | {{xref ch14#rx-alkene-add 14.2 B}} |
| AgNO₃(aq) in ethanol，warm | white / cream / yellow ppt | C–Cl / C–Br / C–I | {{xref ch15#rx-agno3 15.1 E}} |
| Na(s) | effervescence（H₂） | –OH（alcohol 或 COOH） | {{xref ch16#rx-sodium 16.1 E}} |
| Na₂CO₃ / NaHCO₃ | effervescence（CO₂） | –COOH | {{xref ch18#rx-acid-reactions 18.1 B}} |
| acidified K₂Cr₂O₇，warm | orange → green | 1° / 2° alcohol 或 aldehyde | {{xref ch16#rx-oxidation 16.1 F}} |
| 2,4-DNPH | orange ppt | C=O（aldehyde / ketone，**不含** COOH、ester） | {{xref ch17#rx-tests 17.1 D}} |
| Tollens' / Fehling's | silver mirror / red-brown ppt | aldehyde | {{xref ch17#rx-tests 17.1 D}} |
| alkaline I₂(aq) | pale yellow ppt（CHI₃） | CH₃CO– 或 CH₃CH(OH)– | {{xref ch16#rx-iodoform 16.1 I}} |

**(b) 一个 molecule 有几个 functional group 时，每个 reagent 只和「它认识的」基团反应**：

| reagent | 反应的基团 | 不反应的基团（常考陷阱） |
|---|---|---|
| **NaBH₄** | aldehyde、ketone 的 C=O | COOH、ester、C=C |
| **LiAlH₄** | aldehyde、ketone、**COOH**（、ester） | C=C |
| H₂ / Pt or Ni，heat | C=C（也会还原 C=O） | — |
| Br₂(aq)、HBr | C=C | C=O |
| Na(s) | alcohol 的 OH、COOH | ether、ester |
| NaOH(aq) | COOH（neutralise）、halogenoalkane（substitution）、ester（hydrolysis） | alcohol |
| Na₂CO₃ | 只有 COOH | alcohol |
| acidified K₂Cr₂O₇，reflux | 1° OH → COOH、2° OH → C=O、CHO → COOH | 3° OH、ketone |
| hot conc. acidified KMnO₄ | C=C 断开；也氧化 1° / 2° OH、CHO | 3° OH |
| conc. H₂SO₄ / Al₂O₃，heat | alcohol → alkene（dehydration） | — |

例（9701/23 May/June 2025 Q5）：W = CH₂=C(CH₃)COOH 用 LiAlH₄ → COOH 变 CH₂OH，**C=C 不受影响**；W 用 methanol / conc. H₂SO₄ → 只酯化 COOH。

<!-- html: 多官能团 molecule × reagent：哪些基团会反应 #fg-identify -->
{{cell fg-identify}}

<!-- md #routes -->
### B. 设计多步合成路线

{{lo 21.1.2}}

**先数碳**：目标比起点多一个 C → 路线里一定有 **CN⁻**（halogenoalkane + KCN → nitrile；carbonyl + HCN → hydroxynitrile），见 {{xref ch19#rx-nitrile-hydrolysis chapter 19 的「数碳」}}；碳数相同 → 只做 functional group interconversion；碳数减少 → hot conc. KMnO₄ 断 C=C（或 iodoform 去掉一个 C）。

**再看 functional group 怎么转**：alcohol 和 halogenoalkane 是两个「中转站」，几乎所有路线都经过其中一个。

| 起点 → 目标 | 路线 |
|---|---|
| alkene → alcohol | 一步：H₂O(g), H₃PO₄；或两步：HBr → NaOH(aq) |
| alkane → alcohol | Cl₂ / UV → NaOH(aq), heat |
| alcohol → alkene | conc. H₂SO₄ 或 Al₂O₃, heat |
| 1° alcohol → aldehyde / acid | acidified K₂Cr₂O₇：distillation / reflux |
| alcohol → 多一个 C 的 acid | HBr(g) 或 PCl₅ / SOCl₂（→ halogenoalkane）→ KCN in ethanol（→ nitrile）→ dilute acid, reflux |
| aldehyde → 多一个 C 的 hydroxy acid | HCN, KCN → dilute acid hydrolysis |
| alkene → diol | cold dilute acidified KMnO₄ |
| acid → ester | alcohol + conc. H₂SO₄ |
| ketone → alkene | NaBH₄（→ 2° alcohol）→ conc. H₂SO₄, heat |
| halogenoalkane → amine | excess NH₃ in ethanol, under pressure |

每一步答题都要写 **reagent AND condition**（例如「KCN **in ethanol**, **heat**」「K₂Cr₂O₇ **acidified**, **distil**」），漏写条件常常丢分；中间产物要画出结构。

<!-- html: 路线谜题：从起点到目标，每一步选 reagent #route-puzzle -->
{{cell route-puzzle}}

<!-- md #analyse -->
### C. 分析给定的路线：reaction type、reagent、by-product

{{lo 21.1.3}}

拿到一条路线，逐步回答三个问题：

1. **这一步是什么 type**：addition / substitution / elimination / hydrolysis / condensation / oxidation / reduction（{{xref ch13#s13-2 13.2 的术语}}）；有 mechanism 的要说出 mechanism 名（free-radical substitution、electrophilic addition、nucleophilic substitution、nucleophilic addition）；
2. **reagent 和 condition**：照 registry / syllabus 的写法；
3. **by-product**：

| 步骤 | 常见 by-product |
|---|---|
| alcohol + PCl₅ / SOCl₂ / PCl₃ | POCl₃ + HCl / SO₂ + HCl / H₃PO₃ |
| halogenoalkane + NaOH(aq) / KCN / NH₃ | NaX / KX / NH₄X |
| elimination（NaOH in ethanol） | NaX + H₂O；不对称时还有**其他 alkene isomer** |
| dehydration | H₂O；不对称 alcohol 还有其他 alkene isomer |
| free-radical substitution | HCl / HBr，以及**多取代、不同位置**的 halogenoalkane |
| HX + 不对称 alkene | minor 的 Markovnikov 位置异构体 |
| nitrile hydrolysis | NH₄⁺（acid）/ NH₃（alkali） |
| esterification / ester hydrolysis | H₂O / alcohol（或 acid） |
| HCN 加到 ethanal 等 | 两个 enantiomers（racemic mixture） |

「possible by-products」题最喜欢考：free-radical substitution 的多取代物、不对称 alkene 加成或 elimination 得到的 positional isomer、racemic mixture。

<!-- md #practice -->
## Practice

2024–2026 Paper 2 里所有考 chapter 21 的小问，按考试时间排列。展开 **答案** 对照 mark scheme。

<!-- practice: 9701/22 Feb/Mar 2024 -->
### 9701/22 Feb/Mar 2024

#### Q4(b)(i) [1]

Give the structural formula of Q.

::: answer
**答案** — CH₃CHBrCH₂CH₃

:::

#### Q4(b)(ii) [1]

Name the mechanism in reaction 2.

::: answer
**答案** — nucleophilic substitution

:::

#### Q4(b)(iii) [1]

Complete the equation for reaction 3. R is represented as C₄H₉CN.

C₄H₉CN + ……

::: answer
**答案** — C₄H₉CN + 2H₂O + H⁺ → C₄H₉COOH + NH₄⁺

:::

#### Q4(c)(iii) [2]

T also has a single functional group. Use the information in (c)(i) and your answer to (c)(ii) to
identify T and U. Draw the structures of T and U in the boxes.

::: answer
**答案**（官方 MS 把这一问的题号误印成 "4(c)(iv)"，
QP 上实际是 (c)(iii)，以 QP 为准）
- T = ethanol，HOCH₂CH₃
- U = ethyl 2-methylbutanoate，CH₃CH₂CH(CH₃)COOCH₂CH₃（与 (c)(i) 的 7 个碳、S 的 2-methylbutanoic
  acid 结构一致）

（结构图见 mark scheme）

（结构图见 mark scheme）

**判分** — T、U 各 1 分

:::

<!-- practice: 9701/23 May/June 2024 -->
### 9701/23 May/June 2024

#### Q5(a) [1]

M reacts to form R by the addition of one reagent, as shown in Figure 5.1.

![Figure 5.1](passyear/extracted/ch14-hydrocarbons/img/9701_s24_23_fig5-1.png)

Identify the reagent and conditions for this reaction.

::: answer
**答案** — cold dilute KMnO₄ OR cold dilute potassium manganate(VII)

:::

#### Q5(b)(i) [2]

R is also made from M by two steps, as shown in Figure 5.2.

![Figure 5.2](passyear/extracted/ch14-hydrocarbons/img/9701_s24_23_fig5-2.png)

Identify the reagents and conditions for steps 1 and 2 in Figure 5.2.

::: answer
**答案**
- step 1 — Br₂ (in the dark)
- step 2 — NaOH(aq) + heat

:::

#### Q5(b)(ii) [1]

Name the mechanism for step 1 in Figure 5.2.

::: answer
**答案** — electrophilic addition

:::

#### Q5(d)(i) [1]

Y is made from Q in a three-step reaction, as shown in Figure 5.4.

![Figure 5.4](passyear/extracted/ch14-hydrocarbons/img/9701_s24_23_fig5-4.png)

Draw the structure of W in the box in Figure 5.4.

::: answer
**答案** — W = cyclohexane-1,2-dicarbonitrile（cyclohexane 1,2 位上 Q 的两个 Br 都被 KCN 取代成 –CN）

:::

#### Q5(d)(ii) [1]

In step 2, W is heated with HCl(aq) to produce X and an inorganic product. Identify the formula
of the inorganic product.

::: answer
**答案** — NH₄Cl

:::

#### Q5(d)(iii) [1]

In step 3, X reacts with reducing agent Z to produce Y. Complete the equation for the reaction of
X with Z. Use a molecular formula to represent the organic product. Use [H] to represent one atom
of hydrogen from Z.

…… C₈H₁₂O₄ + ……[H] →

::: answer
**答案** — C₈H₁₂O₄ + 8[H] → C₈H₁₆O₂ + 2H₂O

:::

#### Q5(d)(iv) [1]

Identify Z.

::: answer
**答案** — LiAlH₄

:::

<!-- practice: 9701/22 May/June 2025 -->
### 9701/22 May/June 2025

#### Q4(a)(i) [1]

Propanoic acid, CH₃CH₂COOH, reacts with reducing agent Q to produce propan-1-ol,
CH₃CH₂CH₂OH. Suggest the formula of reducing agent Q.

::: answer
**答案** — LiAlH₄

:::

#### Q4(a)(ii) [1]

Complete the equation to show the reduction of propanoic acid to propan-1-ol. Use [H] to
represent one atom of hydrogen from Q.

……CH₃CH₂COOH + ……[H] →

::: answer
**答案** — CH₃CH₂COOH + 4[H] → CH₃CH₂CH₂OH + H₂O

:::

#### Q4(b)(i) [1]

Propan-1-ol is converted to compound T in a three-step synthesis. In step 1, SOCl₂ is added to
propan-1-ol to produce compound E. Name the type of reaction that occurs in step 1.

::: answer
**答案** — substitution

:::

#### Q4(b)(ii) [1]

In step 2, E reacts with a suitable reagent to produce butanenitrile. Identify the reagent and
conditions required in step 2.

::: answer
**答案** — KCN / potassium cyanide in ethanol / C₂H₅OH **AND** heat

:::

#### Q4(b)(iii) [2]

In step 3, butanenitrile is heated with NaOH(aq). Construct an equation to describe the reaction
of butanenitrile with NaOH(aq) in step 3.

::: answer
**答案**
- CH₃CH₂CH₂CN + NaOH + H₂O → CH₃CH₂CH₂CO₂Na + NH₃
- OR CH₃CH₂CH₂CN + NaOH + 2H₂O → CH₃CH₂CH₂CO₂Na + NH₄OH

**判分** — M1 correct organic product (as molecule or anion)；M2 rest of equation is correct

:::

#### Q4(b)(iv) [1]

Name the type of reaction that occurs in step 3.

::: answer
**答案** — (alkaline) hydrolysis

:::

<!-- practice: 9701/22 Oct/Nov 2025 -->
### 9701/22 Oct/Nov 2025

#### Q4(a)(i) [1]

Reaction 1 in Figure 4.1 takes place in the presence of sunlight.

C₃H₈ + Cl₂ → CH₃CH₂CH₂Cl + HCl

The reaction takes place via initiation, propagation and termination steps. Name the mechanism
shown by reaction 1.

::: answer
**答案** — free-radical substitution

:::

#### Q4(a)(iv) [1]

Compound Q is a by-product of reaction 1：CH₃–CHCl–CH₂Cl。Name Q.

::: answer
**答案** — 1,2-dichloropropane

:::

#### Q4(b) [1]

State the reagent and solvent required for reaction 2.

::: answer
**答案** — sodium hydroxide **AND** water

:::

#### Q4(c)(ii) [1]

Construct an equation to represent reaction 3. Use [O] to represent an atom of oxygen from the
oxidising agent.

::: answer
**答案** — CH₃CH₂CH₂OH + 2[O] → CH₃CH₂COOH + H₂O

:::

#### Q4(d)(i) [1]

CH₃CH₂COOH reacts with an unsaturated alcohol R to form unsaturated ester S. State the type of
reaction that forms S.

::: answer
**答案** — condensation

:::

<!-- md -->
{{lo-checklist}}
