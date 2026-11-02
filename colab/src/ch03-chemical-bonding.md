<!-- md -->
# Chapter 3 Chemical bonding

Cambridge International AS & A Level Chemistry 9701（2025 / 2026 / 2027）· **Physical chemistry**

- 内容边界与 learning outcome 逐字取自 syllabus；bond energy 取自 data booklet；Pauling electronegativity 用讲义的表（考试会给数值）；判分句式取自 2024–2026 Paper 2 的 mark scheme，引用写卷号。
- 🔬 / 🧊 / 📝 开头的 cell 是交互图（已经预先渲染好，打开就能用）。如果显示空白：**Runtime → Run all**（连本地运行时即可，几秒跑完）。
- 🧊 3D 图需要联网加载 three.js；拖动旋转、滚轮缩放。离线时会退回一张静态图。

本章的地图：

| 类别 | 是什么之间的作用 | 本章小节 |
|---|---|---|
| ionic bonding | cations 与 anions | 3.2 |
| metallic bonding | positive metal ions 与 delocalised electrons | 3.3 |
| covalent / coordinate bonding | 两个 nuclei 与 shared pair of electrons | 3.4、3.5、3.7 |
| intermolecular forces（van der Waals' forces） | molecules 之间：id-id、pd-pd、hydrogen bonding | 3.6 |

前三种是 **bond**（原子 / 离子之间），最后一种是 **molecules 之间**的作用力，弱得多（3.6 D）。giant structure 与物理性质（melting point、conductivity）属于 chapter 4。

<!-- md -->
## 3.1 Electronegativity and bonding

### A. 定义

**electronegativity**：the power of an atom to attract electrons to itself。

更具体地说，是 atom 把 **covalent bond 里的 bonding pair** 拉向自己的能力。数值越大，拉得越狠。最常用的是 **Pauling scale**（没有单位）。

{{lo 3.1.1}}

### B. 影响 electronegativity 的三个因素

bonding pair 受到的是 nucleus 的吸引，所以凡是影响「nucleus 对外层 electrons 吸引力」的都算：

| 因素 | 怎样影响 | electronegativity |
|---|---|---|
| **nuclear charge**（proton 数） | 越大，对 bonding pair 吸引越强 | 越大 ↑ |
| **atomic radius** | 越大，bonding pair 离 nucleus 越远，吸引越弱 | 越小 ↓ |
| **shielding** by inner shells and sub-shells | 内层 electrons 越多，挡掉越多 nuclear charge | 越小 ↓ |

{{lo 3.1.2}}

### C. 周期表上的趋势

- **across a period（左 → 右）增大**：nuclear charge 增大，而 electrons 加在同一个 shell 里，shielding 差不多；所以 atomic radius 变小，nucleus 对 bonding pair 的吸引变强。
- **down a group（上 → 下）减小**：多了 inner shells，atomic radius 增大、shielding 增大，这两点胜过（outweigh）nuclear charge 的增加，吸引变弱。
- 所以右上角最大：**fluorine is the most electronegative element**（4.0）。最 electronegative 的几个：**F > O > N > Cl > Br**。
- noble gases 一般不形成 bond，表里没有值。

| Group | 1 | 2 | 13 | 14 | 15 | 16 | 17 |
|---|---|---|---|---|---|---|---|
| Period 2 | Li 1.0 | Be 1.5 | B 2.0 | C 2.5 | N 3.0 | O 3.5 | F 4.0 |
| Period 3 | Na 0.9 | Mg 1.2 | Al 1.5 | Si 1.8 | P 2.1 | S 2.5 | Cl 3.0 |
| Period 4 | K 0.8 | Ca 1.0 | Ga 1.6 | Ge 1.8 | As 2.0 | Se 2.4 | Br 2.8 |

H = 2.1，I = 2.5。（讲义的 Pauling 值；不同教科书小数位略有出入，考试用题目给的值。）

{{lo 3.1.3}}

### D. 用 electronegativity difference 预测 bond 的类型

两种 atom 的 electronegativity 差（ΔEN）越大，bonding pair 越偏向一边；差到一定程度，electron 就整个转移过去，形成 ions。讲义的判据：

| ΔEN | bond | 例 |
|---|---|---|
| 0 | non-polar covalent（no ionic character） | Cl–Cl：3.0 − 3.0 = 0 |
| below 1.0 | covalent（ΔEN 越大越 polar，见 3.6 A） | C–H：2.5 − 2.1 = 0.4 |
| 介于两者之间 | 有 ionic character 的 covalent bond / 有 covalent character 的 ionic bond | **不考**（syllabus 写明 will not be assessed） |
| 2.0 or more | ionic | Na–Cl：3.0 − 0.9 = 2.1 |

- 一般规律：metal + non-metal → ionic；non-metal + non-metal → covalent。ΔEN 是这条规律的定量版本。
- AlCl₃：ΔEN = 3.0 − 1.5 = 1.5，比 2.0 小——所以 AlCl₃ 是 covalent molecule（见 3.4 C 的 Al₂Cl₆），这是「metal + non-metal 不一定 ionic」的经典例子。

{{lo 3.1.4}}

<!-- html: ΔEN → bond type -->
{{cell en-bond}}

<!-- md -->
## 3.2 Ionic bonding

**ionic bonding**：the electrostatic attraction between oppositely charged ions（positively charged **cations** 和 negatively charged **anions**）。

- metal atom 失去外层 electrons → cation；non-metal atom 得到 electrons → anion。两者通常都达到 **noble-gas configuration**（外层 8 个，octet）。
- ion 的 charge = 失去 / 得到的 electron 数。
- 在 crystal 里，ions 排成规则重复的 **lattice**，每个 ion 被许多带相反电荷的 ions 包围，吸引作用指向所有方向，所以 ionic bonding 很强。

{{lo 3.2.1}}

syllabus 点名的三个例子：

| compound | electron transfer | ions 的 electronic configuration |
|---|---|---|
| sodium chloride, NaCl | Na（2,8,1）把 1 个 electron 给 Cl（2,8,7） | Na⁺ 1s²2s²2p⁶（= Ne）；Cl⁻ 1s²2s²2p⁶3s²3p⁶（= Ar） |
| magnesium oxide, MgO | Mg（2,8,2）把 2 个 electrons 给 O（2,6） | Mg²⁺ 和 O²⁻ 都是 1s²2s²2p⁶ |
| calcium fluoride, CaF₂ | Ca（2,8,8,2）各给 1 个 electron 给 **两个** F（2,7） | Ca²⁺ 1s²2s²2p⁶3s²3p⁶；每个 F⁻ 1s²2s²2p⁶ |

MgO 的 ions 带 2+ / 2−，比 NaCl 的 1+ / 1− 吸引强得多，所以 MgO 的 melting point 高得多（2852 °C vs 801 °C）。

ionic compound 的 dot-and-cross diagram 规则（交互件在 3.7）：

- 每个 ion 画 **square brackets**，charge 写在右上角；同一种 ion 有两个时，可以画两次，也可以在括号外写系数（2[Li]⁺）。
- 默认只画 **outer shell**。cation 失去了整个外层，括号里就是空的（或画出它新的、满的外层 8 个）。
- 转移过去的 electron 用另一种符号（× 对 •），一眼看出来自哪个 atom。
- 题目写「the arrangement of **all** the electrons」时，每个 shell 都要画（9701/22 May/June 2026 Q1(b) 的 Li₂O）。

{{lo 3.2.2}}

<!-- md -->
## 3.3 Metallic bonding

**metallic bonding**：the electrostatic attraction between positive metal ions and delocalised electrons。

- metal atoms 在 lattice 里紧密、规则地排列；每个 atom 把外层 electrons 放出来，自己变成 **positive ion**。
- 放出来的 electrons **delocalised**：不属于任何一个 atom 或 bond，可以在整个 lattice 里自由移动（"sea of electrons"）。
- 吸引作用指向所有方向。

**画 metallic bonding 的图**（9701/22 Feb/Mar 2024 Q1(a)、9701/22 May/June 2024 Q1(c)）：规则排列的 + 号圆圈（至少 2 × 2），圆圈之间散布 − 号；两个必须的得分点 ① **regular arrangement of positive ions** ② **surrounded by (sea of) delocalised electrons**，并各引一条标注线写上这两个名字。

metallic bonding 的强度随以下增大而增强：

- ion 的 positive charge 越大（每个 atom 贡献的 delocalised electrons 越多）；
- metal ion 越小。

| | Na | Mg | Al | | Li | Na | K |
|---|---|---|---|---|---|---|---|
| ion | Na⁺ | Mg²⁺ | Al³⁺ | | Li⁺ | Na⁺ | K⁺ |
| melting point / °C | 98 | 650 | 660 | | 181 | 98 | 63 |
| 趋势 | across Period 3：charge ↑、ion 变小 → 增强 | | | | down Group 1：ion 变大 → 减弱 | | |

delocalised electrons 能移动，所以 metal 能导电（ch4 细讲）：「delocalised electrons move (through the structure)」（9701/21 May/June 2025 Q1(a)(ii)）。

{{lo 3.3.1}}

<!-- html: metallic bonding -->
{{cell metallic}}

<!-- md -->
## 3.4 Covalent bonding and coordinate (dative covalent) bonding

### A. Covalent bond

**covalent bond**：electrostatic attraction between the nuclei of two atoms and a shared pair of electrons。

mark scheme 的说法：「(electrostatic) attraction between nuclei of two atoms and shared pair of electrons」（9701/21 May/June 2024 Q5(a)）——**nuclei**（两个 nucleus）和 **shared pair** 两个词都不能少。

- 两个 non-metal atoms 各出 electron 组成 pair 共用，通常各自达到 octet（H 是 2）。
- **lone pair**：外层里**没有**用于 bonding 的 electron pair。
- 共用 1 对 = single bond；2 对 = **double bond**；3 对 = **triple bond**。

| molecule | bonds | central atom 上的 lone pairs | 记住 |
|---|---|---|---|
| H₂ | H–H | — | H 只要 2 个 electron |
| Cl₂ | Cl–Cl | 每个 Cl 3 对 | |
| HCl | H–Cl | Cl 3 对 | |
| O₂ | O=O | 每个 O 2 对 | double bond |
| N₂ | N≡N | 每个 N 1 对 | triple bond |
| CO₂ | O=C=O | C 没有；每个 O 2 对 | 两个 double bond |
| NH₃ | 3 × N–H | N 1 对 | |
| CH₄ | 4 × C–H | 0 | |
| C₂H₆ | C–C + 6 × C–H | 0 | |
| C₂H₄ | C=C + 4 × C–H | 0 | |

### B. 不满足 octet 的情况

- **electron deficient**（外层少于 8）：Group 13。BF₃ 的 B 外层只有 6 个；AlCl₃ 的 Al 也是 6 个。
- **expanded octet**（外层多于 8）：只有 **Period 3 及以后**的 element 才行——它们的 *n* = 3 shell 有空的 3d orbitals 可以容纳多出来的 electrons；Period 2（N、O、F）没有 2d，最多 8 个。

| molecule | central atom 外层 electron 数 | 结构 |
|---|---|---|
| SO₂ | 10 | O=S=O，S 上还有 1 个 lone pair |
| PCl₅ | 10 | 5 个 P–Cl |
| SF₆ | 12 | 6 个 S–F |

- 也有 odd number of electrons 的 molecule：NO 有 11 个 outer electrons，N 上有一个 **unpaired electron**——这种 molecule 叫 **(free) radical**（9701/22 Feb/Mar 2026 Q2(a)(i)）。

### C. Coordinate (dative covalent) bond

**coordinate bond**：shared pair 的两个 electrons **都来自同一个 atom**。条件：

1. 一个 atom 有 **lone pair**；
2. 另一个 atom 有空的 orbital 来接收它（electron deficient）。

一旦形成，coordinate bond 和普通 covalent bond 完全一样（NH₄⁺ 的 4 个 N–H 没有区别）。结构式里用 **箭头 →** 表示，箭头从提供 lone pair 的 atom 指向接收的 atom。

- **NH₄⁺**：NH₃(g) + HCl(g) → NH₄Cl(s)。HCl 把 H⁺ 交给 NH₃，N 的 lone pair 和 H⁺ 形成 N→H。
- NH₄Cl 里三种 bond 都有（9701/23 May/June 2024 Q4(a)）：NH₄⁺ 与 Cl⁻ 之间是 **ionic**；4 个 N–H 中 3 个是 **covalent**、1 个是 **coordinate**。M1 = NH₄⁺ AND Cl⁻ AND 4 个 N–H 共用 pair；M2 = 其中一个画成方向正确的箭头（或那一对只用一种符号）。
- **Al₂Cl₆**：低温下两个 AlCl₃ 结合成 dimer。每个 AlCl₃ 的 Al 只有 6 个外层 electrons，另一个分子上的 Cl 用 lone pair 填进去，形成两个 Cl→Al。每个 Al 周围变成 4 对、tetrahedral。
- 同理：BF₃ + NH₃ → F₃B←NH₃（N 的 lone pair 进入 B 的空 orbital）。

{{lo 3.4.1}}

<!-- md -->
### D. σ bond 与 π bond

covalent bond 的本质是两个 atomic orbitals **overlap**，overlap 的区域里放 shared pair。overlap 的方式有两种：

| | σ bond | π bond |
|---|---|---|
| 怎么 overlap | **direct**（end-on / head-on）overlap，沿两个 nuclei 的连线 | **sideways** overlap of adjacent p orbitals |
| electron density 在哪 | 两个 nuclei 之间、连线上 | σ bond 的**上方和下方**（两团，合起来是一个 bond、2 个 electrons） |
| 能用的 orbitals | s–s、s–p、p–p、hybrid orbitals | 只有 p–p |
| 强弱 | 较强 | 较弱 |

- single bond = 1σ；double bond = 1σ + 1π；triple bond = 1σ + 2π（两个 π 互相垂直）。
- **为什么 π bond 先断**（electrophilic addition，9701/21 May/June 2024 Q5(c)(i)）：(pair of) electrons in π bond are **further away from the nuclei** so **weaker attraction**（或反过来说 σ 的 electrons closer to the two nuclei so stronger attraction）。
- 考试画 overlap 图时，画什么 orbital 要看 element：H 是 s-block，画**球形 s orbital**；C、Cl 这类 p-block element 形成 σ bond 时，画一个「一大一小」的 modified p orbital（大的那瓣朝向对方）。
- N₂ 的表（9701/23 May/June 2024 Q1(a)(ii)）：σ 1 个 / π 2 个；σ 是 **direct** overlap，π 是 **sideways** overlap of adjacent p orbitals。

| molecule | σ | π | overlap |
|---|---|---|---|
| H₂ | 1 | 0 | s–s |
| C₂H₆ | 7 | 0 | C–C：sp³–sp³；C–H：sp³–s |
| C₂H₄ | 5 | 1 | C=C：sp²–sp² 的 σ + p–p 的 π；C–H：sp²–s |
| HCN | 2 | 2 | H–C：s–sp；C≡N：1σ + 2π |
| N₂ | 1 | 2 | N≡N：1σ + 2π |

数 σ / π：**每一条线（不管单、双、三）都有且只有 1 个 σ**，多出来的才是 π。例：CH₂=C(CH₃)COOCH₃ 有 14 σ、2 π（9701/23 May/June 2025 Q5(b)(i)）。

<!-- html3d: σ 与 π overlap -->
{{cell sigma-pi}}

<!-- md -->
### E. Hybridisation：sp、sp²、sp³

C 的 ground state 是 2s²2p²，只有 2 个 unpaired electron，却能形成 4 个**完全一样**的 C–H（CH₄）。解释：bonding 时 2s 和 2p orbitals **混合（hybridise）**，变成一组能量、形状相同的 **hybrid orbitals**。混了几个就得到几个。

| hybridisation | 混合 | hybrid orbitals | 夹角 | 剩下没混的 p | 例 |
|---|---|---|---|---|---|
| sp³ | 1 s + 3 p | 4 个 sp³ | 109.5°（tetrahedral） | 0 | CH₄、C₂H₆；NH₃、H₂O 的 N / O 也是 sp³（lone pair 占一个 hybrid orbital） |
| sp² | 1 s + 2 p | 3 个 sp² | 120°（同一平面） | 1 个 p，垂直于平面 → 形成 π | C₂H₄（每个 C）、C=O 的 C |
| sp | 1 s + 1 p | 2 个 sp | 180° | 2 个 p，互相垂直 → 形成 2 个 π | C₂H₂、HCN 的 C |

- hybrid orbital 长得像「一大一小」两瓣，大瓣朝向要成键的 atom；它们只用来形成 **σ bond**（或放 lone pair），π bond 永远来自没 hybridise 的 p orbital。
- 判断方法：数 C 周围有几个 **electron-pair 区域**（σ bonds + lone pairs）：4 → sp³，3 → sp²，2 → sp。C=C 里的 C：3 个 σ（1 个 C–C + 2 个 C–H）→ **sp²**（9701/21 May/June 2024 Q5(b)(i)）。
- 同一个分子里可以混着有：propene CH₂=CH–CH₃ 的 C1、C2 是 sp²（C1–C2–C3 在一个平面上、120°），C3 是 sp³（109.5°）。

<!-- html3d: sp / sp² / sp³ hybrid orbitals -->
{{cell hybrid}}

<!-- md -->
{{lo 3.4.2}}

### F. Bond energy 与 bond length

- **bond energy**：the energy required to break one mole of a particular covalent bond in the gaseous state（单位 kJ mol⁻¹）。
- **bond length**：the internuclear distance of two covalently bonded atoms。
- 两个 atoms 越靠近，bonding pair 同时被两个 nuclei 吸引得越强；但太近时两个 nuclei、以及非成键 electrons 之间的 repulsion 急剧增大——所以存在一个最稳定的距离，就是 bond length。

data booklet 的值（kJ mol⁻¹；bond length 是教科书值，nm）：

| bond | bond energy | bond length | | bond | bond energy | bond length |
|---|---|---|---|---|---|---|
| C–C | 350 | 0.154 | | H–F | 562 | 0.092 |
| C=C | 610 | 0.134 | | H–Cl | 431 | 0.127 |
| C≡C | 840 | 0.120 | | H–Br | 366 | 0.141 |
| N≡N | 944 | 0.110 | | H–I | 299 | 0.161 |
| O=O | 496 | 0.121 | | Cl–Cl | 242 | 0.199 |
| C–H | 410 | 0.109 | | Br–Br | 193 | 0.228 |
| O–H | 460 | 0.096 | | I–I | 151 | 0.267 |

规律：

1. **multiple bond 更短、更强**：C=C 比 C–C 多了 electrons 在两个 nuclei 之间，把 atoms 拉得更近、更难拉开。（C=C 的 610 < 2 × 350：π bond 比 σ bond 弱。）
2. **atom 越大，bond 越长、越弱**：H–F > H–Cl > H–Br > H–I；Cl–Cl > Br–Br > I–I。atom 大 → bonding pair 离 nuclei 远 → 吸引弱。
3. **F–F 是例外**：F–F（158）比 Cl–Cl（242）弱。F–F 太短，两个 F 上各 3 对 lone pairs 靠得太近，repulsion 很大，削弱了 bond。H–F 没有这个问题（H 上没有 lone pair）。

**bond energy 与 reactivity**：反应要先断 bond，bond 越强越不容易反应。

- N₂ 很不活泼：「strong triple (covalent) bond」**AND**「non-polar」两点（9701/23 May/June 2024 Q1(a)(i)）。O₂（O=O 496）比 N₂（944）活泼得多。
- H–X 的热稳定性 HF > HCl > HBr > HI（hot glass rod 能分解 HI，不能分解 HCl），因为 bond energy 依次减小（chapter 11）。
- bond energy 只是因素之一：**bond polarity** 和 **σ / π** 同样重要。C–Cl（340）比 C–C（350）弱不了多少，但 chloroethane 比 ethane 活泼得多——polar C–Cl 的 Cᵟ⁺ 会被 OH⁻ 这类 nucleophile 进攻（chapter 15）；alkene 比 alkane 活泼是因为 π bond 弱、electron density 暴露在外。

{{lo 3.4.3}}

<!-- html: bond energy 与 bond length -->
{{cell bond-energy}}

<!-- md -->
## 3.5 Shapes of molecules

### A. VSEPR theory

**VSEPR**（valence shell electron pair repulsion）：

1. central atom 外层的 electron pairs（bonding pairs + lone pairs）都带负电，**互相排斥**；
2. 它们在空间里尽量**远离**，使 repulsion 最小——这决定了 molecule 的形状；
3. **lone pair 比 bonding pair 排斥得更厉害**（lone pair 只被一个 nucleus 拉着，离 central atom 更近、更"胖"）：

   **lone pair–lone pair > lone pair–bond pair > bond pair–bond pair**

4. double / triple bond 在决定形状时**算一个区域**（和 single bond 一样）。

**shape 只看 atoms 的位置**：lone pairs 影响形状，但不出现在 shape 的名字里。NH₃ 的 4 对 electron pairs 是 tetrahedral 排布，但 shape 叫 **pyramidal**。

syllabus 点名的 7 个（必须背 shape + bond angle）：

| molecule | bonding pairs | lone pairs | shape | bond angle |
|---|---|---|---|---|
| CO₂ | 2（两个 double bond） | 0 | linear | 180° |
| BF₃ | 3 | 0 | trigonal planar | 120° |
| CH₄ | 4 | 0 | tetrahedral | 109.5° |
| NH₃ | 3 | 1 | pyramidal | 107° |
| H₂O | 2 | 2 | non-linear | 104.5° |
| PF₅ | 5 | 0 | trigonal bipyramidal | 120° and 90° |
| SF₆ | 6 | 0 | octahedral | 90° |

**每多一个 lone pair，bond angle 减小约 2.5°**：CH₄ 109.5° → NH₃ 107° → H₂O 104.5°。解释的标准写法（9701/21 May/June 2026 Q1(c)(i)，SCl₂ 的 bond angle）：

- M1 **104.5°**（接受 103–105°）
- M2 **2 bonding pairs and 2 lone pairs**（of electrons）
- M3 **lone pairs repel more than bonding pairs**（或 lp–lp > lp–bp > bp–bp）

写成「2 bonding pairs + 1 lone pair」且角度 107–109° 最多 1 分；写「2 S–Cl bonds」代替 bonding pairs 不给 M2。

{{lo 3.5.1}}

<!-- html3d: VSEPR shapes -->
{{cell vsepr}}

<!-- md -->
### B. 预测没见过的 molecule / ion

步骤（3.5.2 的 "analogous"：找一个形状一样的已知例子）：

1. 找 central atom，数它的 **outer electrons**（= group number 的个位：N 5、S 6、Cl 7、Xe 8）；
2. ion：**负电荷加** electrons，**正电荷减** electrons；
3. 每个 single bond 用掉 central atom 1 个 electron，每个 double bond（通常连 O）用掉 2 个；
4. 剩下的 electrons ÷ 2 = **lone pairs**；
5. electron-pair 区域数 = 成键的 atom 数 + lone pairs → 排布 → shape → bond angle。

| species | 算 | bp | lp | shape | angle | 类比 |
|---|---|---|---|---|---|---|
| NH₄⁺ | N：5 − 1 = 4，4 个 N–H 用掉 4 | 4 | 0 | tetrahedral | 109.5° | CH₄ |
| H₃O⁺ | O：6 − 1 = 5，用掉 3，剩 2 | 3 | 1 | pyramidal | 107° | NH₃ |
| NH₂⁻ | N：5 + 1 = 6，用掉 2，剩 4 | 2 | 2 | non-linear | 104.5° | H₂O |
| SCl₂ | S：6，用掉 2，剩 4 | 2 | 2 | non-linear | 104.5°（MS 接受 103–105°） | H₂O |
| PCl₃ | P：5，用掉 3，剩 2 | 3 | 1 | pyramidal | 107° | NH₃ |
| SiH₄ / CCl₄ | 4，用掉 4 | 4 | 0 | tetrahedral | 109.5° | CH₄ |
| BeCl₂ / CS₂ | 用完 | 2 | 0 | linear | 180° | CO₂ |
| SO₂ | S：6，两个 S=O 用掉 4，剩 2 | 2 | 1 | non-linear（bent） | 约 118°（略小于 120°） | — |
| PCl₄⁺ | P：5 − 1 = 4，用掉 4 | 4 | 0 | tetrahedral | 109.5° | CH₄ |
| PCl₆⁻ | P：5 + 1 = 6，用掉 6 | 6 | 0 | octahedral | 90° | SF₆ |
| XeF₄ | Xe：8，用掉 4，剩 4 | 4 | 2 | square planar | 90° | — |

PCl₅ 在 gas phase 是 trigonal bipyramidal 的 simple molecule，solid 里变成 PCl₄⁺（tetrahedral）和 PCl₆⁻（octahedral）（9701/22 Feb/Mar 2024 Q2(c)(i)）。

**同样是 2 bp + 2 lp，H₂S（92.5°）比 H₂O（104.5°）小**：O 比 S electronegative 得多（3.5 vs 2.5），O–H 的 bonding pairs 被拉得更靠近 O，两对 bonding pairs 靠得近、repulsion 大，张开的角度就大。

讲义附录表里 5、6 对 electron pairs 带 lone pair 的情形（see-saw SF₄、T-shaped ClF₃、linear XeF₂、square pyramidal BrF₅）syllabus 没有点名，讲义也划掉了，了解即可；square planar（XeF₄）讲义保留。

{{lo 3.5.2}}

<!-- html: 一步步推 shape 与 bond angle -->
{{cell vsepr-predict}}

<!-- md -->
## 3.6 Intermolecular forces, electronegativity and bond properties

### A. Bond polarity 与 dipole moment

- 两个 atoms 的 electronegativity **相同**（H₂、Cl₂、O₂）：bonding pair 被平均共享，bond **non-polar**。
- electronegativity **不同**：bonding pair 偏向 electronegativity 大的那个 atom，electron distribution 不对称——它带 partial negative charge **δ−**，另一个带 **δ+**。这个 bond 是 **polar**（has a dipole）。
- ΔEN 越大，bond 越 polar。
- molecule 的 polarity 用 **dipole moment** 衡量；画法是一支箭头指向 δ− 的一端（尾部带一小横，像 +）。

**molecule 是否 polar，要同时看两件事**：每个 bond 的 polarity，以及 bonds 在空间里的**排布**。

| molecule | polar bonds | shape | 各 bond dipole | molecule |
|---|---|---|---|---|
| CO₂ | 2 × C=O | linear | 方向相反，抵消 | **non-polar** |
| BF₃ | 3 × B–F | trigonal planar | 120° 对称，抵消 | non-polar |
| CCl₄ | 4 × C–Cl | tetrahedral | 对称，抵消 | non-polar |
| CHCl₃ | 3 × C–Cl（C–H 几乎 non-polar） | tetrahedral | 三个 C–Cl 指向同一侧，没被 C–H 抵消 | **polar**（δ− 在 Cl 一侧） |
| H₂O | 2 × O–H | non-linear | 不抵消 | polar |
| NH₃ | 3 × N–H | pyramidal | 不抵消 | polar |
| SCl₂ | 2 × S–Cl | non-linear | 不抵消 | polar |

**not all molecules with polar bonds are polar molecules**——对称的形状会让 bond dipoles 抵消。

判分细节：

- 在 SCl₂ 上标 dipoles（9701/21 May/June 2026 Q1(c)(ii)）：S 写 **δ+** AND 两个 Cl 都写 **δ−**；只写 δ 不写正负号 → 拒绝。
- 「H₂O has a greater dipole moment than SCl₂. Explain」（同卷 Q1(d)(iii)）：**electronegativity difference (between H and O) is greater (than S and Cl)**。写 "oxygen is more electronegative than chlorine"、"H₂O is more polar" 都不给分——要比的是**差值**。
- polarity 影响 reactivity：N₂（non-polar）很不活泼，而 isoelectronic 的 C≡O 是 polar，能作 reducing agent；chloroethane 的 polar C–Cl 被 OH⁻ 进攻（chapter 15）。

{{lo 3.6.2}}

<!-- html3d: polar 与 non-polar molecule -->
{{cell polarity}}

<!-- md -->
### B. van der Waals' forces

**van der Waals' forces**：the intermolecular forces between molecular entities other than those due to bond formation——syllabus 把它当作**所有 intermolecular forces 的总称**。分两类：

| | instantaneous dipole–induced dipole（**id-id**，London dispersion forces） | permanent dipole–permanent dipole（**pd-pd**） |
|---|---|---|
| 存在于 | **所有** molecules / atoms 之间（包括 noble gases、non-polar molecules） | **polar** molecules 之间（同时也有 id-id） |
| 来源 | electron cloud 不停运动，某一瞬间一侧 electrons 多 → 瞬时 dipole → 诱导邻近 molecule 产生 dipole → δ+ 与 δ− 互相吸引；一直在变、是暂时的 | molecule 本来就有 δ+ / δ−，相邻 molecules 的 δ+ 与 δ− 互相吸引 |
| 越强，当 | **number of electrons** 越多；**contact points**（表面积）越多 | dipole 越大 |
| hydrogen bonding | — | 是 pd-pd 的一个特例（C） |

**id-id 随 electron 数增大**：

- noble gases：He −269、Ne −246、Ar −186、Kr −153、Xe −108（boiling point / °C）。
- halogens：F₂ −188、Cl₂ −35、Br₂ +59、I₂ +184 °C。解释的写法：number of **electrons** increases → stronger id-id forces → more energy needed to overcome them → boiling point increases（讲义提醒：写 "number of protons" 或 "size of molecule" 不给分）。
- Group 14 hydrides CH₄ → PbH₄（9701/21 Oct/Nov 2024 Q3(d)(i)）：M1 molecules have **greater number of electrons**；M2 **stronger id-id forces**（或 more energy required to overcome the id-id forces）。

**id-id 随 contact points 增大**：同分异构体 electron 数一样，形状越「直」接触越多。

- pentane（直链，36 °C）> 2,2-dimethylpropane（球形，10 °C）。
- hexane > 2-methylpentane > 2,3-dimethylbutane（9701/22 Oct/Nov 2025 Q3(d)(ii)）：M1 顺序；M2 unbranched has **stronger / more IMFs**；M3 unbranched requires **more energy**（to separate the molecules）。

**pd-pd 比同等 electron 数的 id-id 强**：

- propanone（polar，56 °C，liquid）vs butane（non-polar，−1 °C，gas）——electron 数几乎一样（32 vs 34）。
- ICl（97 °C）vs Br₂（59 °C）——electron 数相同（70），ICl 有 permanent dipole。
- methanal 在 −30 °C 是 liquid、CO₂ 是 gas（9701/21 Oct/Nov 2025 Q1(c)(iv)）：M1 CO₂ has **only id-id** forces AND methanal has **pd-pd** (and id-id) forces；M2 IMFs in methanal are **stronger**。CO₂ 有 polar bonds，但 molecule non-polar。
- SCl₂ 和 H₂O 的 id-id 比较（9701/21 May/June 2026 Q1(d)(ii)）：SCl₂ AND **greater number of electrons** (per molecule)（SCl₂ 50 个 vs H₂O 10 个）。写 "more valence electrons" 或 "greater electron density" 不给分。

{{lo 3.6.3}}

<!-- html: boiling point 与 intermolecular forces -->
{{cell imf}}

<!-- md -->
### C. Hydrogen bonding

**hydrogen bonding**：一种特别强的 **pd-pd**，发生在 hydrogen bonded to a **highly electronegative atom**（syllabus 限 N–H、O–H；讲义另加 F–H）的 molecules 之间。需要：

1. 一个 molecule 有 H 直接连在 N / O / F 上——这个 bond 极度 polar，H 几乎裸露成 δ+；
2. 另一个 molecule 的 N / O / F 上有 **lone pair**。

H 的 δ+ 与邻近 molecule 的 lone pair 吸引。hydrogen bond 大约是 covalent bond 强度的 1/10；O–H···O 三个 atoms 通常在一条直线上（180°）。

**画 hydrogen bond 的判分**（9701/22 Feb/Mar 2026 Q4(b)，CH₂(CN)COOH 与 H₂O）：

- M1 hydrogen bond 画得清楚（虚线）并**标注** "hydrogen bond"；
- M2 从 O 上的 **lone pair** 指向另一个 molecule 里**连在 O 上的 H**；
- M3 跨两个 molecules 连续三个正确的 partial charges：**δ−** O–H **δ+** ···· **δ−** O。

每个 molecule 平均形成多少 hydrogen bonds，取决于 N / O / F 上的 H 数和 lone pair 数中**较少**的那个：

- H₂O：2 个 H、2 对 lone pairs → 平均 **2** 个 hydrogen bonds per molecule（extensively hydrogen bonded）；
- NH₃：3 个 H、只有 1 对 lone pair → 平均只有 **1** 个；所以 NH₃ 的 boiling point（−33 °C）比 H₂O（100 °C）低得多。

**hydrogen bonding 解释 water 的 anomalous properties**：

| property | 现象 | 原因 |
|---|---|---|
| relatively high melting and boiling points | H₂O 100 °C，而 H₂S −60 °C、H₂Se −41 °C、H₂Te −2 °C（按趋势 H₂O 应约 −80 °C） | Group 16 其他 hydrides 只有 id-id + pd-pd；water 之间有 extensive hydrogen bonding，需要多得多的 energy 才能分开 |
| relatively high surface tension | 水面像一层膜，比多数 liquid 的 surface tension 大 | 表面的 molecules 被下面的 molecules 用 hydrogen bonds 往里拉 |
| density of ice < liquid water | ice 浮在水上（大多数 substance 的 solid 比 liquid 密） | ice 里每个 O 被 4 个 H 以 tetrahedral 方式包围，形成 3D hydrogen-bonded 的 **open lattice**；hydrogen bonds 比 covalent bonds 长，molecules 离得比 liquid 里远；熔化时 lattice 部分塌缩，molecules 靠得更近 |

HF（+20 °C）和 NH₃ 在各自 group 里也是同样的反常；CH₄（Group 14）没有 hydrogen bonding，所以 Group 14 的曲线没有反常、一路上升。

{{lo 3.6.1}}

<!-- html: hydrogen bond 怎样画 -->
{{cell hbond}}

<!-- md -->
### D. 强弱排序

一般来说，**ionic, covalent and metallic bonding are stronger than intermolecular forces**：

giant covalent / ionic / metallic bonding ≫ hydrogen bonding > pd-pd > id-id

（同一类的 substance 比较时，例如 I₂ 的 id-id 比 NH₃ 的 hydrogen bonding 强——electron 数差太多。上面的排序是指 electron 数相近时。）

所以 simple molecular substance 熔化 / 沸腾时只克服 intermolecular forces，molecule 里的 covalent bonds **不断**——Cl₂ 沸腾得到的还是 Cl₂ molecules。

{{lo 3.6.4}}

<!-- md -->
## 3.7 Dot-and-cross diagrams

**dot-and-cross diagram**：画出 outer-shell electrons 的排布，用 • 和 × 区分 electrons 来自哪个 atom（第三种 atom 用 ○ 或 △）。

- covalent：两个 atom 的圆圈**相交**，shared pair 画在相交区；electrons 成对画，数得出 bonding pairs 与 lone pairs。
- ionic：每个 ion 单独画、加 **square brackets** 和 charge，ions 之间不相交。
- coordinate bond：那一对 shared pair 的两个 electrons **用同一种符号**（都是来自提供 lone pair 的 atom）。
- 允许画 expanded octet（SF₆、PCl₅、SO₂）和 odd number of electrons（NO）。

判分细节：

- SCl₂（9701/21 May/June 2024 Q2(b)(i)）：M1 每个 S–Cl 之间一对 shared pair（一 ×、一 •）；M2 每个 Cl 另有 6 个 non-bonding electrons（只用 ×），S 另有 4 个（只用 •）。
- SF₆（9701/21 May/June 2026 Q1(a)(i)）：6 对 bonding pairs，每个 F 3 对 lone pairs，S 上没有 lone pair。符号随意、画在圆周上或空隙里都行、non-bonding electrons 不必成对；多画 inner electrons 不扣分也不给分。
- Li₂O 画 **all** electrons（9701/22 May/June 2026 Q1(b)）：M1 charges 正确（O²⁻ 与 Li⁺）；M2 其余全对（Li⁺ 只剩 1s²，O²⁻ 是 2,8，括号、系数 2）。误画成 covalent 最多 1 分。

{{lo 3.7.1}}

<!-- html: dot-and-cross diagrams -->
{{cell dotcross}}

<!-- md -->
## Practice

2024–2026 Paper 2 里所有考 chapter 3 的小问，按考试时间排列（含正本在其他章、但这一小问考本章的）。题干里与本章无关的部分只保留到看得懂为止。表格里的空格可以直接填（填对变绿），再展开 **答案** 对照 mark scheme。

<!-- practice: 9701/22 Feb/Mar 2024 -->
### 9701/22 Feb/Mar 2024

#### Q1(a) [1]
Bismuth is an element in Group 15 of the Periodic Table. Bismuth has metallic bonding. Draw a labelled diagram to show the metallic bonding in bismuth.

::: answer
规则排列的「+」圆圈（metal cations，例如三排、每排五个），之间散布「−」号（delocalised electrons），两者各引一条标注线。

判分：图必须同时体现 ① **regular arrangement of positive ions** ② AND **surrounded by / (sea of) delocalised electrons**。
:::

#### Q2(c)(i) [2]
An excess of Cl₂ reacts with phosphorus to form PCl₅. PCl₅ is a simple molecule in the gas phase. It also exists in a solid form as two ions, PCl₄⁺ and PCl₆⁻. Complete Table 2.2 to identify the shapes of each of these species.

| species | PCl₅ | PCl₄⁺ | PCl₆⁻ |
|---|---|---|---|
| shape | [[trigonal bipyramidal|trigonal bipyramid]] | tetrahedral | [[octahedral]] |

::: answer
PCl₅ **trigonal bipyramidal**（5 bp, 0 lp）；PCl₆⁻ **octahedral**（P：5 + 1 = 6 electrons，6 bp, 0 lp）。PCl₄⁺ 是题目给的：5 − 1 = 4 → tetrahedral。
:::

<!-- practice: 9701/21 May/June 2024 -->
### 9701/21 May/June 2024

#### Q2(b)(i) [2]
A molecule of SCl₂ contains two S–Cl covalent bonds. Complete the dot-and-cross diagram in Figure 2.1 to show the arrangement of the outer electrons in a molecule of SCl₂. Use × to show electrons from the chlorine atoms. Use ● to show electrons from the sulfur atom.

{{img passyear/extracted/ch03-chemical-bonding/img/9701_s24_21_fig2-1.png 420}}

::: answer
- M1 每个 S–Cl 相交区一对 shared pair（一个 ×、一个 ●）
- M2 每个 Cl 另有 6 个 non-bonding electrons（3 对，只用 ×）；S 另有 4 个（2 对，只用 ●）

（S：6 个 outer electrons，2 个用于 bonding、4 个是 2 对 lone pairs。）
:::

#### Q2(b)(ii) [2]
Predict the shape of, and bond angle in, a molecule of SCl₂ by using VSEPR theory.

::: answer
- shape：**non-linear**（bent）
- bond angle：**103–105°**

S 上 2 bonding pairs + 2 lone pairs，和 H₂O 一样。
:::

#### Q5(a) [1]
Hydrocarbon molecules contain covalent bonds. Define covalent bond.

::: answer
(electrostatic) attraction between **nuclei** of two atoms and **shared pair** of electrons
:::

#### Q5(b)(i) [1]
A C=C bond in an alkene is made from a σ bond and a π bond. Identify the hybridisation of the carbon atoms in a C=C bond in an alkene.

::: answer
**sp²**（每个 C 有 3 个 σ：1 个 C–C、2 个 C–H/C–C；剩一个 p 形成 π）
:::

#### Q5(b)(ii) [2]
Draw labelled diagrams to show, in terms of orbital overlap, how the σ and π bonds are made in a C=C bond.

::: answer
- **σ bond**：两个 sp² orbitals 沿两个 nuclei 的连线 **direct（end-on）overlap**，overlap 区在两个 nuclei 正中间。
- **π bond**：两个 C 各一个没 hybridise 的 **p orbital**（上下两瓣），**sideways overlap**——上瓣与上瓣、下瓣与下瓣，在 C–C 连线的上方和下方各一团；标注 "p (orbitals)" 和 "sideways overlap"。

（3.4 D 的 3D 图可以对照着画。）
:::

#### Q5(c)(i) [1]
In electrophilic reactions involving alkenes the π bond of C=C is broken. Suggest one difference between σ and π bonds that explains why the π bond is broken in electrophilic addition reactions involving alkenes.

::: answer
**EITHER** (pair of) electrons in π bond are **further away from the nuclei** so **weaker attraction**
**OR** (pair of) electrons in σ bond are closer to the two nuclei so stronger attraction
:::

<!-- practice: 9701/22 May/June 2024 -->
### 9701/22 May/June 2024

#### Q1(c) [1]
Draw a labelled diagram to show the structure and bonding in sodium.

::: answer
规则排列、至少 2 × 2 个圆圈，每个圈内标「+」（Na⁺），圆圈之间散布「−」；分别标注 **positively charged ions** 和 **delocalised electrons**（sea of delocalised electrons 包围着正离子）。
:::

<!-- practice: 9701/23 May/June 2024 -->
### 9701/23 May/June 2024

#### Q1(a)(ii) [4]
Covalent bonds can be σ bonds or π bonds. Complete Table 1.1 to show the number of σ and π bonds in a molecule of N₂ and to describe how the orbitals overlap to form σ and π bonds.

| | σ bond | π bond |
|---|---|---|
| number of bonds in N₂ | [[1]] | [[2]] |
| how the orbitals overlap | [[direct|end-on|head-on]] | [[sideways]] |

::: answer
| | σ bond | π bond |
|---|---|---|
| number of bonds in N₂ | 1 | 2 |
| how the orbitals overlap | **direct** (orbital overlap) | **sideways** (overlap of adjacent p orbitals) |
:::

#### Q4(a) [2]
NH₃(g) reacts with HCl(g) to produce NH₄Cl(s): NH₃(g) + HCl(g) → NH₄Cl(s). Draw a diagram to show the ionic, covalent and coordinate bonding present in a formula unit of NH₄Cl.

::: answer
[NH₄]⁺ 画在方括号里、标「+」：N 连 4 个 H，其中 3 条普通 covalent bond，**1 条画成从 N 指向 H 的箭头**（coordinate bond，用的是 N 的 lone pair）；方括号外单独一个 Cl⁻，两者之间是 ionic bond（不共用 electrons）。

- M1（ionic bond between）**NH₄⁺ AND Cl⁻** AND 4 条 N–H covalent bonds（或 4 对 shared pairs）
- M2 其中 1 条 N–H 是 **coordinate bond**：箭头方向正确，或那 1 对 bonding electrons 只用同一种符号
:::

<!-- practice: 9701/21 Oct/Nov 2024 -->
### 9701/21 Oct/Nov 2024

Figure 3.2 shows the boiling points of the simplest hydrides of the Group 14 elements, C to Pb.

{{img passyear/extracted/ch03-chemical-bonding/img/9701_w24_21_fig3-2.png 460}}

#### Q3(d)(i) [2]
Explain the trend in the boiling points of the Group 14 hydrides shown in Figure 3.2.

::: answer
- M1 molecules CH₄ to PbH₄ have **greater number of electrons** / number of electrons increase
- M2 **greater / stronger instantaneous dipole–induced (dipole) forces** / London forces / dispersion forces **OR** more energy required to overcome the id-id forces
:::

#### Q3(d)(ii) [1]
Deduce the shape of a molecule of SiH₄.

::: answer
**tetrahedral**（Si 4 个 outer electrons，4 bp、0 lp，和 CH₄ 一样）
:::

<!-- practice: 9701/22 Feb/Mar 2025 -->
### 9701/22 Feb/Mar 2025

#### Q1(b)(ii) [1]
P₄ reacts with Cl₂. Predict the shape of a molecule of PCl₅.

::: answer
**trigonal bipyramid(al)**
:::

#### Q2(a) [2]
The Group 2 elements show metallic bonding. Define metallic bonding.

::: answer
**electrostatic attraction** between **positive metal ions / cations** and **delocalised electrons**
:::

<!-- practice: 9701/21 May/June 2025 -->
### 9701/21 May/June 2025

#### Q1(a)(i) [1]
Solid sodium conducts electricity. Sodium oxide conducts electricity when molten but not when solid. Name the type of bonding present in sodium and in sodium oxide.

| | sodium | sodium oxide |
|---|---|---|
| type of bonding | [[metallic]] | [[ionic]] |

::: answer
sodium – **metallic** AND sodium oxide – **ionic**（两个都对才给 1 分）
:::

<!-- practice: 9701/23 May/June 2025 -->
### 9701/23 May/June 2025

#### Q5(b)(i) [2]
Z is the ester CH₂=C(CH₃)COOCH₃ (methyl 2-methylprop-2-enoate). Deduce the number of sigma (σ) bonds and pi (π) bonds present in Z.

number of σ bonds = [[14]]　number of π bonds = [[2]]

::: answer
每一条 bond（不管单、双）有且只有 1 个 σ：

- C–H：CH₂ 上 2 + CH₃ 上 3 + OCH₃ 上 3 = 8
- C–C / C=C：C=C、C–CH₃、C–C(=O) = 3
- C=O 1；C–O：C(=O)–O 和 O–CH₃ = 2

σ = 8 + 3 + 1 + 2 = **14**；π：C=C 一个、C=O 一个 = **2**
:::

<!-- practice: 9701/21 Oct/Nov 2025 -->
### 9701/21 Oct/Nov 2025

#### Q1(c)(iv) [2]
Methanal, CH₂O, is a liquid at −30 °C but carbon dioxide is a gas at this temperature. Explain why.

::: answer
- M1 CO₂ has **only** instantaneous / temporary dipole–induced dipole forces **AND** methanal has **permanent dipole–permanent dipole** (and id-id) forces
- M2 IMFs in methanal are **stronger** than IMFs in CO₂

（CO₂ 的两个 C=O 都 polar，但 linear 形状让 dipoles 抵消，molecule non-polar；methanal trigonal planar，dipole 不抵消。）
:::

<!-- practice: 9701/22 Oct/Nov 2025 -->
### 9701/22 Oct/Nov 2025

Hexane, C₆H₁₄, has four structural isomers. Fig. 3.1 shows hexane and two of its structural isomers.

{{img passyear/extracted/ch03-chemical-bonding/img/9701_w25_22_fig3-1.png 520}}

#### Q3(d)(ii) [3]
A, B and hexane have different boiling points. Arrange A, B and hexane in order of increasing boiling point. Explain your answer.

lowest [[B]] < [[A]] < [[hexane]] highest

::: answer
- M1 **B < A < hexane**
- M2 hexane / unbranched has **stronger / more IMFs**
- M3 hexane / unbranched requires **most / more energy**

B（2,3-dimethylbutane，两个支链）最紧凑、contact points 最少，id-id 最弱；hexane 是直链，contact points 最多。三者 electron 数相同。
:::

<!-- practice: 9701/22 Feb/Mar 2026 -->
### 9701/22 Feb/Mar 2026

Nitrogen monoxide, NO, is an atmospheric pollutant. Figure 2.1 shows the dot-and-cross diagram of NO.

{{img passyear/extracted/ch03-chemical-bonding/img/9701_m26_22_fig2-1.png 360}}

#### Q2(a)(i) [1]
NO has an unpaired electron. State the term for a molecule with an unpaired electron.

::: answer
**(free) radical**
:::

#### Q2(a)(ii) [1]
In NO, the N and O atoms are bonded by a sigma (σ) and a pi (π) bond. Complete Figure 2.2 to show the pi bond in NO that is formed from orbital overlap.

{{img passyear/extracted/ch03-chemical-bonding/img/9701_m26_22_fig2-2.png 420}}

::: answer
在 N–O 连线的**上方和下方**各画一瓣（两个 p orbitals sideways overlap 形成的 π，一团在上、一团在下）。
:::

#### Q4(b) [3]
CH₂(CN)COOH is very soluble in water because it can form hydrogen bonds with water. Complete Figure 4.2 to show one hydrogen bond between a molecule of CH₂(CN)COOH and a molecule of H₂O. Label the hydrogen bond clearly, and show any relevant partial charges and lone pairs of electrons.

{{img passyear/extracted/ch03-chemical-bonding/img/9701_m26_22_fig4-2.png 480}}

::: answer
- M1 clearly distinct / **labelled** H bond
- M2 from **lone pair on any oxygen** to **H atom attached to O**
- M3 with **three correct successive partial charges** across two molecules（δ− O–H δ+ ···· δ− O）

例如：COOH 的 O–H 的 H（δ+）···· H₂O 的 O（δ−，画出 lone pair），再在 COOH 的 O 上标 δ−。
:::

<!-- practice: 9701/21 May/June 2026 -->
### 9701/21 May/June 2026

#### Q1(a)(i) [1]
Complete the dot-and-cross diagram in Figure 1.1 to show the arrangement of outer shell electrons in a molecule of SF₆.

{{img passyear/extracted/ch03-chemical-bonding/img/9701_s26_21_fig1-1.png 360}}

::: answer
S 与每个 F 之间一对 shared electrons（共 6 对 bonding pairs）；每个 F 再补 3 对 lone pairs；S 上没有 lone pair。

判分：符号随意（全同或不同都行）；electrons 画在圆周上或空隙里都行；non-bonding electrons 不必成对；inner electrons 画了不扣也不给。
:::

#### Q1(a)(ii) [1]
Name the shape of a molecule of SF₆.

::: answer
**octahedral**（接受 square bipyramidal / octahedron / octohedral；**拒绝** octagonal）
:::

#### Q1(c)(i) [3]
A molecule of SCl₂ is polar. Predict bond angle *x* in Figure 1.2 using VSEPR theory. Explain your answer.

{{img passyear/extracted/ch03-chemical-bonding/img/9701_s26_21_fig1-2.png 300}}

bond angle *x* = [[104.5|104|103|105]] °

::: answer
- M1 **104.5°**（接受 103–105°）
- M2 **2 bonding pairs** (of electrons) **and 2 lone pairs** (of electrons)
- M3 **lone pairs repel more than bonding pairs**（或 lp–lp > lp–bp > bp–bp）

判分：写「2 S–Cl bonds」代替 bonding pairs 不给 M2；「2 bonding pairs + 1 lone pair」且 107–109° 最多 1 分；提 tetrahedral / 109.5° 不扣分。
:::

#### Q1(c)(ii) [1]
Show on Figure 1.3 all the dipoles present in the molecule of SCl₂.

{{img passyear/extracted/ch03-chemical-bonding/img/9701_s26_21_fig1-3.png 300}}

::: answer
S 标 **δ+** AND 两个 Cl 都标 **δ−**。

判分：接受 δ+δ+ / 2δ+，接受只用 + 和 −；只写 δ 或 δ 不带正负号 → 拒绝；只画一支总 dipole 箭头不给分。
:::

#### Q1(d)(i) [1]
SCl₂ and H₂O both contain instantaneous dipole–induced dipole attractions and permanent dipole attractions. Complete Table 1.2.

| | SCl₂ | H₂O |
|---|---|---|
| total number of electrons per molecule | [[50]] | 10 |

::: answer
SCl₂：16 + 2 × 17 = **50**
:::

#### Q1(d)(ii) [1]
Identify which molecule, SCl₂ or H₂O, has the stronger instantaneous dipole–induced dipole attractions. Explain your answer.

::: answer
**SCl₂** AND **greater number of electrons** (per molecule)（或 H₂O has weaker id-id as it has smaller number of electrons）

判分：写 greater electron density / electron cloud、more valence / outer electrons 都不给分。
:::

#### Q1(d)(iii) [1]
H₂O has a greater dipole moment than SCl₂. Explain why.

::: answer
**electronegativity difference** (between H and O) is **greater** (than S and Cl)

判分：「H₂O is more polar」「oxygen is more electronegative than chlorine」「hydrogen bonding」都不给分；「H₂O is more electronegative than SCl₂」拒绝。
:::

<!-- practice: 9701/22 May/June 2026 -->
### 9701/22 May/June 2026

#### Q1(b) [2]
Lithium reacts with oxygen to produce lithium oxide, Li₂O. Li₂O is a white solid with a melting point over 1400 °C. Draw a dot-and-cross diagram to show the arrangement of **all** the electrons in Li₂O.

::: answer
2[Li]⁺ [O]²⁻：

- [Li]⁺：只剩 inner shell 的 **2** 个 electrons（1s²），方括号、右上角 +，前面系数 2（或画两个）；
- [O]²⁻：inner shell 2 个 + outer shell **8** 个，其中 2 个用另一种符号（来自两个 Li），方括号、右上角 2−。

- M1 charges 都正确（−2 for O ion AND +1 for Li ion）
- M2 其余全对（electron 数、方括号、系数 2）

误画成 covalent 但其余全对，最多 1 分。（3.7 的交互件里切到「all electrons」看。）
:::

<!-- md -->
{{lo-checklist}}
