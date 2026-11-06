<!-- md #top -->
# Chapter 14 Hydrocarbons

Cambridge International AS & A Level Chemistry 9701（2025 / 2026 / 2027）· **Organic chemistry**

{{org-nav}}

- 内容边界与 learning outcome 逐字取自 syllabus；判分句式取自 2024–2026 Paper 2 的 mark scheme，引用写卷号（冲突时以 9701/22 May/June 2026 为准）。
- 🔬 / 🧊 / 📝 开头的 cell 是交互图（打开就能用；空白时 **Runtime → Run all**）。蓝色链接跳到别章：新标签页打开后，**左边目录里高亮的那一项就是目标**。
- 术语（free radical、electrophile、addition …）见 {{xref ch13#s13-2 chapter 13.2}}；sp² / π bond 见 {{xref ch13#s13-3 13.3}}。

| | alkane | alkene |
|---|---|---|
| general formula | C<sub>n</sub>H<sub>2n+2</sub> | C<sub>n</sub>H<sub>2n</sub>（一根 C=C） |
| saturated? | saturated（只有 single bond） | unsaturated（有 π bond） |
| C 的 hybridisation | 全部 sp³，109.5° | C=C 的两个 C 是 sp²，120°，planar |
| 典型 reaction | combustion、free-radical substitution | **electrophilic addition**、oxidation、addition polymerisation |
| 本章小节 | 14.1 | 14.2 |

<!-- md #alkanes -->
## 14.1 Alkanes

### A. alkane 从哪里来

crude oil 是 hydrocarbon（alkane、cycloalkane、arene）的复杂混合物；refinery 先用 **fractional distillation** 按 boiling point 分成 fractions，再用 cracking 把用途少的长链 fraction 变成短链。

{{lo 14.1.1}}

{{rxn-in alkane}}

hydrogenation 的详细内容在 14.2 B（它首先是 alkene 的 reaction）；cracking 见本节 D。

<!-- md #rx-combustion -->
### B. combustion，以及汽车尾气

{{lo 14.1.2}}

**(a) complete combustion**（O₂ 充足）→ CO₂ + H₂O；**incomplete combustion**（O₂ 不足，例如汽车引擎里）→ CO（甚至 C，soot）+ H₂O：

- C₈H₁₈ + 12½O₂ → 8CO₂ + 9H₂O
- C₈H₁₈ + 8½O₂ → 8CO + 9H₂O

配平技巧：先配 C，再配 H，最后数 O（O₂ 可以写半数）。

**internal combustion engine 的三种 pollutant**：

| pollutant | 怎样产生 | 危害 | catalytic converter 里变成 |
|---|---|---|---|
| **CO** | incomplete combustion | toxic：和 haemoglobin 结合，血液不能运 O₂；无色无味 | 被 oxidise：2CO + O₂ → 2CO₂ |
| **NOₓ**（NO、NO₂） | 引擎里高温使空气中的 N₂ 与 O₂ 反应：N₂ + O₂ → 2NO | acid rain、photochemical smog（见 chapter 12） | 被 reduce 成 N₂：2CO + 2NO → 2CO₂ + N₂ |
| **unburnt hydrocarbons** | 燃料没烧完 | photochemical smog；部分致癌 | 被 oxidise 成 CO₂ + H₂O |

catalytic converter 里是 Pt / Pd / Rh 等 metal 涂在蜂窝状 ceramic 上（表面积大）；它**不能**减少 CO₂（greenhouse gas）。

{{lo 14.1.6}}

<!-- html: 配平 combustion、跟踪尾气里的 pollutant #combustion -->
{{cell combustion}}

<!-- md #rx-frs -->
### C. free-radical substitution

{{lo 14.1.3}}

ethane + Cl₂，**ultraviolet light**（Br₂ 同理）→ chloroethane + HCl。三步：

| 步骤 | equation | 说明 |
|---|---|---|
| **initiation** | Cl₂ → 2Cl• | UV 提供能量，Cl–Cl **homolytic fission**（Cl–Cl 比 C–H 弱得多） |
| **propagation 1** | Cl• + CH₃CH₃ → CH₃CH₂• + HCl | radical 进攻 alkane，产生新的 radical |
| **propagation 2** | CH₃CH₂• + Cl₂ → CH₃CH₂Cl + Cl• | Cl• 再生 → chain reaction |
| **termination** | Cl• + Cl• → Cl₂；CH₃CH₂• + Cl• → CH₃CH₂Cl；2CH₃CH₂• → C₄H₁₀ | 两个 radical 结合，radical 消失 |

判分要点（多卷一致，例如 9701/21 Oct/Nov 2024、9701/22 May/June 2026）：

- propagation 两步：**第一步产物一定有 HCl**（Cl• 拿走 H），第二步一定**再生 Cl•**；
- radical 的 • 要画在 C / Cl 上；不写 • 不给分；
- termination 写任意一个两 radical 结合的 equation 都可以；
- 换成别的 alkane（propane、C₅H₁₀ 的 cyclopentane）时照抄同一套模板。

这个 reaction **不适合用来制备单一的 halogenoalkane**：chloroethane 里剩下的 H 也会被继续取代（further substitution），得到 1,1-dichloroethane、1,2-dichloroethane … hexachloroethane 的混合物；Cl₂ 越多，多取代产物越多。长链 alkane 的不同位置也都会被取代（propane → 1-chloropropane + 2-chloropropane）。

只用 Cl₂ 和 Br₂：F₂ 太活泼、反应失控；I₂ 的取代整体 endothermic，不发生（讲义）。

<!-- html: free-radical substitution 分步 #frs-mech -->
{{cell frs-mech}}

<!-- md #rx-cracking -->
### D. cracking

**cracking**：把长链（大 *M*ᵣ）的 alkane 断成短链的 alkane 和 alkene。条件：**heat with Al₂O₃**（catalyst；隔绝 O₂，否则会燃烧）。

- 例：C₁₀H₂₂ → C₈H₁₈ + C₂H₄；C₁₂H₂₆ → C₈H₁₈ + 2C₂H₄；产物里**至少有一个 alkene**（H 不够把所有碎片都变成 alkane）。
- 配平：左右 C、H 各自相等；常见题型「补全 equation」只要按 C<sub>n</sub>H<sub>2n+2</sub> / C<sub>n</sub>H<sub>2n</sub> 凑数。
- **为什么有用**：heavier crude oil fractions 产量多、需求少；短链 alkane（petrol 范围）需求大、做 fuel；alkene（ethene、propene）是 polymer 和其他 chemicals 的原料（feedstock）。

{{lo 14.1.4}}

<!-- html: cracking：选一个断点并配平 #cracking -->
{{cell cracking}}

<!-- md #unreactive -->
### E. alkane 为什么不活泼

{{lo 14.1.5}}

mark scheme 的两个得分点（9701/22 Oct/Nov 2025 Q3(b)）：

- **M1 strong C–H bonds**（和 C–C bonds）：要很多能量才能断；
- **M2 non-polar**：C 与 H 的 electronegativity 很接近，C–H 几乎不 polar → 没有 δ+ 的 C 吸引 nucleophile，也没有高 electron density 的区域吸引 electrophile；所以 alkane 不和 polar reagent（acid、alkali、oxidising agent 如 KMnO₄）反应，只和 O₂（燃烧）、Cl₂ / Br₂（UV 下的 radical）反应。

{{rxn-out alkane}}

<!-- md #alkenes -->
## 14.2 Alkenes

### A. alkene 从哪里来

alkene：unsaturated hydrocarbon，含一根 C=C，C<sub>n</sub>H<sub>2n</sub>。C=C = 1 σ + 1 π；π 的 electron density 在分子平面上下方，暴露在外，是 alkene 一切 reaction 的根源。

{{lo 14.2.1}}

{{rxn-in alkene}}

elimination 的 solvent 是关键：**NaOH in ethanol** 得 alkene，**NaOH(aq)** 得 alcohol（{{xref ch15#rx-elimination 15.1 D}} 对比两者）。

<!-- md #rx-alkene-add -->
### B. electrophilic addition（四个 addition reaction）

{{lo 14.2.2}}

所有 addition 都是 **C=C 里的 π bond 断开，两个 C 各连上一个新 atom**（sp² → sp³）：

| (a) | reagent and conditions | ethene 的 product | propene 的 product |
|---|---|---|---|
| (i) **hydrogenation** | H₂(g) and Pt/Ni catalyst and heat | ethane | propane |
| (ii) **steam** | H₂O(g) and H₃PO₄ catalyst | ethanol | **propan-2-ol**（major）+ propan-1-ol |
| (iii) **hydrogen halide** | HX(g), at room temperature | bromoethane | **2-bromopropane**（major）+ 1-bromopropane |
| (iv) **halogen** | X₂ | 1,2-dibromoethane | 1,2-dibromopropane |

- steam 的判分：**M1 steam / H₂O(g)**、**M2 H₃PO₄ (catalyst)**（9701/22 May/June 2026）；写 H₂O(l) 或 dilute acid 不给。
- hydrogenation 用于把 vegetable oil 变成 margarine（unsaturated → 部分 saturated，mp 升高）。
- (b)(c) 的 KMnO₄ 见 C，(d) addition polymerisation 详见 {{xref ch20#rx-polymerisation chapter 20}}。

**aqueous bromine 测 C=C**：加 bromine water（orange）→ 有 C=C 时 **orange → colourless**（decolourised）；alkane 不褪色。（严格说 Br₂(aq) 和 alkene 的主产物是 2-bromoethanol，考试写 1,2-dibromoethane 的 equation 也接受。）

{{lo 14.2.3}}

<!-- html: alkene 反应轮：ethene / propene × reagent #alkene-wheel -->
{{cell alkene-wheel}}

<!-- md #ea-mech -->
### C. electrophilic addition 的 mechanism

{{lo 14.2.4}}

**Br₂ / ethene**（9701/22 Oct/Nov 2024 等）：

1. Br₂ 本身 non-polar；靠近 C=C 时，π electrons 的高 electron density 把 Br–Br 的 bonding pair 推向远端 → **induced dipole**：近端 Br<sup>δ+</sup>、远端 Br<sup>δ−</sup>；
2. curly arrow ① 从 **C=C（π bond）指向 Br<sup>δ+</sup>**；curly arrow ② 从 **Br–Br bond 指向 Br<sup>δ−</sup>**（heterolytic fission，Br⁻ 带走电子对）→ carbocation intermediate ⁺CH₂–CH₂Br + Br⁻；
3. curly arrow ③ 从 **Br⁻ 的 lone pair 指向 C⁺** → BrCH₂CH₂Br。

判分 5 点（累计给分）：pt 1 dipole on Br₂；pt 2 arrow C=C → Br<sup>δ+</sup>；pt 3 arrow Br–Br → Br；pt 4 correct intermediate；pt 5 arrow lone pair on Br⁻ → C⁺。5 点 = 3 分，3–4 点 = 2 分，2 点 = 1 分。

**HBr / propene**：H–Br 本来就 polar（H<sup>δ+</sup>–Br<sup>δ−</sup>），H 是 electrophile：

- M1 curly arrow 从 C=C 指向 H<sup>δ+</sup>；M2 H–Br 的 dipole + 从 H–Br bond 指向 Br 的 curly arrow；M3 正确的 carbocation（**secondary**，CH₃C⁺HCH₃）；M4 Br⁻ 的 lone pair → C⁺。产物 2-bromopropane。

<!-- html: electrophilic addition 分步：Br₂ / ethene 与 HBr / propene #ea-mech-cell -->
{{cell ea-mech}}

<!-- html3d: Br₂ 靠近 π 电子云：induced dipole #br2-pi3d -->
{{cell br2-pi3d}}

<!-- md #markovnikov -->
### D. carbocation 的稳定性与 Markovnikov addition

{{lo 14.2.5}}

HBr 加到不对称的 alkene（propene）上，H 可以加到 C1 或 C2：

| H 加到 | carbocation | 连着几个 alkyl group | 稳定性 | product |
|---|---|---|---|---|
| **C1**（=CH₂ 端，H 多的那个） | CH₃–C⁺H–CH₃（**secondary**） | 2 | 较稳定 → 形成得多 | **2-bromopropane（major）** |
| C2 | ⁺CH₂–CH₂–CH₃（primary） | 1 | 较不稳定 | 1-bromopropane（minor） |

解释（mark scheme 口径）：alkyl group 有 **positive inductive effect**（electron-donating），把电子推向 C⁺，**分散（reduce）正电荷** → carbocation 更稳定。连的 alkyl group 越多越稳定：**tertiary > secondary > primary**。更稳定的 carbocation 更容易形成，它给出的就是 major product。

**Markovnikov 规则**（结果）：H 加到 C=C 上**本来 H 较多**的那个 C，X（或 OH）加到 alkyl group 较多的那个 C。规则是结论，inductive effect 是理由——答「explain」题要写理由。

同样的道理在 {{xref ch15#rx-nucsub 15.1 的 S<sub>N</sub>1}}（tertiary carbocation）和 {{xref ch16#rx-sodium 16.1 alcohol 的 acidity}}（inductive effect 让 alkoxide 更不稳定）里还会用到。

<!-- md #rx-kmno4 -->
### E. 用 KMnO₄ oxidise alkene

| 条件 | 发生什么 | product |
|---|---|---|
| (b) **cold dilute acidified KMnO₄** | 在 C=C 两端各加一个 OH（purple → colourless） | **diol**：ethene → ethane-1,2-diol |
| (c) **hot concentrated acidified KMnO₄** | C=C **完全断开**（rupture），两端各自被 oxidise | 看每个 C=C 碳上连着什么（下表） |

hot concentrated KMnO₄ 时，**C=C 的每一个碳**按它连着的 group 决定产物：

| 这个 C 上连着 | 变成 | 例 |
|---|---|---|
| 两个 H（=CH₂ 端） | **CO₂**（+ H₂O） | 有 CO₂ 冒出 → C=C 在链端 |
| 一个 H + 一个 alkyl | **carboxylic acid**（–COOH） | CH₃CH= → CH₃COOH |
| 两个 alkyl | **ketone** | (CH₃)₂C= → propanone |

用途：由 product 反推 C=C 在长链里的位置。例：pent-2-ene CH₃CH=CHCH₂CH₃ → ethanoic acid + propanoic acid；2-methylbut-2-ene → propanone + ethanoic acid；cyclopentene（ring 里的 C=C）→ 一个 molecule 两端都是 –COOH（pentanedioic acid，9701/21 Oct/Nov 2025）。

<!-- html: hot KMnO₄：正推 product、反推 C=C 的位置 #kmno4-hot -->
{{cell kmno4-hot}}

<!-- md #alkene-out -->
### F. alkene 能变成什么

{{rxn-out alkene}}

<!-- md #practice -->
## Practice

2024–2026 Paper 2 里所有考 chapter 14 的小问，按考试时间排列（含正本在其他章、但这一小问考本章的）。展开 **答案** 对照 mark scheme。

<!-- practice: 9701/22 Feb/Mar 2024 -->
### 9701/22 Feb/Mar 2024

NaBiO₃ is an oxidising agent with similar properties to KMnO₄.
Figure 1.1 shows an example of the use of NaBiO₃ as an oxidising agent: 化合物 **X**（一个连有两个
OH 的叔醇/仲醇二醇结构）与 NaBiO₃ 反应，生成 **Y**（丙-2-酮，CH₃COCH₃）加 **Z**（乙醛，CH₃CHO）。
![Figure 1.1](passyear/extracted/ch02-stoichiometry/img/9701_m24_22_fig1-1.png)

#### Q1(d)(ii) [1]

Compound **X** forms when methylbut-2-ene reacts with KMnO₄.

State the essential conditions for this reaction.

::: answer
**答案** — (KMnO₄ is) cold and dilute

:::

Cl₂ reacts readily with propene to form **K**, 1,2-dichloropropane. **K** can be used to form **L**.
![Fig. 2.1](passyear/extracted/ch09-periodicity/img/9701_m24_22_fig2-1.png)

#### Q2(d)(i) [4]

Complete Fig. 2.2 to show the mechanism for the reaction of Cl₂ with propene in reaction 1.
Include charges, dipoles, lone pairs of electrons and curly arrows, as appropriate.

![Fig. 2.2](passyear/extracted/ch09-periodicity/img/9701_m24_22_fig2-2.png)

::: answer
**答案**（机理图，见 MS 渲染页 `_img/9701_m24_22_msp07.png`）

- 从丙烯 C1=C2 双键画一支弯箭头指向 Cl₂ 中带 δ+ 的 Cl 原子（即新键在 C1，端位 =CH₂ 碳上生成）
- Cl₂ 标出正确偶极（Cl^δ+—Cl^δ−），并从 Cl–Cl 键画一支弯箭头指向带 δ− 的 Cl 原子，使其以 Cl⁻ 离去
- 画出正确的碳正离子中间体：C1 已连上 Cl，C2 带正电荷（仲碳正离子），C3 仍为 CH₃ 支链
- 从 Cl⁻ 上的一对孤对电子画一支弯箭头指向 C2 的碳正离子（C⁺）成键，生成 1,2-dichloropropane

:::

#### Q4(b)(i) [1]

Give the structural formula of Q.

::: answer
**答案** — CH₃CHBrCH₂CH₃

:::

<!-- practice: 9701/21 May/June 2024 -->
### 9701/21 May/June 2024

In electrophilic reactions involving alkenes the π bond of C=C is broken.

#### Q5(c)(ii) [4]

Complete Figure 5.1 to show the mechanism for the electrophilic addition of hydrogen bromide to
2-methylpropene to produce the major organic product. Include charges, dipoles, lone pairs of
electrons and curly arrows, as appropriate.

![Figure 5.1](passyear/extracted/ch03-chemical-bonding/img/9701_s24_21_fig5-1.png)

::: answer
**答案**（机理三步：2-methylpropene + HBr → 叔碳正离子中间体 + Br⁻ → 2-bromo-2-methylpropane）
- M1 curly arrow：从 C=C 双键指向 H–Br 的 H
- M2：H–Br 上标出正确 dipole（Hᵟ⁺—Brᵟ⁻），并有 curly arrow 从 H–Br 键指向 Br
- M3：画出正确的（叔碳）carbocation intermediate，**AND** 最终产物为 2-bromo-2-methylpropane
- M4：curly arrow 从 Br⁻ 的 lone pair 指向中间体的 C⁺（C 上标 +ve 或 δ+ 电荷）

**判分** — 中间体必须是三级碳正离子（(CH₃)₃C⁺），因为 2-methylpropene 加成遵循 Markovnikov 规则。

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

<!-- practice: 9701/21 Oct/Nov 2024 -->
### 9701/21 Oct/Nov 2024

The halogenoalkane CH₃CH₂Cl forms when chlorine reacts with C₂H₆ via a free-radical substitution mechanism.

#### Q2(b)(ii) [1]

State the essential condition for chlorine to react with C₂H₆ at room temperature.

::: answer
**答案** — ultraviolet (light)

:::

#### Q2(b)(iii) [2]

Write two equations to show the propagation steps in this reaction.

::: answer
**答案**
- C₂H₆ + Cl• → C₂H₅• + HCl
- C₂H₅• + Cl₂ → C₂H₅Cl + Cl•

:::

<!-- practice: 9701/22 Oct/Nov 2024 -->
### 9701/22 Oct/Nov 2024

#### Q4(a) [3]

Complete Fig. 4.2 to show the mechanism for the formation of 1,2-dibromoethane in reaction 1.
Include charges, dipoles, lone pairs of electrons and curly arrows as appropriate.

![Figure 4.2](passyear/extracted/ch14-hydrocarbons/img/9701_w24_22_fig4-2.png)

::: answer
**答案**（electrophilic addition 机理，两步）

- **第一步**：Br₂ 上标出偶极 Brδ+—Brδ−；curly arrow① 从 H₂C=CH₂ 的 C=C π 键指向 Brδ+；curly arrow②
  从 Br–Br 键指向另一个 Br，使其带着成键电子对离去，形成 carbocation intermediate
  ⁺CH₂–CH₂Br（+ Br⁻）
- **第二步**：nucleophile Br⁻ 上的 lone pair 发出 curly arrow 指向 carbocation 的 C⁺，生成
  C–Br 键，得到产物 BrCH₂CH₂Br

**判分**（5 个得分点，累计给分）

- pt 1 dipole on Br₂
- pt 2 curly arrow from C=C bond to a Brδ+
- pt 3 curly arrow from Br–Br bond to the other Br
- pt 4 correct intermediate
- pt 5 curly arrow from lone pair on Br⁻ to C⁺
- 5 点 = 3 分。4 点 = 2 分。3 点 = 2 分。2 点 = 1 分。1 点 = 0 分。

:::

<!-- practice: 9701/23 May/June 2025 -->
### 9701/23 May/June 2025

Different hydrocarbon mixtures produced from fractional distillation of crude oil have
different uses.

#### Q3(a)(i) [1]

State the compound that is heated with long-chain hydrocarbons to produce more useful smaller
alkanes and alkenes.

::: answer
**答案** — Al₂O₃ / aluminium oxide

**判分** — 简报原稿把这一小问的官方答案栏标成"空"，但渲染 MS 第 8 页（`msp08`）后可见答案其实
是文字，不是图：catalytic cracking 用的催化剂是 aluminium oxide

:::

C₄H₈ reacts with an excess of H₂ to produce C₄H₁₀.
reaction 1　C₄H₈ + H₂ → C₄H₁₀

#### Q3(b)(i) [1]

Name a catalyst for reaction 1.

::: answer
**答案** — nickel / platinum

:::

W is a colourless liquid.
![Figure 5.1](passyear/extracted/ch14-hydrocarbons/img/9701_s25_23_fig5-1.png)
W = CH₂=C(CH₃)COOH（2-methylprop-2-enoic acid / methacrylic acid）。

#### Q5(a)(ii) [4]

Two different reagents are each added to separate samples of W as shown in Table 5.1. Complete Table 5.1.

**Table 5.1**

| reagent and conditions | observation when reagent is added to W | structural formula of organic product |
|---|---|---|
| solid Na | fizz / bubbles etc **OR** solid Na disappears / dissolves | CH₂=C(CH₃)CO₂Na **OR** CH₂=C(CH₃)CO₂⁻Na⁺ |
| Br₂ in the absence of ultraviolet light | brown to colourless / decolourise | CH₂BrCBr(CH₃)CO₂H |

Na(s) 与 W 的 carboxyl 反应放出 H₂；Br₂ 在暗处（无 UV）对 C=C 做 electrophilic addition，不是 free-radical substitution。


#### Q5(c) [1]

Poly(ethene) is an addition polymer made from ethene. Explain why ethene reacts with electrophiles but poly(ethene) does not.

::: answer
**答案** — ethene 的 π bond 是一个（高）electron density 区域（位于 C–C（σ）bond 的上方和下方）；poly(ethene) 分子中 C–C 全为 single bond，没有这样的富电子 π 区域可供 electrophile 进攻。

:::

<!-- practice: 9701/21 Oct/Nov 2025 -->
### 9701/21 Oct/Nov 2025

Cyclopentane reacts with Cl₂ in the presence of ultraviolet light to form C₅H₉Cl.

#### Q3(c)(i) [1]

The reaction is initiated by the bond fission of Cl₂. State the type of bond fission shown in the
initiation step.

::: answer
**答案** — homolytic

:::

#### Q3(c)(ii) [2]

Complete the equations to show the two propagation steps that follow the initiation step.

propagation 1　C₅H₁₀ + ……… → C₅H₉• + ………
propagation 2　C₅H₉• + ……… → ………

::: answer
**答案**
- M1 C₅H₁₀ + Cl• → C₅H₉• + HCl
- M2 C₅H₉• + Cl₂ → C₅H₉Cl + Cl•

:::

#### Q3(c)(iii) [1]

The final step is shown：C₅H₉• + Cl• → C₅H₉Cl. Give the name for this step in the reaction.

::: answer
**答案** — termination

:::

Fig. 3.2 shows a reaction cycle involving cyclopentane, cyclopentene and C₅H₉Cl.
![Fig. 3.2](passyear/extracted/ch05-chemical-energetics/img/9701_w25_21_fig3-2.png)

#### Q3(d)(i) [1]

Identify a suitable reagent for reaction 3.

::: answer
**答案** — HCl (g)

:::

Cyclopentene, C₅H₈, reacts with hot concentrated acidified KMnO₄ to form compound W,
C₅H₈O₄.

#### Q3(e)(i) [1]

Draw the structure of W.

::: answer
**答案** — W 是 pentanedioic acid：HOOC–CH₂–CH₂–CH₂–COOH（cyclopentene 环上的
C=C 被 hot concentrated acidified KMnO₄ 氧化裂解，两端各生成一个 –COOH，环打开成
直链的 dicarboxylic acid）

:::

<!-- practice: 9701/22 Oct/Nov 2025 -->
### 9701/22 Oct/Nov 2025

#### Q3(b) [2]

Give two reasons to explain the general unreactivity of alkanes.

::: answer
**答案**
- M1 strong C—H (bonds)
- M2 non-polar (C—H / molecule / bonds)

:::

#### Q3(c) [1]

Alkanes with low relative molecular mass, *M*ᵣ, are more useful than those found in heavier crude
oil fractions. Name the process that is used to obtain alkanes with low *M*ᵣ from heavier crude oil
fractions.

::: answer
**答案** — cracking

:::

Hexane can be converted into compounds E and F at high temperature and pressure. Fig. 3.2
shows the reaction scheme involving hexane, E and F.
![Fig. 3.2](passyear/extracted/ch03-chemical-bonding/img/9701_w25_22_fig3-2.png)
（reaction 1：hexane → E，Δ*H*₁ = +215 kJ mol⁻¹；reaction 2：E → F，Δ*H*₂ 待求；
reaction 3：hexane → F，直接反应）

#### Q3(e)(i) [1]

Identify a suitable reagent for reaction 3.

::: answer
**答案** — H₂ ((g)) OR hydrogen (gas)

:::

#### Q3(e)(iii) [1]

Write an equation for the complete combustion of hexane.

::: answer
**答案** — C₆H₁₄ + 9½O₂ → 6CO₂ + 7H₂O

:::

#### Q4(a)(ii) [3]

Complete the mechanism for reaction 1. Construct equations to describe the steps of the
mechanism.

initiation：Cl₂ → 2Cl•

::: answer
**答案**
- propagation 1 — C₃H₈ + Cl• → CH₃CH₂CH₂• + HCl（OR C₃H₈ + Cl• → C₃H₇• + HCl）
- propagation 2 — CH₃CH₂CH₂• + Cl₂ → CH₃CH₂CH₂Cl + Cl•（OR C₃H₇• + Cl₂ → C₃H₇Cl + Cl• 等）
- termination — CH₃CH₂CH₂• + Cl• → CH₃CH₂CH₂Cl（OR C₃H₇• + Cl• → CH₃CH₂CH₂Cl）

:::

<!-- practice: 9701/22 Feb/Mar 2026 -->
### 9701/22 Feb/Mar 2026

2-chlorobutane can be formed by the electrophilic addition of HCl to different isomers of C₄H₈. Compound A is one of these isomers.
![Figure 3.2](passyear/extracted/ch13-organic-intro/img/9701_m26_22_fig3-2.png)
（A 是 *cis*-but-2-ene / (Z)-but-2-ene——从 QP 图上双键两侧的顺式画法可确认）

#### Q3(b)(i) [1]

Draw a structural isomer of A that can also form 2-chlorobutane when it reacts with HCl.

::: answer
**答案** — but-1-ene（CH₂=CH-CH₂-CH₃；与 HCl 按 Markovnikov 加成，H 加到端位 C1，Cl 加到 C2，
同样生成 2-chlorobutane）

:::

Butane, C₄H₁₀, reacts with Cl₂ in the presence of ultraviolet light to form 2-chlorobutane, which has molecular formula C₄H₉Cl.
C₄H₁₀ + Cl₂ → C₄H₉Cl + HCl

#### Q3(c)(i) [1]

Name the mechanism of this reaction.

::: answer
**答案** — (free-)radical substitution

:::

#### Q3(c)(ii) [2]

Complete the reaction scheme given to show the formation of 2-chlorobutane. You may use
molecular formulas in your answer.

initiation　　　Cl₂ → 2Cl•

::: answer
**答案**

- M1 propagation　　Cl• + C₄H₁₀ → C₄H₉• + HCl
- propagation（已给）　　C₄H₉• + Cl₂ → C₄H₉Cl + Cl•
- M2 termination　　C₄H₉• + Cl• → C₄H₉Cl

:::

<!-- practice: 9701/21 May/June 2026 -->
### 9701/21 May/June 2026

#### Q5(b) [1]

In reaction 1, ethene reacts with Cl₂(g) at room temperature. Name the mechanism for reaction 1.

::: answer
**答案** — electrophilic addition

**判分** — 只写 addition 不给分（I addition alone）

:::

#### Q5(d) [4]

Complete Figure 5.2 to show the mechanism for the reaction of ethene with Cl₂ in reaction 1.
Include charges, dipoles, lone pairs of electrons and curly arrows, as appropriate.

![Figure 5.2](passyear/extracted/ch13-organic-intro/img/9701_s26_21_fig5-2.png)

::: answer
**答案** — ethene（对称分子）与 Cl₂ 的 electrophilic addition：
- curly arrow 从 C=C 双键指向离双键较近的那个 Cl 原子
- Cl–Cl 键上标出 dipole：靠近双键的 Cl 为 δ+、远离双键的 Cl 为 δ−；另一条 curly arrow 从
  Cl–Cl 键指向 δ− 的 Cl，使该键异裂生成 Cl⁻
- 生成的 intermediate 是碳正离子：一个碳接 Cl，相邻碳带正电荷 C⁺
- 第三条 curly arrow 从 :Cl⁻ 的 lone pair 指向该 C⁺，生成 1,2-dichloroethane

**判分**
- M1 curly arrow from C=C bond to Cl closest to C=C
- M2 correct dipoles Clδ⁺—Clδ⁻ AND curly arrow from bond of Clδ⁺—Clδ⁻ to Clδ⁻
- M3 correct carbocation intermediate
- M4 curly arrow from lone pair of :Cl⁻ to C⁺ of intermediate
- 曲箭头即使画得偏直也接受，但绝不能是单尖头（fishhook）；M1 的箭头起点只要落在 π 键上、
  终点指向 Cl 或接近 Cl 原子即可；M3 不接受在 C⁺ 上另画 lone pair 或标 + 号在错误位置；
  M4 若 M3 的中间体错误但已 ecf（正电荷位置一致）仍可给分

:::

<!-- practice: 9701/22 May/June 2026 -->
### 9701/22 May/June 2026

P reacts to produce compound Q.
![Figure 6.2](passyear/extracted/ch13-organic-intro/img/9701_s26_22_fig6-2.png)

#### Q6(b)(i) [2]

Identify the reagent and conditions required to convert P to Q.

::: answer
**答案**
- M1 steam / H₂O (g)
- M2 H₃PO₄ (catalyst) / phosphoric(V) acid (catalyst)

**判分**
- M1 A water 且随后给出温度 ≥100 °C（温度写在 conditions 行也算）
- M2 A H₃PO₄ (catalyst) / phosphoric(V) acid (catalyst) / sulfuric acid (catalyst) /
  H₂SO₄ (catalyst) 写在 reagent 行；A orthophosphoric acid / phosphoric acid / sulfuric acid；
  **I** heat under reflux / heat alone；**I** pressure；**I** state symbols

:::

An unlabelled sample contains one of compounds P, R or S.
![Figure 6.4](passyear/extracted/ch13-organic-intro/img/9701_s26_22_fig6-4.png)
The mass spectrum of the sample is shown in Figure 6.5.
![Figure 6.5](passyear/extracted/ch13-organic-intro/img/9701_s26_22_fig6-5.png)

#### Q6(c)(iii) [2]

Suggest one reagent that is used to distinguish between samples of R and S. Include appropriate
observations.

::: answer
**答案**（任选一组）
- M1 Br₂(aq) / bromine water　　M2 orange / brown to colourless in S (not R)
- 或　M1 Na₂CO₃ / sodium carbonate / NaHCO₃ / sodium hydrogencarbonate　　M2 fizzing /
  effervescence in R (not S)

**判分**
- **R** 大小写只扣一次，如 KMNO₄
- M2 的现象必须对应 M1 试剂的明确指认，例：M1 Br₂ → M2 decolourises S ✓；
  M1 K₂Cr₂O₇ / Cr₂O₇²⁻（不加酸）→ M2 (orange) to green ✓；M1 Na₂CO₃ → M2 bubbles in R ✓ 等
- M2 **I** 直接说 alkene for S / carboxylic acid for R，但 A alcohol for S
- M1 A bromine / Br₂；A aqueous iodine / aqueous I₂ / iodine water（不能只写 iodine）；
  **R** iodoform
- M2 A decolourises；A yellow to colourless；**R** red；A bubbles；**I** limewater (turns milky)
- **同样给 2 分的其他试剂**（MS 续页 Alternatives）：
  - acidified potassium dichromate / H⁺ AND K₂Cr₂O₇（BOD H⁺ / Cr₂O₇²⁻）
    → (orange) to green with S (not R)
  - potassium permanganate / KMnO₄（BOD potassium manganate / MnO₄⁻）
    → decolorises / (purple) to colourless (solution) / brown ppt with S (not R)；
    A green solution formed if alkaline KMnO₄ used
  - 加入 named alcohol + (conc) sulfuric acid（或 named alcohol AND catalyst）
    → sweet smell with R (not S)
  - 加入 named carboxylic acid + (conc) sulfuric acid（或 named carboxylic acid AND catalyst）
    → sweet smell with S (and not R)
  - named acid-base indicator → appropriate colour change with R (and not S)
  - A Mg / magnesium → A faster bubbles with R（需要比较）

:::

<!-- md -->
{{lo-checklist}}
