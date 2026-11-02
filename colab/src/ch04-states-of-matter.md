<!-- md -->
# Chapter 4 States of matter

Cambridge International AS & A Level Chemistry 9701（2025 / 2026 / 2027）· **Physical chemistry**

- 内容边界与 learning outcome 逐字取自 syllabus；常数取自 data booklet；判分句式取自 2024–2026 Paper 2 的 mark scheme，引用写卷号。
- 🔬 / 🧊 / 📝 开头的 cell 是交互图（已经预先渲染好，打开就能用）。如果显示空白：**Runtime → Run all**（连本地运行时即可，几秒跑完）。🧊 是 3D 图，要联网载入 three.js。
- 本章两半：4.1 是 gas 的计算（*pV* = *nRT*），4.2 是「structure 决定 property」的解释题。后者在 Paper 2 里几乎每卷都出现，常常挂在 chapter 3 或 chapter 9 的大题里。

本章用到的常数（data booklet）：

| 常数 | 值 |
|---|---|
| molar gas constant, *R* | 8.31 J K⁻¹ mol⁻¹ |
| molar volume of gas, *V*ₘ | 24.0 dm³ mol⁻¹ under room conditions；22.4 dm³ mol⁻¹ at s.t.p.（101 kPa，273 K） |

<!-- md -->
## 背景：solid、liquid、gas

（讲义开头的复习内容，syllabus 4.1 / 4.2 都建立在它上面。）

| | solid | liquid | gas |
|---|---|---|---|
| arrangement | regular，particles 紧密接触 | 大多 random，particles 仍然靠得很近 | random，particles 相距很远 |
| movement | 只能在固定位置 vibrate | 可以互相 slide past | 向各个方向快速、random 地运动 |
| compress | 几乎不能 | 只能稍微压缩（fixed volume） | 很容易压缩 |

**change of state** 的本质：加热时 particles 的 kinetic energy 增大，足以 overcome particles 之间的 forces of attraction。

- **melting**：solid → liquid，发生在 melting point（1 atm 下）。
- **vaporisation**：liquid → gas。**evaporation** 在 boiling point 以下就会发生——表面能量最高的 molecules 先逃逸；到 boiling point 时整个 liquid 里都形成 vapour。
- **freezing / condensation** 反过来：particles 失去 kinetic energy，attraction 把它们拉近。
- **sublimation**：solid 直接变 gas（dry ice、iodine、naphthalene、aluminium chloride）；反过来叫 **deposition**。
- 在 closed system 里 liquid ⇌ gas 会达到 equilibrium：vaporisation 和 condensation 的 rate 相等。此时 vapour 对器壁的压强叫 **vapour pressure**，温度越高越大。

要 overcome 的是什么力，决定了 melting point / boiling point 的高低——这就是 4.2 的主题：

| type of structure | 熔化 / 沸腾时要 overcome 的力 | melting point / boiling point |
|---|---|---|
| giant ionic | ionic bonds（electrostatic attraction between oppositely charged ions） | high |
| giant metallic | metallic bonds | 一般 high |
| giant molecular | covalent bonds | very high |
| simple molecular | intermolecular forces（id-id、pd-pd、hydrogen bond），**不是** covalent bond | low |

<!-- md -->
## 4.1 The gaseous state: ideal and real gases and *pV* = *nRT*

### A. Kinetic theory：pressure 从哪里来

kinetic theory of gases 的假设：

1. gas molecules 不停地做 rapid、random 的运动；
2. molecules 之间的距离远大于 molecule 本身的直径，所以 molecules 自身的 volume 可以忽略（negligible）；
3. molecules 之间没有 intermolecular forces of attraction（或 repulsion）；
4. 所有 collision 都是 elastic 的：collision 中没有 kinetic energy 损失；
5. gas 的 temperature 与 molecules 的 average kinetic energy 成正比。

**pressure 的来源**：gas molecules 不断撞击容器壁，每次撞击对壁施加一个力；单位面积上受到的总力就是 pressure（1 Pa = 1 N m⁻²）。

- volume 变小（*T* 不变）：molecules 挤得更近，**单位时间内撞壁的次数更多** → pressure 增大；
- temperature 升高（*V* 不变）：molecules 运动更快，撞壁**更频繁、每次更用力** → pressure 增大；
- molecules 更多（*n* 增大）：撞壁更频繁 → pressure 增大。

答题时 "collisions of gas molecules with the walls of the container" 这一句是核心，只写 "molecules move around" 不得分。

{{lo 4.1.1}}

<!-- html: gas pressure：molecules 撞壁 -->
{{cell gas-box}}

<!-- md -->
### B. Ideal gas 与三条 gas law

完全符合上面 kinetic theory 的 gas 叫 **ideal gas**。syllabus 要的两点：

- ideal gas 的 particles **volume 为零**（zero particle volume）；
- particles 之间**没有 intermolecular forces of attraction**。

真实的 gas（**real gas**）只是接近，不完全符合。

{{lo 4.1.2}}

三条 gas law 都是 ideal gas 的行为，合起来就是 *pV* = *nRT*：

| law | 保持不变 | 关系 | 例（讲义） |
|---|---|---|---|
| Boyle's law | *n*、*T* | *pV* = constant → *p*₁*V*₁ = *p*₂*V*₂ | 240 cm³ air at 100 kPa 压到 150 cm³：*p*₂ = 100 × 240 / 150 = **160 kPa** |
| Charles's law | *n*、*p* | *V* / *T* = constant → *V*₁ / *T*₁ = *V*₂ / *T*₂（*T* 必须用 K） | 1.13 dm³ at 47 °C → 29 °C：*V*₂ = 1.13 × 302 / 320 = **1.07 dm³** |
| Avogadro's law | *p*、*T* | *V* / *n* = constant：同温同压下，相同 volume 的 gas 含相同数目的 molecules | room conditions 下 1 mol 任何 gas ≈ 24.0 dm³ |

- Charles's law 的直线外推到 *V* = 0 时，温度是 −273 °C = 0 K（**absolute zero**）。real gas 在到达之前早就 liquefy / solidify 了。
- 两种 gas 混合（*T* 不变）：各自按 Boyle's law 算出在总 volume 里的 partial pressure，再相加。例：5 dm³ He at 12 kPa 与 10 dm³ Ne at 6 kPa 相连 → 15 dm³ 里 He 4 kPa、Ne 4 kPa → 总 pressure **8 kPa**。

<!-- md -->
### C. The ideal gas equation *pV* = *nRT*

| 符号 | 量 | SI 单位 | 常见换算 |
|---|---|---|---|
| *p* | pressure | Pa | 1 kPa = 1000 Pa；1 atm = 101 325 Pa（题目常写 101 kPa） |
| *V* | volume | **m³** | 1 m³ = 1000 dm³ = 10⁶ cm³；1 dm³ = 10⁻³ m³；1 cm³ = 10⁻⁶ m³ |
| *n* | amount | mol | *n* = *m* / *M* |
| *R* | molar gas constant | J K⁻¹ mol⁻¹ | 8.31（data booklet；= 8.31 m³ Pa K⁻¹ mol⁻¹） |
| *T* | temperature | **K** | *T* / K = *θ* / °C + 273 |

**单位是这一节失分最多的地方**：*p* 用 Pa、*V* 用 m³、*T* 用 K。也可以 *p* 用 kPa、*V* 用 dm³——两边都放大 1000 倍，*pV* 不变（9701/23 May/June 2026 Q2(c) 的 mark scheme 明确接受「101 × 617.0 × 10⁻³」这种一致换算）。但 Pa 配 dm³、kPa 配 cm³ 都是错的。

例 1：0.500 mol CO₂ at 150 kPa、19 °C 的 volume。

1. *p* = 150 000 Pa，*T* = 19 + 273 = 292 K
2. *V* = *nRT* / *p* = 0.500 × 8.31 × 292 / 150 000 = **8.09 × 10⁻³ m³**（= 8.09 dm³）

例 2：5.00 dm³ flask 里有 4.00 g O₂（*M*ᵣ = 32.0），127 °C 时的 pressure。

1. *n* = 4.00 / 32.0 = 0.125 mol；*V* = 5.00 × 10⁻³ m³；*T* = 400 K
2. *p* = *nRT* / *V* = 0.125 × 8.31 × 400 / (5.00 × 10⁻³) = **8.31 × 10⁴ Pa**（83.1 kPa）

**determination of *M*ᵣ**：把 *n* = *m* / *M* 代进去，

*pV* = (*m* / *M*) *RT*　→　*M* = *mRT* / (*pV*)

例 3：ethane 在 20 °C、1 atm 下的 density 是 1.264 g dm⁻³。1 dm³（= 1 × 10⁻³ m³）里有 1.264 g：

*M* = 1.264 × 8.31 × 293 / (101 325 × 1 × 10⁻³) = **30.4 g mol⁻¹**（C₂H₆ = 30.0，real gas 略有偏差）

讲义练习（答案在交互件里能直接验）：

- 2.00 dm³ flask 含 5.28 g gas，200 kPa、20 °C → *M*ᵣ = 5.28 × 8.31 × 293 / (200 000 × 2.00 × 10⁻³) = **32.1**
- 0.25 mol CO 在 10 dm³ flask 里 pressure 120 kPa → *T* = 120 000 × 0.010 / (0.25 × 8.31) = **578 K**
- 1.00 cm³ ice（density 1.00 g cm⁻³）在 596 K、101 kPa 变成 steam 的 volume：*n* = 1.00 / 18.0 = 0.0556 mol，*V* = 0.0556 × 24.0 × 596 / 298 = **2.67 dm³**（用 *V* ∝ *T* 从 24.0 dm³ at 298 K 换算；MCQ 选 C）

{{lo 4.1.3}}

<!-- html: pV = nRT 计算器（单位换算 + working） -->
{{cell pv-calc}}

<!-- md -->
### D. Real gases：什么时候偏离 ideal

real gas 不符合 kinetic theory 的正是 4.1.2 那两条：

1. molecules 之间**有** forces of attraction（id-id，polar molecule 还有 pd-pd，NH₃ 之类还有 hydrogen bond）；
2. molecules 自身的 volume **不能**忽略。

衡量偏离的量：**compression factor** *Z* = *pV* / *nRT*。ideal gas 永远 *Z* = 1。

| 条件 | 发生了什么 | 结果 |
|---|---|---|
| **low pressure、high temperature** | molecules 相距很远、运动很快：自身 volume 相对容器可以忽略，attraction 来不及起作用 | 最接近 ideal（*Z* ≈ 1） |
| low temperature（中等 pressure） | molecules 运动慢，attraction 把它们拉向彼此、拉离器壁 → 撞壁的力变小 | pressure 比 ideal 预测的**低**，*Z* < 1 |
| **very high pressure** | molecules 被挤得很近，自身 volume 占了容器的一大块，能自由运动的空间比 *V* 小；electron clouds 靠近时互相 repel | *pV* 比 ideal 预测的**大**，*Z* > 1 |
| 接近 boiling point | 快要 condense 成 liquid，attraction 已经很重要 | 偏离最大 |

结论（mark scheme 的句式）：**real gases behave most like an ideal gas at low pressure and high temperature**；偏离最大在 high pressure、low temperature。

**哪种 gas 更 ideal**：比的就是那两条——molecule 越小、intermolecular forces 越弱，越 ideal。

- noble gases（He、Ne）最接近：monatomic、non-polar、electrons 很少 → id-id forces 特别弱，atom 也小。
- polar molecule（NH₃、SO₂）、大 molecule（CO₂、C₂H₄）偏离较大。讲义的 molar volume at s.t.p.（3 s.f.）：He、N₂、O₂ 都是 22.4 dm³；CH₄、CO₂ 22.3；C₂H₄ 22.2；NH₃ 22.1；SO₂ 21.9——attraction 越强，molar volume 越被「拉小」。

9701/23 May/June 2026 Q2(b)：Group 18 里 neon 最像 ideal gas，因为 it has the **smallest** volume（atoms）和 the **weakest** id-id forces——两点都要带比较级。

<!-- html: ideal vs real gas：Z = pV / nRT -->
{{cell real-gas}}

<!-- md -->
## 4.2 Bonding and structure

很多 ionic、metallic、covalent substance 是 **crystalline** 的：particles（ions、atoms 或 molecules）在三维空间里规则地重复排列，这种排列叫 **crystal lattice**。syllabus 要会描述四类：

| type of structure | lattice 里的 particle | 把它们连起来的力 | 例（syllabus 点名） |
|---|---|---|---|
| **giant ionic** | positive ions 和 negative ions 交替 | ionic bonding（strong electrostatic attraction between oppositely charged ions，**all directions**） | sodium chloride、magnesium oxide |
| **simple molecular** | 小 molecules | molecule **内** strong covalent bonds；molecule **之间** weak intermolecular forces | iodine、buckminsterfullerene C₆₀、ice |
| **giant molecular**（giant covalent） | atoms | strong covalent bonds 贯穿整个 structure | silicon(IV) oxide、graphite、diamond |
| **giant metallic** | positive metal ions | metallic bonding：positive ions 与 sea of delocalised electrons 之间的 attraction | copper |

{{lo 4.2.1}}

### A. Giant ionic：NaCl、MgO

- 三维的 alternating positive and negative ions；lattice 的形状由 ions 的相对大小决定。
- NaCl 和 MgO 都是 **cubic**（同一种 lattice）：每个 Na⁺ 被 6 个 Cl⁻ 包围，每个 Cl⁻ 也被 6 个 Na⁺ 包围（**6 : 6 coordination**）。Cl⁻（0.181 nm）比 Na⁺（0.095 nm）大得多，Na⁺ 嵌在 Cl⁻ 之间的空隙里，离它们尽可能近。
- MgO 的 ions 是 Mg²⁺ 和 O²⁻：charge 是 NaCl 的两倍、ions 又更小 → attraction 强得多 → melting point 2852 °C，远高于 NaCl 的 801 °C。

### B. Giant metallic：copper

- positive metal ions 排成规则的层（copper 是 cubic close packing），被 **sea of delocalised electrons** 包围；attraction 作用于所有方向。
- 受力时 layers 可以滑过彼此，新位置上 ions 与 delocalised electrons 之间的 metallic bonds 立即重新形成 → **malleable**（能锤成各种形状）、**ductile**（能拉成丝）。
- **alloy**：加入大小不同的另一种 atom（brass = copper + zinc；bronze = copper + tin）。Zn atoms 比 Cu 大，打乱层的规则排列，layers 不容易滑动 → 比纯 copper **更硬、更强**，但仍然 malleable。aluminium alloy（加 Cu、Mg、Si、Mn）轻、强、耐腐蚀，用于飞机机身、自行车架。

### C. Simple molecular：iodine、C₆₀、ice

- **iodine**：I₂ molecules 规则排列成 lattice。相邻两个 I₂ molecule 的 nuclei 距离比**同一个** I₂ 里两个 nuclei 的距离大——molecule 内是 strong covalent bond，molecule 之间只有 weak id-id forces。加热时只需要 overcome id-id forces → melting point 低，还会 sublime。
- **buckminsterfullerene C₆₀**：60 个 C atoms 组成足球形的笼子（12 个 pentagons + 20 个 hexagons），每个 C 连 3 个 C。它是 **simple molecule**（不是 giant structure）：molecules 之间只有 weak intermolecular forces → 约 600 °C sublime、比较软、能少量溶于 methylbenzene 之类的 solvent；有一部分 electrons delocalised，但比 graphite 少 → conductivity 远不如 graphite。
- **ice**：H₂O molecules 通过 **hydrogen bonds** 排成 open lattice，每个 O 周围 4 个 H（2 个 covalent bond + 2 个 hydrogen bond），tetrahedral 排列。这个空旷的结构让 ice 的 density 比 liquid water 小（ice 浮在水面上）；hydrogen bonding 的细节在 chapter 3。

### D. Giant molecular：diamond、graphite、SiO₂

diamond 和 graphite 是 carbon 的 **allotropes**（同一 element 的不同 structural forms）。

| | diamond | graphite | silicon(IV) oxide, SiO₂ |
|---|---|---|---|
| 每个 atom 连几个 | C 连 4 个 C，tetrahedral | C 连 3 个 C，hexagon 组成平面 layers | 每个 Si 连 4 个 O（tetrahedral）、每个 O 连 2 个 Si → formula SiO₂ |
| layer 之间 | — | weak id-id forces | — |
| delocalised electrons | 无：4 个 outer electrons 全部用于 bonding | 每个 C 的第 4 个 electron 在 p orbital 里，sideways overlap 形成 layer 上下的 delocalised electrons | 无 |
| melting point | very high（strong covalent bonds throughout） | very high（layer 内 strong covalent bonds） | very high（> 1600 °C） |
| hardness | very hard（3D network 很难破坏）→ drill tip | soft、slippery：layers 容易 slide → pencil lead、lubricant | hard |
| electrical conductivity | does not conduct | **conducts**：delocalised electrons move along / between the layers | does not conduct |

- SiO₂（quartz、sand 的主要成分）的结构和 diamond 很像：把 diamond 里每个 C 换成 Si，每两个 Si 之间插一个 O。
- **graphene** = 单独一层 graphite；**carbon nanotube** = 一层 graphene 卷成的圆筒（沿长轴导电、tensile strength 很高、melting point 约 3500 °C）。二者都不在 syllabus 点名的例子里，知道是 giant molecular 即可。

<!-- html3d: lattice 3D：九种晶格 -->
{{cell lattice}}

<!-- md -->
### E. Structure 怎样决定 physical properties

| property | giant ionic | giant metallic | giant molecular | simple molecular |
|---|---|---|---|---|
| melting / boiling point | high：要破坏大量 strong ionic bonds | 一般 high | very high：要破坏大量 strong covalent bonds | low：只需 overcome weak intermolecular forces |
| electrical conductivity | solid **不**导电（ions 固定在 lattice 里）；molten 或 aqueous 导电（**ions move**） | solid、liquid 都导电（**delocalised electrons move**） | 不导电；**graphite 例外**（delocalised electrons） | 不导电（没有 mobile charged particles） |
| solubility | 很多溶于 water（ions 被 polar water molecules 包围），不溶于 non-polar solvent | 不溶（有的与 water 反应） | 不溶于任何 solvent | 大多不溶于 water（能形成 hydrogen bond 的除外），溶于 non-polar solvent |
| 受力 | hard 但 **brittle**：一层移动半个 ion，同号 ions 对齐、互相 repel → 裂开 | malleable、ductile | diamond / SiO₂ hard；graphite soft | soft |

答 conductivity 题的标准句式（mark scheme 逐字）：

- metal（sodium、tin）：**delocalised electrons move (through the structure)** / delocalised electrons are free to move；
- ionic compound molten：**ions move (through the liquid)**——不能说 electrons move；
- graphite：**delocalised electrons move through / between the layers**；
- diamond 不导电：**no delocalised electrons** / all (4) outer electrons are used in bonding。

比较 melting point 时必须说清**破坏的是哪一种力**：「SiO₂ is giant covalent AND SiCl₄ is simple molecular, so less energy is needed to overcome the intermolecular forces in SiCl₄ than the covalent bonds in SiO₂」（9701/21 Oct/Nov 2024 Q3(e)(iii)）。只说 "SiCl₄ has weak bonds" 是错的——SiCl₄ 熔化时 Si–Cl covalent bond 根本没断。

{{lo 4.2.2}}

<!-- html: 受力与导电：metal vs ionic -->
{{cell properties}}

<!-- md -->
### F. 从数据推断 structure and bonding

题目给 melting point、conductivity（solid / molten / aqueous）、solubility、state at room temperature 或与 water 的反应，要你判断 structure 和 bonding，并**逐条说理由**。思路：

1. **melting point**：低（低于约 200 °C，或 room temperature 下是 liquid / gas）→ simple molecular；高 → giant（ionic、metallic 或 molecular 再看导电）。
2. **conductivity**：
   - solid 就导电（且 malleable、shiny）→ giant metallic（或 graphite）；
   - solid 不导电、molten / aqueous 导电 → giant ionic；
   - 都不导电 + melting point very high → giant molecular；
   - 都不导电 + melting point low → simple molecular。
3. 与 water 反应得 acidic solution、misty fumes（hydrolysis）→ 往往是 covalent chloride，simple molecular（chapter 9）。

判分时 structure 和 bonding 各占一分，**每一分都要「结论 AND 证据」**，例如 Bi₂O₃（9701/22 Feb/Mar 2024 Q1(b)(ii)）：

- M1 **giant AND** has a high melting point
- M2 **ionic AND** conducts electricity (only) when molten

{{lo 4.2.3}}

<!-- html: 推断 structure and bonding -->
{{cell deduce}}

<!-- md -->
## Practice

2024–2026 Paper 2 里所有考 chapter 4 的小问，按考试时间排列（含正本在其他章、但这一小问考本章的）。题干里与本章无关的部分只保留到看得懂为止。空格可以直接填（填对变绿），再展开 **答案** 对照 mark scheme。

<!-- practice: 9701/22 Feb/Mar 2024 -->
### 9701/22 Feb/Mar 2024

Bismuth is an element in Group 15 of the Periodic Table. Bismuth reduces water to form bismuth oxide, Bi₂O₃.

#### Q1(b)(ii) [2]
Bi₂O₃ is a yellow insoluble solid that melts at 1090 K. The molten compound conducts electricity. Deduce the structure and bonding of Bi₂O₃. Explain your answer.

::: answer
- M1 **giant AND** has a high melting point
- M2 **ionic AND** conducts electricity (only) when molten

每一分都是「结论 + 证据」：只写 "giant ionic" 没有理由得 0 分。
:::

<!-- practice: 9701/21 May/June 2024 -->
### 9701/21 May/June 2024

Boron nitride is a white solid that melts above 2900 °C. Figure 2.2 shows part of the lattice structure of a crystal of boron nitride.

{{img passyear/extracted/ch02-stoichiometry/img/9701_s24_21_fig2-2.png 420}}

#### Q2(d)(ii) [1]
Suggest the identity of another crystalline solid that has atoms arranged in layers similar to that of solid boron nitride.

::: answer
graphite

（B 和 N 交替排成 hexagon 组成的平面 layers，layers 之间是 weak intermolecular forces——和 graphite 一样。）
:::

<!-- practice: 9701/21 Oct/Nov 2024 -->
### 9701/21 Oct/Nov 2024

The Group 14 elements show a change from non-metallic to metallic character down the group. Table 3.1 shows some properties of two Group 14 elements, C and Sn, in their standard states. The table is incomplete.

#### Q3(a)(i) [3]
Complete Table 3.1.

| element | C (graphite) | Sn |
|---|---|---|
| state and appearance in standard state | grey shiny solid | silvery solid |
| electrical conductivity | [[good\|conductor\|good conductor]] | good |
| type of bonding | [[covalent]] | metallic |
| type of structure | giant | [[giant]] |

::: answer
- C (graphite) electrical conductivity：good / conductor
- C (graphite) type of bonding：covalent
- Sn type of structure：giant
:::

#### Q3(a)(ii) [1]
Identify the lattice structure shown by graphite.

::: answer
giant molecular
:::

#### Q3(a)(iii) [1]
Explain why Sn has good electrical conductivity.

::: answer
its delocalised electrons are free to move
:::

#### Q3(e)(iii) [2]
SiO₂ is a white solid that melts above 1700 °C. SiCl₄ is a colourless liquid at room temperature. Explain the difference in the melting points of these two compounds with reference to their structure and bonding.

::: answer
- M1 SiO₂ is **giant covalent AND** SiCl₄ is **simple covalent** / simple molecular / molecular
- M2 so **less energy** is needed to overcome the **intermolecular forces** in SiCl₄ compared to the (covalent) **bonds** in SiO₂（or reverse argument）
:::

<!-- practice: 9701/22 Feb/Mar 2025 -->
### 9701/22 Feb/Mar 2025

The third compound of phosphorus and chlorine, **W**, has the molecular formula P₂Cl₄.

#### Q1(a)(iv) [2]
**W** is a liquid at room temperature and pressure. It reacts vigorously with water to form an acidic solution. Suggest the structure and bonding in **W**. Explain your answer.

::: answer
- (structure =) **simple / molecular**, because (it has a) low melting point / weak intermolecular forces
- (bonding =) **covalent**, because (it is) hydrolysed
:::

<!-- practice: 9701/21 May/June 2025 -->
### 9701/21 May/June 2025

Solid sodium conducts electricity. Sodium oxide conducts electricity when molten but not when solid.

#### Q1(a)(ii) [1]
Explain how solid sodium conducts electricity.

::: answer
delocalised electrons move (through the structure)
:::

#### Q1(a)(iii) [1]
Explain why sodium oxide conducts electricity when molten.

::: answer
(sodium and oxide) **ions** move (through the liquid)

写 "electrons move" 不给分——Na₂O 是 ionic，没有 delocalised electrons。solid 不导电是因为 ions 固定在 lattice 里。
:::

<!-- practice: 9701/22 May/June 2025 -->
### 9701/22 May/June 2025

Diamond and graphite are both crystalline solids made from carbon atoms. Graphite conducts electricity. Diamond does not conduct electricity.

#### Q1(a)(i) [1]
Name the type of lattice structure present in the crystalline solids diamond and graphite.

::: answer
(both) giant molecular
:::

#### Q1(a)(ii) [1]
Explain how graphite conducts electricity.

::: answer
delocalised electrons move through the structure **OR** delocalised electrons move through / between the layers
:::

#### Q1(a)(iii) [1]
Explain why diamond does not conduct electricity.

::: answer
no delocalised electrons (to carry charge through the structure) **OR** all (4) outer electrons are used in bonding
:::

#### Q1(d)(i) [3]
The melting points of different oxides are shown in Table 1.1. Complete Table 1.1 by identifying the strongest force of attraction in each oxide that is broken during melting. Use the abbreviations: i.d. = instantaneous dipole–induced dipole; p.d. = permanent dipole–permanent dipole; H = hydrogen bond; C = covalent bond; I = ionic bond.

| oxide | melting point / °C | force of attraction broken during melting |
|---|---|---|
| SO₂ | −73 | [[p.d.\|pd]] |
| H₂O | 0 | [[H]] |
| SiO₂ | 1610 | [[C]] |
| Na₂O | 1132 | [[I]] |
| MgO | 2852 | [[I]] |

::: answer
SO₂ = p.d.，H₂O = H，SiO₂ = C，Na₂O = I，MgO = I

SO₂ 是 polar 的 bent molecule，最强的 intermolecular force 是 p.d.（id-id 也有，但题目问 strongest）。H₂O 熔化时破坏的是 hydrogen bonds，不是 O–H covalent bonds。
:::

#### Q1(d)(ii) [2]
A student suggests the following hypothesis: "The stronger the covalent bond between atoms in non-metal oxides, the higher the melting point." Use Table 1.1 to deduce if this hypothesis is true or false or if there is not enough information to make a conclusion. Explain your answer.

::: answer
- M1 **not enough information**
- M2 SO₂ and / or H₂O break intermolecular forces **OR** SO₂ and / or H₂O does not break covalent bonds **OR** only SiO₂ breaks covalent bonds

（三个 non-metal oxide 里只有 SiO₂ 熔化时断 covalent bond，没法比较「covalent bond 强弱」对 melting point 的影响。）
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
- M2 *p* = 101 000 Pa，*R* = 8.31，*T* = 278 K，*n* = 0.00262（OR *p* = 101 kPa）
- M3 use of *pV* = *nRT*（*V* = *nRT* / *p*）
- M4 *V* = 5.99 × 10⁻⁵ m³ × 10⁶ = **59.9 cm³**（OR 5.99 × 10⁻² dm³ × 10³）
:::

<!-- practice: 9701/21 May/June 2026 -->
### 9701/21 May/June 2026

#### Q2(c)(ii) [4]
equation 1　2CaCO₃ + 2SO₂ + O₂ → 2CaSO₄ + 2CO₂

Use the ideal gas equation to calculate the volume of O₂(g) that reacts with 0.500 mol of SO₂ at 400 °C and 101 kPa in equation 1. Include units in your answer.

::: answer
- M1 *pV* = *nRT*
- M2 *n*(O₂) = 0.500 ÷ 2 = 0.250 mol
- M3 *T* = 400 + 273 = 673 K
- M4 *V* = 0.250 × 8.31 × 673 ÷ 101 000 = **0.0138 m³**（= 13.8 dm³ = 13 800 cm³）

判分：单位跟数值配套即可（0.014 m³ / 14 dm³ / 14 000 cm³ 都给满分）；273.15 也接受；M4 允许 ecf。
:::

<!-- practice: 9701/23 May/June 2026 -->
### 9701/23 May/June 2026

Group 18 elements exist as colourless gases at room temperature and pressure.

| atom | relative volume of atom |
|---|---|
| neon | 172 |
| argon | 287 |
| krypton | 355 |
| xenon | 446 |

#### Q2(a) [2]
Use Table 2.1 to describe and explain the variation in atomic radius down Group 18.

::: answer
- M1 (down the group) atomic radius increases **OR** atom volume increases **OR** Ne < Ar < Kr < Xe
- M2 (down the group) the number of shells (of electrons) increases

判分：shells = energy levels；只写 "sub-shells increase"、"shielding outweighs nuclear charge" 都不给 M2（这是 chapter 1 的内容）。
:::

#### Q2(b) [3]
Identify **one** Group 18 element from Table 2.1 that behaves most like an ideal gas under standard conditions. Explain your answer.

::: answer
- M1 **neon** / Ne
- M2 it has the **smallest** volume
- M3 **weakest** van der Waals' / instantaneous dipole – induced dipole attractions / London (dispersion) forces

判分：M2 和 M3 合起来要出现一次比较词（smaller / smallest、weaker / weakest / least），例如 "Ne has smaller volume and weak vdw"。用 mass 作 M2、只写 "smallest number of electrons" 都不给分。
:::

#### Q2(c) [4]
A sample of 1.775 g of gas X occupies 617.0 cm³ at 300 K and 101 kPa. Calculate the relative molecular mass, *M*ᵣ, of X assuming that X behaves as an ideal gas.

*M*ᵣ of X = [[71.0|71]]

::: answer
- M1 *pV* = *nRT*
- M2 use of appropriate pressure value with volume：617.0 cm³ = 617.0 × 10⁻⁶ m³ 配 101 000 Pa（OR 101 kPa 配 617.0 × 10⁻³ dm³）
- M3 *n* = 101 000 × 617.0 × 10⁻⁶ ÷ (8.31 × 300) = 0.024997 ≈ 0.0250 mol
- M4 *M*ᵣ = 1.775 ÷ 0.024997 = **71.0**

判分：最后答案 71(.0) 四分全给；M3、M4 允许 ecf（单位换错了但后面算对，仍给后面的分）。（X 是 Cl₂。）
:::

<!-- md -->
{{lo-checklist}}
