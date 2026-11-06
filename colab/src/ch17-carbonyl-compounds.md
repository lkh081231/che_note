<!-- md #top -->
# Chapter 17 Carbonyl compounds

Cambridge International AS & A Level Chemistry 9701（2025 / 2026 / 2027）· **Organic chemistry**

{{org-nav}}

- 内容边界与 learning outcome 逐字取自 syllabus；判分句式取自 2024–2026 Paper 2 的 mark scheme，引用写卷号（冲突时以 9701/22 May/June 2026 为准）。
- 🔬 / 🧊 / 📝 开头的 cell 是交互图（打开就能用；空白时 **Runtime → Run all**）。蓝色链接跳到别章：新标签页打开后，**左边目录里高亮的那一项就是目标**。

aldehyde 和 ketone 共用一个 functional group：**carbonyl, C=O**。C=O 的 C 是 sp²（trigonal planar，120°），C=O 是 polar 的（C<sup>δ+</sup>=O<sup>δ−</sup>）——这一点决定了本章的 mechanism：**nucleophile 进攻 δ+ 的 C**（对比 alkene 的 C=C 是被 electrophile 进攻）。

<!-- md #carbonyls -->
## 17.1 Aldehydes and ketones

### A. 结构、命名与制备

| | aldehyde | ketone |
|---|---|---|
| C=O 的位置 | 链端：C=O 的 C 连一个 H（–CHO） | 链中间：C=O 的 C 连两个 C |
| suffix | -al（在 C1，不写数字）：ethanal CH₃CHO、propanal CH₃CH₂CHO | -one：propanone CH₃COCH₃、butanone、pentan-3-one |
| 来源 | 1° alcohol 的 oxidation（distillation） | 2° alcohol 的 oxidation |
| 能否再被 oxidise | **能**（→ carboxylic acid） | **不能**（温和条件下） |

{{lo 17.1.1}}

{{rxn-in aldehyde}}

{{rxn-in ketone}}

distillation 为什么能停在 aldehyde、reflux 为什么会得到 acid：见 {{xref ch16#rx-oxidation 16.1 F}}（K₂Cr₂O₇ 试管和装置图都在那里）。

<!-- md #rx-reduction -->
### B. reduction → alcohol

{{lo 17.1.2}}

**(a) reduction**：NaBH₄（warm，aqueous alkaline 或 aqueous ethanol）或 LiAlH₄（**dry ether**，LiAlH₄ 遇水剧烈反应）。

- aldehyde → **primary** alcohol：CH₃CHO + 2[H] → CH₃CH₂OH
- ketone → **secondary** alcohol：CH₃COCH₃ + 2[H] → CH₃CH(OH)CH₃
- 每个 C=O 用 2[H]。NaBH₄ **不还原** C=C、COOH、ester；LiAlH₄ 还能还原 COOH（{{xref ch18#rx-acid-reactions 18.1}}）。多官能团题（chapter 21）常考「哪些基团被还原」。
- 9701 卷的配平题：数清楚 molecule 里有几个 C=O，[H] 的系数 = 2 × C=O 数。

<!-- md #rx-hcn -->
### C. HCN 的 nucleophilic addition → hydroxynitrile

**(b)** aldehyde / ketone + **HCN, KCN as catalyst, and heat** → **hydroxynitrile**（2-hydroxynitrile：OH 和 CN 连在同一个 C 上）。

- ethanal + HCN → CH₃CH(OH)CN，**2-hydroxypropanenitrile**；
- propanone + HCN → (CH₃)₂C(OH)CN，**2-hydroxy-2-methylpropanenitrile**；
- 碳链**多一个 C**（和 {{xref ch15#rx-nucsub KCN + halogenoalkane}} 一样是延长碳链的方法）；hydroxynitrile 再 hydrolyse 得到 hydroxy carboxylic acid（{{xref ch19#rx-nitrile-hydrolysis 19.2 B}}）。
- HCN 剧毒，实际常用 KCN + dilute H₂SO₄ 就地生成；KCN 提供更多 CN⁻（真正的 nucleophile），所以叫 catalyst。

{{lo 17.1.3}}

**mechanism（nucleophilic addition）**：

1. C=O polar：C<sup>δ+</sup>、O<sup>δ−</sup>；
2. curly arrow 从 **:CN⁻ 的 lone pair（在 C 上）指向 C<sup>δ+</sup>**；同时 curly arrow 从 **C=O（π bond）指向 O** → 带负电的 intermediate（O⁻）；
3. curly arrow 从 **O⁻ 的 lone pair 指向 H⁺**（H⁺ 来自 HCN 或水）→ hydroxynitrile（CN⁻ 再生，所以 KCN 是 catalyst）。

判分（9701 卷）：**M1** curly arrow from lone pair on :CN⁻ to C(δ+)；**M2** curly arrow from C=O to O(δ−) **AND** correct dipole；**M3** correct intermediate；**M4** curly arrow from lone pair on O⁻ to H⁺。

C=O 的 C 是 trigonal planar，CN⁻ 从平面上方或下方进攻的机会相等。如果产物的那个 C 连着四个不同 group（ethanal、butanone 都是），就得到等量的两个 enantiomers——**racemic mixture**（没有 optical activity）。chiral centre 见 {{xref ch13#optical 13.4 C}}。propanone 的产物没有 chiral centre（两个 CH₃ 相同）。

<!-- html: nucleophilic addition 分步：HCN + ethanal / propanone #na-mech -->
{{cell na-mech}}

<!-- html3d: 平面 C=O 两面受 CN⁻ 进攻 → racemic mixture #racemic3d -->
{{cell racemic3d}}

<!-- md #rx-tests -->
### D. 鉴别：2,4-DNPH、Tollens'、Fehling's、ease of oxidation、iodoform

{{lo 17.1.4}}

**2,4-DNPH**（2,4-dinitrophenylhydrazine）：加到样品里，aldehyde **和** ketone 都给出 **orange（red / yellow）precipitate**（9701 卷：red / orange / yellow ppt 都接受）。

- 只有 aldehyde 和 ketone 阳性；carboxylic acid、ester 也有 C=O 但**不反应**；
- 这是 condensation reaction（放出 H₂O）；沉淀重结晶后测 melting point，对照数据表可以认出具体是哪个 aldehyde / ketone。

{{lo 17.1.5}}

aldehyde 能被温和的 oxidising agent 氧化，ketone 不能：

| test | 做法 | aldehyde | ketone |
|---|---|---|---|
| **Tollens' reagent** | ammoniacal silver nitrate（[Ag(NH₃)₂]⁺），warm | **silver mirror**（或 grey / black ppt）：Ag⁺ → Ag | no change |
| **Fehling's** solution | alkaline Cu²⁺（blue），warm | blue solution → **red-brown (brick-red) precipitate**：Cu²⁺ → Cu₂O | stays blue |
| **acidified K₂Cr₂O₇**（ease of oxidation） | warm | orange → **green** | stays orange |

Tollens' / Fehling's 是 alkaline，所以 aldehyde 变成 **carboxylate ion RCOO⁻**（不是 RCOOH）。

**推断步骤**（多卷的表格题）：2,4-DNPH 阳性 → 是 carbonyl；再看 Tollens' / Fehling's 或 K₂Cr₂O₇：阳性 → aldehyde，阴性 → ketone。注意 1°、2° alcohol 也让 K₂Cr₂O₇ 变绿，但 2,4-DNPH 阴性。

{{lo 17.1.6}}

**iodoform test**：**alkaline I₂(aq)**，warm → **yellow precipitate of tri-iodomethane, CHI₃**，说明有 **CH₃CO–**（methyl ketone，或 ethanal）；另一个 product 是 **RCO₂⁻**：CH₃COR → CHI₃ + RCO₂⁻。例：propanone → CHI₃ + CH₃CO₂⁻；butanone → CHI₃ + CH₃CH₂CO₂⁻；propanal、pentan-3-one 阴性。同一个 test 也检出 CH₃CH(OH)– alcohol——详细讲解和交互都在 {{xref ch16#rx-iodoform 16.1 I}}。

<!-- html: 未知物鉴定：2,4-DNPH / Tollens' / Fehling's / K₂Cr₂O₇ / 碱性 I₂ #carbonyl-tests -->
{{cell carbonyl-tests}}

<!-- md #carbonyl-out -->
### E. aldehyde / ketone 能变成什么

{{rxn-out aldehyde}}

{{rxn-out ketone}}

<!-- md #practice -->
## Practice

2024–2026 Paper 2 里所有考 chapter 17 的小问，按考试时间排列（含正本在其他章、但这一小问考本章的）。展开 **答案** 对照 mark scheme。

<!-- practice: 9701/22 Feb/Mar 2024 -->
### 9701/22 Feb/Mar 2024

NaBiO₃ is an oxidising agent with similar properties to KMnO₄.
Figure 1.1 shows an example of the use of NaBiO₃ as an oxidising agent: 化合物 **X**（一个连有两个
OH 的叔醇/仲醇二醇结构）与 NaBiO₃ 反应，生成 **Y**（丙-2-酮，CH₃COCH₃）加 **Z**（乙醛，CH₃CHO）。
![Figure 1.1](passyear/extracted/ch02-stoichiometry/img/9701_m24_22_fig1-1.png)

#### Q1(d)(iii) [4]

Complete Table 1.1 to show what is observed when compounds **Y** and **Z** react separately with the
named reagents.

**Table 1.1**

| reagent | observation with Y | observation with Z |
|---|---|---|
| Na₂CO₃(aq) | no reaction | no reaction |
| alkaline I₂(aq) | yellow precipitate (ppt) | yellow ppt |
| 2,4-dinitrophenylhydrazine (2,4-DNPH) | red / orange / yellow ppt | red / orange / yellow ppt |
| Tollens' reagent | no reaction | silver mirror |


#### Q1(d)(iv) [1]

Construct an equation for the reaction of **Z** with NaBH₄. Use [H] to represent an atom of hydrogen
from the reducing agent.

::: answer
**答案** — CH₃CHO + 2[H] → CH₃CH₂OH

:::

<!-- practice: 9701/22 Oct/Nov 2024 -->
### 9701/22 Oct/Nov 2024

Compound E is the only isomer of 1,2-dibromoethane. Alkaline hydrolysis of E gives compound F.
- **E** = CH₃CHBr₂（1,1-dibromoethane）
- **F** = CH₃CHO（ethanal）——E 的两个 Br 同时被 OH 取代生成 gem-diol CH₃CH(OH)₂，不稳定，
  自发脱水成 aldehyde F

#### Q4(d)(iii) [3]

Complete Table 4.1 to state what is observed when F reacts with the reagents listed.

Table 4.1

| reagent | observation with F |
|---|---|
| 2,4-dinitrophenylhydrazine (2,4-DNPH reagent) | red / orange / yellow ppt |
| Tollens' reagent | silver mirror OR grey ppt OR black ppt |
| alkaline I₂(aq) | yellow ppt |


<!-- practice: 9701/22 Feb/Mar 2025 -->
### 9701/22 Feb/Mar 2025

#### Q4(a) [5]

Table 4.1 gives details of tests on J to M. In each test, only two compounds give a positive
result. Complete Table 4.1.

| reagent | observation of positive result | compounds that give a positive result |
|---|---|---|
| acidified K₂Cr₂O₇(aq) | *(空)* | J and L |
| alkaline I₂(aq) | yellow precipitate | *(空)* |
| *(空)* | orange precipitate | J and K |
| Na(s) | *(空)* | *(空)* |

::: answer
**答案** — 完整表格：

| reagent | observation of positive result | compounds that give a positive result |
|---|---|---|
| acidified K₂Cr₂O₇(aq) | (solution) turns (from orange to) green | J and L |
| alkaline I₂(aq) | yellow precipitate (forms) | K and L |
| 2,4-dinitrophenylhydrazine / 2,4-DNPH | orange precipitate (forms) | J and K |
| Na(s) | effervescence | L and M |

**判分** — 5 个空各 1 分：K₂Cr₂O₇ 一行的 observation、I₂ 一行的 compounds、reagent 一行填
2,4-DNPH、Na(s) 一行的 observation 与 compounds

:::

K reacts with HCN in the presence of a KCN catalyst, forming N.

#### Q4(b)(i) [4]

Complete Fig. 4.2 to show the mechanism for this reaction. Include charges, dipoles, lone pairs
of electrons and curly arrows, as appropriate.

![Figure 4.2](passyear/extracted/ch16-hydroxy-compounds/img/9701_m25_22_fig4-2.png)

::: answer
**答案**（nucleophilic addition of HCN 到 butan-2-one 的羰基碳，生成 N =
2-hydroxy-2-methylbutanenitrile）
- M1 curly arrow from lone pair on :CN⁻ to C(δ+)
- M2 curly arrow from C=O to O(δ–) **AND** correct dipole
- M3 correct intermediate
- M4 curly arrow from lone pair on O:⁻ to H⁺

:::

#### Q4(b)(ii) [1]

Identify the class of compound of which N is a member.

::: answer
**答案** — hydroxynitrile

:::

<!-- practice: 9701/21 May/June 2026 -->
### 9701/21 May/June 2026

Compound A is a structural isomer of Z.
![Figure 4.2](passyear/extracted/ch16-hydroxy-compounds/img/9701_s26_21_fig4-2.png)
A 的结构（渲染页逐键核对后确认为 5 个碳）：HOCH₂CH₂–CH(OH)–CH(OH)–CH₂OH（pentane-1,2,3,5-tetraol）。

#### Q4(b)(i) [2]

Complete Table 4.1 to show what is observed when separate samples of A are added to each reagent. State 'none' if no reaction occurs.

**Table 4.1**

| reagent | observation with A |
|---|---|
| Na(s) | effervescence / fizzing / bubbling |
| 2,4-dinitrophenylhydrazine (2,4-DNPH) | none |
| Fehling's reagent | none |

::: answer
**判分** — Na(s) 一行：I 只写「产生气体」不写现象；I 气体名称/检验气体的方法；I 固体消失/变无色溶液。Fehling's 一行：A（仍为）orange 溶液/无沉淀/无反应/无现象；I 写成"变橙色"

:::

#### Q4(b)(ii) [1]

Suggest why Fehling's reagent does not react with A but does react with aldehyde functional groups.

::: answer
**答案** — Alcohols / Compound A are not oxidised by Fehling's reagent（aldehydes are oxidised by Fehling's reagent）

**判分** — A alcohol groups = hydroxy = hydroxyl = OH group；R hydroxide/OH⁻ 表述算 alcohol group；A "Fehling's 对 alcohol 而言不是足够强的 oxidising agent"／"Fehling's 对 aldehyde 而言是足够强的 oxidising agent"；I "Fehling's 是温和氧化剂"（不加限定）；R ketone 也被 Fehling's 氧化

:::

#### Q4(c) [2]

Compound B reacts with an excess of LiAlH₄ to produce organic compound C.

![Figure 4.3](passyear/extracted/ch16-hydroxy-compounds/img/9701_s26_21_fig4-3.png)

Complete the equation in Figure 4.3 to show the reaction of B with an excess of LiAlH₄ to produce C. [H] represents one atom of hydrogen from the reducing agent, LiAlH₄.

B 的结构（渲染页逐键核对）：CH₃–CO–CH₂–CO–C(OH)(CH₃)–COOH（7 个碳：2 个 ketone + 1 个 tertiary alcohol + 1 个 carboxylic acid）。

::: answer
**答案** — 过量 LiAlH₄ 把 COOH 还原成 CH₂OH（耗 4[H]，副产物 H₂O），把 2 个 ketone 分别还原成 CH(OH)（各耗 2[H]），tertiary alcohol 不受影响：

C = HOCH₂–C(OH)(CH₃)–CH(OH)–CH₂–CH(OH)–CH₃（共 8 个 [H]）

B + 8[H] → C + H₂O

**判分** — M1 A C 的任何无歧义结构；M2 按该结构配平的化学计量数；A ecf：若结构错但仍正确配平，且结构含 7 个碳，同样给分

:::

<!-- practice: 9701/22 May/June 2026 -->
### 9701/22 May/June 2026

#### Q4(c)(ii) [2]

Each molecule of W contains four hydroxyl groups. Only two of these are primary hydroxyl groups. Table 4.1 shows the observations when separate samples of Z are added to each reagent. Use the information in 4(c) to suggest the structure of W.

**Table 4.1**（题目给出，非填空）

| reagent | observations with Z |
|---|---|
| 2,4-dinitrophenylhydrazine (2,4-DNPH) | orange precipitate |
| Fehling's reagent | none |

Z 对 2,4-DNPH 有反应（含 C=O）但对 Fehling's 无反应（不是 aldehyde，是 ketone）——说明 W 的 4 个 hydroxyl 里，2 个 primary 被完全氧化成 carboxylic acid（COOH），1 个 secondary 被氧化成 ketone（C=O），1 个 tertiary 氧化不了、原样保留。按此推出 W = HOCH₂–CH(OH)–C(OH)(CH₃)–CH₂OH 时，Z = HOOC–CO–C(OH)(CH₃)–COOH，分子式 C₅H₆O₆，与 (c)(i) 配平方程里的 C₅H₆O₆ 完全对上，交叉验证成立。

::: answer
**答案** — W = HOCH₂CH(OH)C(OH)(CH₃)CH₂OH （**OR** (HOCH₂)₂C(OH)(CHOHCH₃)）：2 个 primary alcohol（两端 CH₂OH）、1 个 secondary alcohol（CH(OH)）、1 个 tertiary alcohol（C(OH)(CH₃)）

**判分** — A 任何无歧义结构；I 尝试命名；Max 1：全部基团正确但有 1 处或以上 connectivity 错误（如写成 C−H−O）

:::

<!-- practice: 9701/23 May/June 2026 -->
### 9701/23 May/June 2026

#### Q4(a)(ii) [2]

Complete Table 4.2 to show what is observed when separate samples of V are added to each reagent. State 'none' if no reaction occurs.

**Table 4.2**

| reagent | observation with V |
|---|---|
| Na(s) | effervescence / fizzing / bubbling |
| 2,4-dinitrophenylhydrazine (2,4-DNPH) | none |
| Fehling's reagent | none |

::: answer
**判分** — Na(s) 一行：I 只写「产生气体」不写现象／写气体名称／写检验方法／固体消失或变无色溶液；2,4-DNPH 一行：A（仍为）orange 溶液/无沉淀/无反应/无现象；I 写成"变橙色"

:::

#### Q4(a)(iii) [1]

Suggest why Fehling's reagent does not react with V but does react with aldehyde functional groups.

::: answer
**答案** — Alcohols / Compound V are not oxidised by Fehling's reagent（aldehydes are oxidised by Fehling's reagent）

**判分** — A alcohol groups = hydroxy = hydroxyl = OH group；R hydroxide/OH⁻ 表述算 alcohol group；A "Fehling's 对 alcohol 不是足够强的 oxidising agent"／"Fehling's 对 aldehyde 是足够强的 oxidising agent"；I "Fehling's 是温和氧化剂"（不加限定）；R ketone 也被 Fehling's 氧化

:::

<!-- md -->
{{lo-checklist}}
