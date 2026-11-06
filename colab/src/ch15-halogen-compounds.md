<!-- md #top -->
# Chapter 15 Halogen compounds

Cambridge International AS & A Level Chemistry 9701（2025 / 2026 / 2027）· **Organic chemistry**

{{org-nav}}

- 内容边界与 learning outcome 逐字取自 syllabus；判分句式取自 2024–2026 Paper 2 的 mark scheme，引用写卷号（冲突时以 9701/22 May/June 2026 为准）。
- 🔬 / 🧊 / 📝 开头的 cell 是交互图（打开就能用；空白时 **Runtime → Run all**）。蓝色链接跳到别章：新标签页打开后，**左边目录里高亮的那一项就是目标**。
- 术语 nucleophile / heterolytic fission / carbocation 见 {{xref ch13#s13-2 chapter 13.2}}；carbocation 稳定性的 inductive effect 第一次出现在 {{xref ch14#markovnikov 14.2 D Markovnikov}}。

halogenoalkane 是 organic 合成的「中转站」：它容易从 alkane、alkene、alcohol 做出来，又能变成 alcohol、nitrile、amine、alkene。本章三件事：**怎样做出来（15.1 A）、和 nucleophile 反应（15.1 B–C）、和 base 发生 elimination（15.1 D）**。

<!-- md #halogenoalkanes -->
## 15.1 Halogenoalkanes

### A. 怎样制得

{{lo 15.1.1}}

{{rxn-in halogenoalkane}}

- free-radical substitution 得到的是**混合物**（不同位置、多取代），不适合制备单一 product；
- alkene + HX 遵循 Markovnikov（{{xref ch14#markovnikov 14.2 D}}）；
- alcohol 的几种 halogenating reagent 详见 {{xref ch16#rx-halogenation 16.1 C}}。

### B. primary / secondary / tertiary

按**连着 halogen 的那个 C** 上直接连了几个 alkyl group（R）来分：

| 类型 | 连 X 的 C 上 | 例 |
|---|---|---|
| **primary（1°）** | 1 个 R（或 CH₃X 是 0 个，也归 primary） | 1-bromobutane CH₃CH₂CH₂CH₂Br |
| **secondary（2°）** | 2 个 R | 2-bromobutane CH₃CHBrCH₂CH₃ |
| **tertiary（3°）** | 3 个 R | 2-bromo-2-methylpropane (CH₃)₃CBr |

C₄H₉Br 的四个 structural isomer 正好三类都有（1-bromobutane、1-bromo-2-methylpropane 是 1°；2-bromobutane 是 2°；2-bromo-2-methylpropane 是 3°）。同一个 *M*ᵣ，boiling point 1° > 2° > 3°（分子越「圆」，接触面越小，id-id 越弱）。

{{lo 15.1.2}}

<!-- md #rx-nucsub -->
### C. nucleophilic substitution

C–X bond 是 polar 的：X 比 C electronegative，C 带 δ+，X 带 δ−。**nucleophile**（electron pair donor）进攻 δ+ 的 C，X 以 **X⁻** 离开（C–X heterolytic fission）。

{{lo 15.1.3}}

| nucleophile | reagent and conditions | product | 说明 |
|---|---|---|---|
| OH⁻ | **NaOH(aq) and heat**（reflux） | **alcohol** | 也叫 hydrolysis；H₂O 也能水解但慢得多（OH⁻ 带整个负电荷，是更强的 nucleophile） |
| CN⁻ | **KCN in ethanol and heat** | **nitrile** | 碳链**多一个 C**：C₂H₅Br → C₂H₅CN（propanenitrile）；用于延长碳链（{{xref ch19#nitriles chapter 19}}） |
| NH₃ | **NH₃ in ethanol heated under pressure** | **amine** | NH₃ 要 excess，否则 product amine 再当 nucleophile → secondary / tertiary amine 混合物 |
| H₂O（AgNO₃(aq) 里的） | **aqueous silver nitrate in ethanol** | alcohol + X⁻ → AgX 沉淀 | 鉴别 halogen，见本节 E |

equation 例：CH₃CH₂Br + OH⁻ → CH₃CH₂OH + Br⁻；CH₃CH₂Br + CN⁻ → CH₃CH₂CN + Br⁻；CH₃CH₂Br + 2NH₃ → CH₃CH₂NH₂ + NH₄Br。

为什么用 ethanol 做 solvent：halogenoalkane 不溶于水；KCN 用水会给出 OH⁻（得到 alcohol）。

<!-- md #sn1-sn2 -->
### D. S<sub>N</sub>1 与 S<sub>N</sub>2

{{lo 15.1.5}}

| | **S<sub>N</sub>2** | **S<sub>N</sub>1** |
|---|---|---|
| 典型底物 | **primary** | **tertiary** |
| 步数 | **一步**：nucleophile 进攻和 C–X 断开同时发生 | **两步**：① C–X 先断（慢）→ carbocation；② nucleophile 进攻 C⁺（快） |
| 中间体 | 没有（只有 transition state，C 上五个 group，虚线表示半断半成的 bond） | **tertiary carbocation**（planar，sp²） |
| rate 取决于 | [halogenoalkane] **和** [nucleophile]（「2」= rate-determining step 有两个 species） | 只有 [halogenoalkane]（「1」） |
| 立体结果 | nucleophile 从 X 的**背面**进攻 → configuration 翻转 | 平面 carbocation 两面都能被进攻 |

**S<sub>N</sub>2 的得分点**（9701/22 May/June 2026 Q5(b)(i)，CN⁻ + 1° chloroalkane）：

- **M1** curly arrow 从 **CN⁻ 里 C 上的 lone pair** 指向 δ+ 的 C；
- **M2** C–Cl 上正确的 dipole（C<sup>δ+</sup>–Cl<sup>δ−</sup>）**AND** curly arrow 从 C–Cl bond 指向 Cl。
- 画 transition state 时 nucleophile 与 X 在 C 的两侧（约 180°），整体带负电荷（[ … ]⁻）。

**S<sub>N</sub>1 的得分点**（tertiary + OH⁻ 或 NH₃）：M1 C–Br dipole + curly arrow 从 C–Br 指向 Br（形成 carbocation + Br⁻）；M2 nucleophile 的 lone pair → C⁺；NH₃ 时还要 M3：N–H bond 断开的箭头（失去 H⁺ 得到中性 amine）。

**inductive effect**（为什么 tertiary 走 S<sub>N</sub>1）：三个 alkyl group 都向 C⁺ 推电子（positive inductive effect），分散正电荷，**tertiary carbocation 最稳定**，所以 3° 的 C–X 可以先断开；primary carbocation 太不稳定，1° 只能走一步的 S<sub>N</sub>2。另外 3° 的 C 被三个 alkyl group 挤住，nucleophile 很难从背面靠近（steric hindrance）。

mark scheme（9701/22 Feb/Mar 2025 Q4(f)(ii)）：M1 **2-bromo-2-methylpropane AND more stable carbocation**；M2 **alkyl groups have an inductive effect AND it has more alkyl groups attached to C⁺**。

{{lo 15.1.6}}

<!-- html: S<sub>N</sub>1 / S<sub>N</sub>2 分步 #sn-mech -->
{{cell sn-mech}}

<!-- html3d: backside attack 与平面 carbocation #sn2-3d -->
{{cell sn2-3d}}

<!-- md #rx-agno3 -->
### E. AgNO₃ 鉴别 halogen，以及 C–X bond 的强弱

**做法**：几滴 halogenoalkane + **aqueous silver nitrate in ethanol**，水浴温热。水（nucleophile）慢慢 hydrolyse halogenoalkane，放出的 X⁻ 立刻和 Ag⁺ 形成沉淀：

R–X + H₂O → R–OH + H⁺ + X⁻；Ag⁺(aq) + X⁻(aq) → AgX(s)

| halogenoalkane | 沉淀 | 出现快慢 |
|---|---|---|
| chloroalkane | **white** AgCl | 最慢 |
| bromoalkane（例：bromoethane） | **cream** AgBr | 中 |
| iodoalkane | **yellow** AgI | **最快** |

ethanol 的作用：让 halogenoalkane 和水溶在一起（common solvent）。

**为什么 iodoalkane 最快**：决定速率的是 C–X bond 要断开；**bond energy C–F 467 > C–Cl 346 > C–Br 290 > C–I 228 kJ mol⁻¹**，C–I 最弱、最容易断。注意：C–F 最 polar，但反应最慢——**bond strength 比 bond polarity 更重要**。

mark scheme（9701/22 Feb/Mar 2026）：M1 顺序 **iodo > bromo > chloro**；M2 **carbon–halogen bond gets weaker down the group**（所以断得快）。观察题：AgNO₃ + CHCl₃ → M1 white precipitate；M2 CHCl₃ is hydrolysed / chloride ions are released。

{{lo 15.1.7}}

<!-- html: AgNO₃ 试管：沉淀颜色与出现时间 #agno3-rate -->
{{cell agno3-rate}}

<!-- md #rx-elimination -->
### F. elimination：同一个 NaOH，换个 solvent

{{lo 15.1.4}}

bromoethane + **NaOH in ethanol and heat** → ethene + NaBr + H₂O：OH⁻ 在 ethanol 里主要当 **base**，从和 C–Br 相邻的 C 上拿走一个 H⁺，同时 C–Br 断开，两 C 之间形成 C=C。消去的小 molecule 是 **HBr**。

CH₃CH₂Br + NaOH → CH₂=CH₂ + NaBr + H₂O（ethanolic，heat）

| 条件 | 主要 reaction | product |
|---|---|---|
| **NaOH(aq)**，heat | nucleophilic substitution（OH⁻ 当 nucleophile） | alcohol |
| **NaOH in ethanol**，heat | elimination（OH⁻ 当 base） | alkene |

不对称的 2° / 3° halogenoalkane 消去时 H 可以从两边的 C 拿 → 可能有多种 alkene（2-bromobutane → but-1-ene + cis / trans but-2-ene，共 3 种）。

alkene 的后续反应见 {{xref ch14#rx-alkene-add 14.2 B}}。

<!-- html: substitution 还是 elimination：选 nucleophile 和 solvent #sub-vs-elim -->
{{cell sub-vs-elim}}

<!-- md #halo-out -->
### G. halogenoalkane 能变成什么

{{rxn-out halogenoalkane}}

<!-- md #practice -->
## Practice

2024–2026 Paper 2 里所有考 chapter 15 的小问，按考试时间排列（含正本在其他章、但这一小问考本章的）。展开 **答案** 对照 mark scheme。

<!-- practice: 9701/22 Feb/Mar 2024 -->
### 9701/22 Feb/Mar 2024

Cl₂ reacts readily with propene to form **K**, 1,2-dichloropropane. **K** can be used to form **L**.
![Fig. 2.1](passyear/extracted/ch09-periodicity/img/9701_m24_22_fig2-1.png)

#### Q2(d)(ii) [1]

Identify the reagent and conditions for reaction 2.

::: answer
**答案** — NaOH in ethanol **AND** heat

:::

<!-- practice: 9701/23 May/June 2024 -->
### 9701/23 May/June 2024

Substitution reactions of NH₃ and OH⁻ with halogenoalkanes both involve a lone pair of electrons.

#### Q4(c)(i) [1]

Name the role of NH₃ and OH⁻ in these reactions.

::: answer
**答案** — nucleophile

:::

#### Q4(c)(ii) [1]

Suggest which species, NH₃ or OH⁻, is more reactive during these reactions. Explain your answer.

::: answer
**答案** — OH⁻（more reactive because）negatively charged species more attracted to halogenoalkane
and/or Cᵟ⁺ and/or intermediate and/or C⁺
　**OR** NH₃（more reactive because）N electrons less tightly held
　**OR** N is more able to donate (lp) electrons (to make the covalent bond)
　**OR** N is less electronegative

**判分** — 选 OH⁻ 或 NH₃ 皆可给分，只要解释逻辑自洽（ORA）。

:::

#### Q4(e)(i) [3]

Complete Figure 4.2 to show the mechanism for the S<sub>N</sub>1 reaction that occurs when CH₃CHBrC₂H₅
reacts with NH₃ to produce CH₃CH(NH₂)C₂H₅. Include charges, dipoles, lone pairs of electrons and
curly arrows, as appropriate.

![Figure 4.2](passyear/extracted/ch03-chemical-bonding/img/9701_s24_23_fig4-2.png)

::: answer
**答案**（三步机理：CH₃CHBrC₂H₅ → 二级碳正离子中间体 + Br⁻ → 经 NH₃ 进攻生成
CH₃CH(NH₃⁺)C₂H₅ → 失去 H⁺ 生成 CH₃CH(NH₂)C₂H₅）
- M1：2-bromobutane 的 C—Br 键上标正确 dipole，并有 curly arrow 从该键指向 Br
- M2：NH₃ 的 lone pair 上有 curly arrow 指向中间体的 C⁺
- M3：curly arrow 表示其中一条 N—H 键断裂、箭头指向 N（即该 H⁺ 被 later 转移走，得到中性胺
  产物）

:::

#### Q4(f)(i) [1]

Complete Table 4.1 by drawing the structural formula of the intermediate that is formed when
2-bromo-2-methylpropane reacts in an S<sub>N</sub>1 reaction.

**Table 4.1**

| | 2-bromobutane | 2-bromo-2-methylpropane |
|---|---|---|
| structural formula of intermediate in S<sub>N</sub>1 reaction | C⁺ 连接 H、C₂H₅、CH₃（二级碳正离子） | （需自行画出） |

::: answer
**答案** — 官方 mark scheme 该格实际留空（无印刷图样），按题目逻辑类推：2-bromo-2-methylpropane
是 (CH₃)₃CBr，失去 Br⁻ 后得到的中间体应画成 **C⁺ 上连接三个 CH₃ 基团**（三级碳正离子），
与左栏 2-bromobutane 那格的画法风格一致（C⁺ 居中，三条键分别标 CH₃、CH₃、CH₃）。

:::

#### Q4(f)(ii) [2]

Identify the halogenoalkane in Table 4.1 that has the greater tendency to react using the
S<sub>N</sub>1 mechanism. Explain your answer.

::: answer
**答案**
- M1 2-bromo-2-methylpropane **AND** more stable carbocation / C⁺
- M2 alkyl groups have an inductive effect (of alkyl groups) **AND** 2-bromo-2-methylpropane has
  more / most alkyl groups attached (to C⁺) / carbocation contains more alkyl groups

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

#### Q5(d)(i) [1]

Y is made from Q in a three-step reaction, as shown in Figure 5.4.

![Figure 5.4](passyear/extracted/ch14-hydrocarbons/img/9701_s24_23_fig5-4.png)

Draw the structure of W in the box in Figure 5.4.

::: answer
**答案** — W = cyclohexane-1,2-dicarbonitrile（cyclohexane 1,2 位上 Q 的两个 Br 都被 KCN 取代成 –CN）

:::

<!-- practice: 9701/21 Oct/Nov 2024 -->
### 9701/21 Oct/Nov 2024

CHCl₃ is another halogenoalkane. CHCl₃ forms when propanone reacts with NaClO. NaClO is made from chlorine in a disproportionation reaction.

#### Q2(c)(iv) [2]

Aqueous AgNO₃ dissolved in ethanol reacts with an aqueous solution of CHCl₃. State what is observed in this reaction. Explain your answer.

::: answer
**答案**
- M1 white precipitate / white ppt forms
- M2 CHCl₃ is hydrolysed / chloride ions are released
- OR Cl⁻ / chloride ions which are released react with Ag⁺
- OR silver chloride / AgCl is formed

:::

<!-- practice: 9701/22 Oct/Nov 2024 -->
### 9701/22 Oct/Nov 2024

#### Q4(c)(i) [2]

Complete Fig. 4.1 to draw the structure of compound A and name compound B.

::: answer
**答案**

- **A** = HOCH₂CH₂OH（ethane-1,2-diol，reaction 2 是 BrCH₂CH₂Br 与 NaOH(aq) 的 nucleophilic
  substitution / alkaline hydrolysis，两个 C–Br 都被 OH 取代）
- **B** = bromoethene（reaction 3 是 NaOH in ethanol 对 BrCH₂CH₂Br 的消除，脱去一分子 HBr）

:::

#### Q4(c)(iii) [1]

In reaction 5, compound B reacts with an excess of NaOH dissolved in ethanol. The products are
HBr, H₂O and an unsaturated hydrocarbon D. Suggest the identity of D.

::: answer
**答案** — C₂H₂（ethyne）——bromoethene（CH₂=CHBr）在过量 NaOH/ethanol 下再消去一分子 HBr，
C=C 进一步变成 C≡C

:::

<!-- practice: 9701/22 Feb/Mar 2025 -->
### 9701/22 Feb/Mar 2025

1,2-dichloroethane, ClCH₂CH₂Cl, reacts with NaOH to produce an unsaturated compound, C₂H₃Cl, as shown in reaction 7.
reaction 7　ClCH₂CH₂Cl + NaOH → C₂H₃Cl + H₂O + NaCl

#### Q1(c)(ii) [1]

State the conditions for reaction 7.

::: answer
**答案** — ethanol (as solvent) **AND** heat

:::

<!-- practice: 9701/22 May/June 2025 -->
### 9701/22 May/June 2025

#### Q4(b)(ii) [1]

In step 2, E reacts with a suitable reagent to produce butanenitrile. Identify the reagent and
conditions required in step 2.

::: answer
**答案** — KCN / potassium cyanide in ethanol / C₂H₅OH **AND** heat

:::

<!-- practice: 9701/22 Oct/Nov 2025 -->
### 9701/22 Oct/Nov 2025

#### Q4(b) [1]

State the reagent and solvent required for reaction 2.

::: answer
**答案** — sodium hydroxide **AND** water

:::

<!-- practice: 9701/22 Feb/Mar 2026 -->
### 9701/22 Feb/Mar 2026

#### Q3(a) [1]

Explain why 2-chlorobutane is classified as a secondary halogenoalkane.

::: answer
**答案** — (organic molecule where) carbon (of C—Hal) is bonded to two other C atoms

:::

#### Q3(d) [2]

The rates of hydrolysis of three secondary halogenoalkanes, B, C and D, are compared.

![Figure 3.3](passyear/extracted/ch13-organic-intro/img/9701_m26_22_fig3-3.png)

Each halogenoalkane is dissolved in ethanol and reacted with AgNO₃(aq). Identify the order of
the rates of hydrolysis of compounds B, C and D. Explain your answer.

::: answer
**答案**

- M1 fastest　D > C > B　slowest（B = Cl，C = Br，D = I）
- M2 carbon—halogen gets weaker down the group (so breaks faster)

:::

#### Q4(c)(i) [2]

The reaction mechanism of the synthesis in Figure 4.3 has a single step.

Complete Figure 4.3 to show this mechanism. Include lone pairs, charges, dipoles and curly
arrows as appropriate.

::: answer
**答案**
- M1 curly arrow from lone pair on C of CN⁻ to (δ+)C of C–Cl
- M2 correct dipole of δ⁺C—Clδ⁻ AND curly arrow from bond to Cl

:::

#### Q4(c)(ii) [1]

Identify the nucleophile in Figure 4.3.

::: answer
**答案** — CN⁻ / cyanide

:::

#### Q4(c)(iii) [1]

Identify the mechanism of the reaction in Figure 4.3.

::: answer
**答案** — nucleophilic substitution / S<sub>N</sub>2

### (d)

Figure 4.4 describes a sequence of reactions, starting with CH₂(CN)COOH, to form E.

![Figure 4.4](passyear/extracted/ch03-chemical-bonding/img/9701_m26_22_fig4-4.png)

:::

<!-- practice: 9701/22 May/June 2026 -->
### 9701/22 May/June 2026

Figure 4.1 shows two reactions of compound D.
![Figure 4.1](passyear/extracted/ch02-stoichiometry/img/9701_s26_22_fig4-1.png)
D = (CH₃)₃C–OH（2-methylpropan-2-ol / tert-butanol，图中以十字骨架 + OH 标注表示）。

#### Q4(a)(i) [1]

D reacts with a single reagent, G, to produce compound E. Identify reagent G.

::: answer
**答案** — PCl₅ **OR** SOCl₂ **OR** HCl **OR** PCl₃（或等效名称）

**判分** — A thionyl chloride / sulfur oxide dichloride（SOCl₂）；A phosphorus pentachloride / phosphorus trichloride；A conc. HCl / concentrated hydrochloric acid；A hydrogen chloride / HCl(g)；I 单独 hydrochloric acid / HCl(aq) / dilute HCl；I NaCl／KCl + conc. H₂SO₄／H₃PO₄；R PCl₅(aq)

:::

<!-- md -->
{{lo-checklist}}
